"""Guest cart with time-boxed inventory reservations.

Checkout and payment are deliberately out of scope. A cart reserves units for a
short window; removing a line or letting the cart expire releases them. The
existing conditional inventory update is the oversell guard, so two guests can
never reserve the same last unit.
"""

from __future__ import annotations

import hashlib
import math
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

# Anti-hoarding caps. A single IP cannot hold more than 20% of a size's
# on-hand units (with a floor of two so small runs stay buyable) or more than
# ten units in total across all of its active carts.
MAX_UNITS_PER_IP = 10
SIZE_RESERVATION_RATIO = 0.20
MIN_SIZE_RESERVATION_CAP = 2

CART_COOKIE_NAME = "santvana_cart"
CART_COOKIE_MAX_AGE = 60 * 60 * 24 * 7
CART_COOKIE_PATH = "/"

RULES = {
    "reservation_minutes": RESERVATION_MINUTES,
    "max_line_quantity": MAX_LINE_QUANTITY,
    "max_total_units": MAX_TOTAL_UNITS,
    "max_lines": MAX_LINES,
    "max_units_per_ip": MAX_UNITS_PER_IP,
    "size_reservation_ratio": SIZE_RESERVATION_RATIO,
    "min_size_reservation_cap": MIN_SIZE_RESERVATION_CAP,
    "checkout": "available after Milestone 3",
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
    return f"cart:{cart.id}:{variant_id}:{uuid.uuid4().hex[:12]}"


def hash_cart_token(raw_token: str) -> str:
    """Hash a guest cart token before it is stored.

    The raw token only ever lives in the httpOnly cookie. A database leak does
    not hand an attacker usable cart tokens.
    """

    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


def hash_client_ip(ip: str | None, secret: str | None = None) -> str | None:
    """Store an IP as a salted hash so reservation caps can be enforced."""

    if not ip:
        return None
    material = f"{secret or ''}:{ip}".encode("utf-8")
    return hashlib.sha256(material).hexdigest()


def size_reservation_cap(on_hand: int) -> int:
    """Per-IP cap for one size: 20% of on-hand, with a floor of two units."""

    if on_hand <= 0:
        return 0
    return max(MIN_SIZE_RESERVATION_CAP, math.ceil(on_hand * SIZE_RESERVATION_RATIO))


def create_cart(db: Session, ip_hash: str | None = None) -> tuple[Cart, str]:
    raw_token = secrets.token_urlsafe(32)
    cart = Cart(
        token_hash=hash_cart_token(raw_token),
        ip_hash=ip_hash,
        status="active",
        expires_at=_now() + timedelta(minutes=RESERVATION_MINUTES),
        last_seen_at=_now(),
    )
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart, raw_token


def get_cart(db: Session, raw_token: str | None) -> Cart | None:
    if not raw_token:
        return None
    return db.scalar(
        select(Cart)
        .options(joinedload(Cart.items).joinedload(CartItem.variant).joinedload(ProductVariant.product))
        .where(Cart.token_hash == hash_cart_token(raw_token))
    )


def require_cart(db: Session, raw_token: str | None) -> Cart:
    if not raw_token:
        raise CartNotFound("Missing cart cookie")
    cart = get_cart(db, raw_token)
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


def _ip_usage(
    db: Session, ip_hash: str, *, exclude_item_id: int | None = None
) -> tuple[int, dict[int, int]]:
    """Units held by this IP in other active, unexpired carts."""

    statement = (
        select(CartItem.variant_id, CartItem.quantity)
        .join(Cart, CartItem.cart_id == Cart.id)
        .where(
            Cart.ip_hash == ip_hash,
            Cart.status == "active",
            Cart.expires_at > _now(),
        )
    )
    if exclude_item_id is not None:
        statement = statement.where(CartItem.id != exclude_item_id)
    total = 0
    per_variant: dict[int, int] = {}
    for variant_id, quantity in db.execute(statement):
        total += quantity
        per_variant[variant_id] = per_variant.get(variant_id, 0) + quantity
    return total, per_variant


def _check_reservation_caps(
    db: Session,
    cart: Cart,
    variant: ProductVariant,
    new_quantity: int,
    existing: CartItem | None,
) -> None:
    if not cart.ip_hash:
        return
    exclude_id = existing.id if existing is not None else None
    ip_total, per_variant = _ip_usage(db, cart.ip_hash, exclude_item_id=exclude_id)
    if ip_total + new_quantity > MAX_UNITS_PER_IP:
        raise CartRuleError(
            f"Maximum {MAX_UNITS_PER_IP} reserved units per IP. "
            "Remove a line or wait for a reservation to expire."
        )
    inventory = variant.inventory
    on_hand = inventory.on_hand if inventory is not None else 0
    cap = size_reservation_cap(on_hand)
    held = per_variant.get(variant.id, 0)
    if held + new_quantity > cap:
        raise CartRuleError(
            f"Maximum {cap} reserved units for this size per IP. "
            "Remove a line or wait for a reservation to expire."
        )


def _reload(db: Session, cart: Cart) -> Cart:
    return (
        db.scalar(
            select(Cart)
            .options(
                joinedload(Cart.items)
                .joinedload(CartItem.variant)
                .joinedload(ProductVariant.product)
            )
            .where(Cart.id == cart.id)
        )
        or cart
    )


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
    _check_reservation_caps(db, cart, variant, new_quantity, existing)

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
    return _reload(db, cart)


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
    _check_reservation_caps(db, cart, item.variant, quantity, item)

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
    return _reload(db, cart)


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
    return _reload(db, cart)


def cart_payload(db: Session, cart: Cart) -> dict[str, Any]:
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
        on_hand = inventory.on_hand if inventory else 0
        cap = size_reservation_cap(on_hand)
        max_by_size = cap
        max_by_ip = MAX_UNITS_PER_IP
        if cart.ip_hash:
            ip_total, per_variant = _ip_usage(
                db, cart.ip_hash, exclude_item_id=item.id
            )
            max_by_size = cap - per_variant.get(variant.id, 0)
            max_by_ip = MAX_UNITS_PER_IP - ip_total
        max_reservable = max(
            min(
                MAX_LINE_QUANTITY,
                available + item.quantity,
                max_by_size,
                max_by_ip,
            ),
            0,
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
                "max_reservable": max_reservable,
                "reservation_expires_at": _aware(item.reservation_expires_at),
            }
        )
    return {
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
        on_hand = inventory.on_hand if inventory else 0
        sizes.append(
            {
                "sku": variant.sku,
                "size_uk": variant.size_uk,
                "available": available,
                "max_reservable": size_reservation_cap(on_hand),
            }
        )
    return {"slug": product.slug, "sizes": sizes, "as_of": _now()}
