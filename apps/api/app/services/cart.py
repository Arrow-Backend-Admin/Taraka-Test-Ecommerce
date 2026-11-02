"""Guest cart with time-boxed inventory reservations.

Checkout and payment are deliberately out of scope. A cart reserves units for a
short window; removing a line or letting the cart expire releases them. The
existing conditional inventory update is the oversell guard, so two guests can
never reserve the same last unit.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..models import Cart, CartItem, Product, ProductVariant
from .inventory import InventoryNotFound, OutOfStock, release_stock, reserve_stock
from .publish import is_production

RESERVATION_MINUTES = 15
MAX_LINE_QUANTITY = 5
MAX_TOTAL_UNITS = 10
MAX_LINES = 5
RULES = {
    "reservation_minutes": RESERVATION_MINUTES,
    "max_line_quantity": MAX_LINE_QUANTITY,
    "max_total_units": MAX_TOTAL_UNITS,
    "max_lines": MAX_LINES,
    "checkout": "not available in this milestone",
}


class CartError(Exception):
    pass


class CartNotFound(CartError):
    pass


class CartRuleError(CartError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _new_reference(cart: Cart, variant_id: int) -> str:
    return f"cart:{cart.token}:{variant_id}:{uuid.uuid4().hex[:12]}"


def create_cart(db: Session) -> Cart:
    cart = Cart(
        token=secrets.token_urlsafe(24),
        status="active",
        expires_at=_now() + timedelta(minutes=RESERVATION_MINUTES),
        last_seen_at=_now(),
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_cart(db: Session, token: str) -> Cart | None:
    return db.scalar(
        select(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.variant).joinedload(ProductVariant.product))
        .where(Cart.token == token)
    )


def require_cart(db: Session, token: str | None) -> Cart:
    if not token:
        raise CartNotFound("Missing X-Cart-Token header")
    cart = get_cart(db, token)
    if cart is None:
        raise CartNotFound("Cart not found")
    expire_if_needed(db, cart)
    return cart


def expire_if_needed(db: Session, cart: Cart) -> bool:
    if cart.status != "active":
        return False
    expires = _aware(cart.expires_at)
    if expires is None or expires > _now():
        return False
    for item in list(cart.items):
        try:
            release_stock(
                db,
                item.variant_id,
                item.quantity,
                reference=f"{item.reservation_reference}:expired",
                note="Cart reservation expired; units released.",
            )
        except (InventoryNotFound, OutOfStock):
            pass
    cart.items.clear()
    cart.status = "expired"
    cart.expires_at = None
    db.commit()
    return True


def _touch(db: Session, cart: Cart) -> None:
    cart.expires_at = _now() + timedelta(minutes=RESERVATION_MINUTES)
    cart.last_seen_at = _now()
    for item in cart.items:
        item.reservation_expires_at = cart.expires_at
    db.commit()


def _variant_for_sku(db: Session, sku: str) -> ProductVariant:
    variant = db.scalar(
        select(ProductVariant)
        .options(joinedload(ProductVariant.product), joinedload(ProductVariant.inventory))
        .where(ProductVariant.sku == sku)
    )
    if variant is None:
        raise CartRuleError(f"Unknown SKU {sku}")
    if is_production() and variant.product.status != "published":
        raise CartRuleError("Product is not published")
    return variant


def _total_units(items: list[CartItem]) -> int:
    return sum(item.quantity for item in items)


def _replace_reservation(
    db: Session,
    cart: Cart,
    item: CartItem | None,
    variant: ProductVariant,
    quantity: int,
) -> str:
    """Release the old hold and reserve the new one.

    The caller deletes the line if the new hold cannot be made, so a cart never
    keeps a quantity without a matching reservation.
    """

    old_quantity = item.quantity if item is not None else 0
    old_reference = item.reservation_reference if item is not None else None
    if item is not None and old_reference:
        try:
            release_stock(
                db,
                variant.id,
                old_quantity,
                reference=f"{old_reference}:replace",
                note="Cart quantity changed; previous hold released.",
            )
        except (InventoryNotFound, OutOfStock):
            pass
    reference = _new_reference(cart, variant.id)
    reserve_stock(
        db,
        variant.id,
        quantity,
        reference=reference,
        note=f"Guest cart reservation for {RESERVATION_MINUTES} minutes.",
    )
    return reference


def add_item(db: Session, cart: Cart, sku: str, quantity: int) -> Cart:
    if cart.status != "active":
        raise CartRuleError("Cart is no longer active")
    if quantity < 1:
        raise CartRuleError("Quantity must be at least 1")
    variant = _variant_for_sku(db, sku)
    existing = next(
        (item for item in cart.items if item.variant_id == variant.id), None
    )
    new_quantity = (existing.quantity if existing else 0) + quantity
    if new_quantity > MAX_LINE_QUANTITY:
        raise CartRuleError(f"Maximum {MAX_LINE_QUANTITY} units per size")
    if existing is None and len(cart.items) >= MAX_LINES:
        raise CartRuleError(f"Maximum {MAX_LINES} lines per cart")
    total = _total_units([item for item in cart.items if item is not existing]) + new_quantity
    if total > MAX_TOTAL_UNITS:
        raise CartRuleError(f"Maximum {MAX_TOTAL_UNITS} units per cart")

    try:
        reference = _replace_reservation(db, cart, existing, variant, new_quantity)
    except OutOfStock:
        if existing is not None:
            cart.items.remove(existing)
            db.commit()
        raise
    if existing is None:
        existing = CartItem(
            cart_id=cart.id,
            variant_id=variant.id,
            quantity=new_quantity,
            unit_price=variant.price_inr,
            reservation_reference=reference,
            reservation_expires_at=cart.expires_at,
        )
        cart.items.append(existing)
    else:
        existing.quantity = new_quantity
        existing.unit_price = variant.price_inr
        existing.reservation_reference = reference
        existing.reservation_expires_at = cart.expires_at
    _touch(db, cart)
    return get_cart(db, cart.token) or cart


def update_item(db: Session, cart: Cart, item_id: int, quantity: int) -> Cart:
    if cart.status != "active":
        raise CartRuleError("Cart is no longer active")
    item = next((entry for entry in cart.items if entry.id == item_id), None)
    if item is None:
        raise CartNotFound("Cart line not found")
    if quantity == 0:
        remove_item(db, cart, item_id)
        return cart
    if quantity < 0:
        raise CartRuleError("Quantity cannot be negative")
    if quantity > MAX_LINE_QUANTITY:
        raise CartRuleError(f"Maximum {MAX_LINE_QUANTITY} units per size")
    others = _total_units([entry for entry in cart.items if entry.id != item.id])
    if others + quantity > MAX_TOTAL_UNITS:
        raise CartRuleError(f"Maximum {MAX_TOTAL_UNITS} units per cart")

    variant = item.variant
    try:
        reference = _replace_reservation(db, cart, item, variant, quantity)
    except OutOfStock:
        cart.items.remove(item)
        db.commit()
        raise
    item.quantity = quantity
    item.unit_price = variant.price_inr
    item.reservation_reference = reference
    item.reservation_expires_at = cart.expires_at
    _touch(db, cart)
    return get_cart(db, cart.token) or cart


def remove_item(db: Session, cart: Cart, item_id: int) -> Cart:
    item = next((entry for entry in cart.items if entry.id == item_id), None)
    if item is None:
        raise CartNotFound("Cart line not found")
    try:
        release_stock(
            db,
            item.variant_id,
            item.quantity,
            reference=f"{item.reservation_reference}:remove",
            note="Cart line removed; units released.",
        )
    except (InventoryNotFound, OutOfStock):
        pass
    cart.items.remove(item)
    db.commit()
    return get_cart(db, cart.token) or cart


def cart_payload(cart: Cart) -> dict[str, Any]:
    items = []
    subtotal = 0.0
    total_units = 0
    for item in sorted(cart.items, key=lambda entry: entry.id):
        variant = item.variant
        product = variant.product
        inventory = variant.inventory
        available = (
            max(inventory.on_hand - inventory.reserved, 0) if inventory else 0
        )
        line_total = float(item.unit_price) * item.quantity
        subtotal += line_total
        total_units += item.quantity
        items.append(
            {
                "id": item.id,
                "sku": variant.sku,
                "name": product.name,
                "slug": product.slug,
                "size_uk": variant.size_uk,
                "quantity": item.quantity,
                "unit_price": float(item.unit_price),
                "line_total": line_total,
                "available": available,
                "reservation_expires_at": _aware(item.reservation_expires_at),
            }
        )
    return {
        "token": cart.token,
        "status": cart.status,
        "expires_at": _aware(cart.expires_at),
        "items": items,
        "subtotal_inr": subtotal,
        "total_units": total_units,
        "reservation_minutes": RESERVATION_MINUTES,
        "rules": RULES,
    }


def stock_for_slug(db: Session, slug: str) -> dict[str, Any] | None:
    product = db.scalar(
        select(Product)
        .options(joinedload(Product.variants).joinedload(ProductVariant.inventory))
        .where(Product.slug == slug)
    )
    if product is None:
        return None
    sizes = []
    for variant in sorted(product.variants, key=lambda entry: entry.id):
        inventory = variant.inventory
        available = (
            max(inventory.on_hand - inventory.reserved, 0) if inventory else 0
        )
        sizes.append(
            {
                "sku": variant.sku,
                "size_uk": variant.size_uk,
                "available": available,
            }
        )
    return {"slug": product.slug, "sizes": sizes, "as_of": _now()}
