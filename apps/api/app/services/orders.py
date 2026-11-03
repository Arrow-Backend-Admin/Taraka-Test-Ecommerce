"""Order creation, reservation transfer and the payment state machine.

Rules enforced here, not in the browser:

* prices come from the database at checkout time and are copied onto order lines;
* all money is integer paise;
* GST is split out of each GST-inclusive line at that line's own rate;
* the cart's stock reservation is transferred to the order, then released on
  failure or expiry and converted to a sale only after a signed webhook;
* a late payment after expiry is re-reserved when possible, otherwise refunded.
"""

from __future__ import annotations

import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..config import Settings
from ..models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Payment,
    ProductVariant,
)
from .cart import CartRuleError, expire_if_needed
from .inventory import (
    InventoryNotFound,
    OutOfStock,
    commit_sale,
    release_stock,
    reserve_stock,
)
from .mail import send_order_confirmation
from .money import gst_rate_pct, rupees_to_paise, split_gst
from .razorpay import PaymentConfigurationError, RazorpayError, RazorpayGateway


class OrderError(Exception):
    pass


class OrderNotFound(OrderError):
    pass


class OrderStateError(OrderError):
    pass


class PaymentStartError(OrderError):
    def __init__(self, order: Order, message: str) -> None:
        self.order = order
        self.public_id = order.public_id
        super().__init__(message)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value if value.tzinfo is not None else value.replace(tzinfo=timezone.utc)


def new_public_id() -> str:
    return "ord_" + secrets.token_urlsafe(18)


def _clean_hsn(value: str | None) -> str | None:
    if not value or "[TO CONFIRM" in value:
        return None
    return value


def _checkout_snapshot(cart: Cart, settings: Settings) -> list[dict[str, Any]]:
    lines: list[dict[str, Any]] = []
    for item in cart.items:
        variant = item.variant
        product = variant.product
        if settings.is_production and product.status != "published":
            raise OrderStateError(f"{product.name} is not published")
        unit_price_paise = rupees_to_paise(variant.price_inr)
        quantity = item.quantity
        line_total_paise = unit_price_paise * quantity
        rate = gst_rate_pct(unit_price_paise, product.gst_rate)
        taxable_value_paise, gst_paise = split_gst(line_total_paise, rate)
        lines.append(
            {
                "variant_id": variant.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_slug": product.slug,
                "sku": variant.sku,
                "size_uk": variant.size_uk,
                "hsn": _clean_hsn(product.hsn),
                "quantity": quantity,
                "unit_price_paise": unit_price_paise,
                "line_total_paise": line_total_paise,
                "taxable_value_paise": taxable_value_paise,
                "gst_paise": gst_paise,
                "gst_rate_pct": rate,
                "reservation_reference": item.reservation_reference,
            }
        )
    return lines


def create_order(
    db: Session, cart: Cart, checkout: Any, settings: Settings
) -> tuple[Order, Payment]:
    if cart.status != "active":
        raise OrderStateError("Cart is no longer active")
    expire_if_needed(db, cart)
    if cart.status != "active":
        raise OrderStateError("Cart reservation expired. Add the items again.")
    if not cart.items:
        raise OrderStateError("Cart is empty")

    lines = _checkout_snapshot(cart, settings)
    subtotal_paise = sum(line["taxable_value_paise"] for line in lines)
    gst_paise = sum(line["gst_paise"] for line in lines)
    total_paise = sum(line["line_total_paise"] for line in lines)
    if subtotal_paise + gst_paise != total_paise:
        raise OrderStateError("GST split does not add up to the order total")

    address = checkout.address
    order = Order(
        public_id=new_public_id(),
        cart_id=cart.id,
        status="created",
        currency="INR",
        customer_name=checkout.customer_name,
        customer_email=checkout.customer_email,
        customer_phone=checkout.customer_phone,
        address_line1=address.line1,
        address_line2=address.line2,
        city=address.city,
        state=address.state,
        pincode=address.pincode,
        country=address.country,
        seller_state=settings.seller_state,
        seller_gstin=settings.seller_gstin,
        subtotal_paise=subtotal_paise,
        gst_paise=gst_paise,
        shipping_paise=0,
        total_paise=total_paise,
        reservation_expires_at=_now()
        + timedelta(minutes=settings.order_payment_window_minutes),
    )
    db.add(order)
    try:
        db.flush()
    except IntegrityError as exc:
        db.rollback()
        raise OrderStateError("This cart has already been converted to an order") from exc

    for line in lines:
        order.items.append(OrderItem(**line, stock_state="reserved"))

    # The stock hold moves from the cart to the order. Clearing the cart lines
    # must not release the reservation, so it is done directly rather than
    # through cart.remove_item().
    cart.items.clear()
    cart.status = "converted"
    cart.expires_at = None
    cart.last_seen_at = _now()
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise OrderStateError("This cart has already been converted to an order") from exc
    db.refresh(order)

    try:
        payment = create_payment_attempt(db, order, settings)
    except (PaymentConfigurationError, RazorpayError) as exc:
        release_order_stock(db, order, reason="payment-start-failed")
        order.status = "payment_failed"
        order.reservation_expires_at = None
        order.notes = f"Could not start payment: {exc}"
        db.commit()
        raise PaymentStartError(order, str(exc)) from exc
    return order, payment


def create_payment_attempt(
    db: Session, order: Order, settings: Settings
) -> Payment:
    if order.status == "paid":
        raise OrderStateError("Order is already paid")
    if order.status in {"refunded", "refund_pending"}:
        raise OrderStateError("Order is being refunded")

    if order.status in {"expired", "payment_failed"}:
        try:
            reserve_order_stock(db, order)
        except (OutOfStock, InventoryNotFound) as exc:
            raise OrderStateError(
                "The reserved stock was released and is no longer available. "
                "Start a new cart."
            ) from exc
    elif order.status not in {"created", "awaiting_payment"}:
        raise OrderStateError(f"Cannot start payment from status {order.status}")

    gateway = RazorpayGateway(settings)
    provider_order = gateway.create_order(
        amount_paise=order.total_paise,
        receipt=order.public_id,
        notes={"order_id": order.public_id},
    )
    provider_order_id = str(provider_order.get("id") or "").strip()
    if not provider_order_id:
        raise RazorpayError("Razorpay did not return an order id")

    payment = Payment(
        order_id=order.id,
        provider="razorpay",
        provider_order_id=provider_order_id,
        status="created",
        amount_paise=order.total_paise,
        currency=order.currency,
    )
    db.add(payment)
    order.status = "awaiting_payment"
    order.reservation_expires_at = _now() + timedelta(
        minutes=settings.order_payment_window_minutes
    )
    order.notes = None
    db.commit()
    db.refresh(payment)
    db.refresh(order)
    return payment


def checkout_options(order: Order, payment: Payment, settings: Settings) -> dict[str, Any]:
    return {
        "provider": "razorpay",
        "key_id": settings.razorpay_key_id,
        "order_id": payment.provider_order_id,
        "amount_paise": order.total_paise,
        "currency": order.currency,
        "name": "Sāntvana",
        "description": f"Order {order.public_id}",
        "mock": settings.razorpay_mock,
        "prefill": {
            "name": order.customer_name,
            "email": order.customer_email,
            "contact": order.customer_phone,
        },
    }


def order_payload(order: Order) -> dict[str, Any]:
    latest_payment = order.payments[-1] if order.payments else None
    if order.status == "paid":
        next_action = "none"
        message = "Payment confirmed."
    elif order.status == "awaiting_payment":
        next_action = "pay"
        message = "Waiting for the signed Razorpay webhook."
    elif order.status == "payment_failed":
        next_action = "retry"
        message = "The payment did not complete. The reservation was released."
    elif order.status == "expired":
        next_action = "retry"
        message = "The payment window closed. Retry while stock is still available."
    elif order.status in {"refund_pending", "refunded"}:
        next_action = "none"
        message = "This order was paid after the reservation expired and is being refunded."
    else:
        next_action = "retry"
        message = "Payment has not started."

    return {
        "public_id": order.public_id,
        "status": order.status,
        "currency": order.currency,
        "created_at": order.created_at,
        "paid_at": order.paid_at,
        "expired_at": order.expired_at,
        "reservation_expires_at": order.reservation_expires_at,
        "customer_name": order.customer_name,
        "customer_email": order.customer_email,
        "customer_phone": order.customer_phone,
        "address": {
            "line1": order.address_line1,
            "line2": order.address_line2,
            "city": order.city,
            "state": order.state,
            "pincode": order.pincode,
            "country": order.country,
        },
        "seller": {"state": order.seller_state, "gstin": order.seller_gstin},
        "items": [
            {
                "product_name": item.product_name,
                "product_slug": item.product_slug,
                "sku": item.sku,
                "size_uk": item.size_uk,
                "quantity": item.quantity,
                "unit_price_paise": item.unit_price_paise,
                "line_total_paise": item.line_total_paise,
                "taxable_value_paise": item.taxable_value_paise,
                "gst_paise": item.gst_paise,
                "gst_rate_pct": item.gst_rate_pct,
            }
            for item in order.items
        ],
        "subtotal_paise": order.subtotal_paise,
        "gst_paise": order.gst_paise,
        "shipping_paise": order.shipping_paise,
        "total_paise": order.total_paise,
        "latest_payment": (
            {
                "provider_order_id": latest_payment.provider_order_id,
                "status": latest_payment.status,
                "amount_paise": latest_payment.amount_paise,
                "method": latest_payment.method,
            }
            if latest_payment is not None
            else None
        ),
        "next_action": next_action,
        "message": message,
    }


def get_order(db: Session, public_id: str) -> Order:
    order = db.scalar(
        select(Order)
        .options(joinedload(Order.items), joinedload(Order.payments))
        .where(Order.public_id == public_id)
    )
    if order is None:
        raise OrderNotFound("Order not found")
    return order


def expire_order(db: Session, order: Order, *, now: datetime | None = None) -> bool:
    if order.status not in {"created", "awaiting_payment"}:
        return False
    moment = now or _now()
    expires = _aware(order.reservation_expires_at)
    if expires is not None and expires > moment:
        return False
    release_order_stock(db, order, reason="expired")
    order.status = "expired"
    order.expired_at = moment
    order.reservation_expires_at = None
    db.commit()
    return True


def expire_orders(db: Session, *, now: datetime | None = None) -> int:
    moment = now or _now()
    orders = db.scalars(
        select(Order)
        .options(joinedload(Order.items))
        .where(
            Order.status.in_(("created", "awaiting_payment")),
            Order.reservation_expires_at.is_not(None),
            Order.reservation_expires_at <= moment,
        )
    ).unique().all()
    expired = 0
    for order in orders:
        if expire_order(db, order, now=moment):
            expired += 1
    return expired


def reserve_order_stock(db: Session, order: Order) -> None:
    """Re-reserve every line whose stock was released.

    Used when a payment arrives after the order expired, or when a failed
    payment is retried. If any line cannot be reserved, the lines reserved in
    this call are released again.
    """

    reserved_here: list[OrderItem] = []
    for item in order.items:
        if item.stock_state == "sold":
            continue
        if item.stock_state == "reserved":
            continue
        reference = f"order:{order.id}:{item.variant_id}:{uuid.uuid4().hex[:12]}"
        try:
            reserve_stock(
                db,
                item.variant_id,
                item.quantity,
                reference=reference,
                note=f"Order {order.public_id} retry reservation.",
            )
        except (OutOfStock, InventoryNotFound):
            for previous in reserved_here:
                try:
                    release_stock(
                        db,
                        previous.variant_id,
                        previous.quantity,
                        reference=f"{previous.reservation_reference}:compensate",
                        note="Compensating release after a failed re-reservation.",
                    )
                except (OutOfStock, InventoryNotFound):
                    pass
                previous.stock_state = "released"
            db.commit()
            raise
        item.reservation_reference = reference
        item.stock_state = "reserved"
        reserved_here.append(item)
    db.commit()


def release_order_stock(db: Session, order: Order, *, reason: str) -> None:
    for item in order.items:
        if item.stock_state != "reserved":
            continue
        try:
            release_stock(
                db,
                item.variant_id,
                item.quantity,
                reference=f"{item.reservation_reference}:{reason}",
                note=f"Order {order.public_id}: reservation released ({reason}).",
            )
        except (OutOfStock, InventoryNotFound):
            pass
        item.stock_state = "released"
    db.commit()


def commit_order_sale(db: Session, order: Order) -> None:
    for item in order.items:
        if item.stock_state == "sold":
            continue
        if item.stock_state != "reserved":
            raise OrderStateError(
                f"Order line {item.sku} has no active reservation to sell"
            )
        commit_sale(
            db,
            item.variant_id,
            item.quantity,
            reference=f"{item.reservation_reference}:sale",
            note=f"Order {order.public_id}: payment confirmed.",
        )
        item.stock_state = "sold"
    db.commit()


def refund_payment(
    db: Session,
    order: Order,
    payment: Payment,
    *,
    reason: str,
    settings: Settings,
) -> str:
    if payment.status == "refunded" and payment.refund_id:
        order.status = "refunded"
        db.commit()
        return "refunded"

    payment_id = payment.provider_payment_id
    if not payment_id:
        order.status = "refund_pending"
        order.notes = f"Refund needed but no payment id was captured: {reason}"
        db.commit()
        return "refund_pending"

    gateway = RazorpayGateway(settings)
    try:
        result = gateway.refund(
            payment_id=payment_id,
            amount_paise=payment.amount_paise,
            notes={"order_id": order.public_id, "reason": reason[:100]},
        )
    except (PaymentConfigurationError, RazorpayError) as exc:
        order.status = "refund_pending"
        order.notes = f"Refund failed: {exc}"
        db.commit()
        return "refund_pending"

    payment.refund_id = str(result.get("id") or "")
    payment.refunded_paise = payment.amount_paise
    payment.status = "refunded"
    order.status = "refunded"
    order.notes = f"Refunded: {reason}"
    db.commit()
    return "refunded"


def _send_confirmation(db: Session, order: Order, settings: Settings) -> None:
    try:
        sent = send_order_confirmation(order, settings)
    except Exception as exc:  # noqa: BLE001 - email must not undo a payment
        order.notes = f"Confirmation email failed: {exc}"
        db.commit()
        return
    if sent:
        order.confirmation_email_sent_at = _now()
        db.commit()


def mark_paid(
    db: Session,
    order: Order,
    payment: Payment,
    *,
    provider_payment_id: str,
    amount_paise: int,
    method: str | None,
    raw_status: str | None,
    settings: Settings,
) -> str:
    if order.status == "paid":
        if payment.status != "captured":
            payment.status = "captured"
            payment.provider_payment_id = provider_payment_id
            db.commit()
        return "already_paid"

    if amount_paise != order.total_paise:
        payment.provider_payment_id = provider_payment_id
        payment.raw_status = raw_status
        payment.failure_code = "amount_mismatch"
        payment.failure_reason = (
            f"Webhook amount {amount_paise} does not match order total "
            f"{order.total_paise}"
        )
        db.commit()
        return refund_payment(
            db, order, payment, reason="payment amount mismatch", settings=settings
        )

    if order.status in {"expired", "cancelled", "payment_failed"}:
        try:
            reserve_order_stock(db, order)
        except (OutOfStock, InventoryNotFound):
            payment.provider_payment_id = provider_payment_id
            payment.raw_status = raw_status
            payment.method = method
            db.commit()
            return refund_payment(
                db,
                order,
                payment,
                reason="paid after the reservation expired and stock is gone",
                settings=settings,
            )

    if order.status not in {"created", "awaiting_payment", "expired", "payment_failed"}:
        return refund_payment(
            db, order, payment, reason=f"unexpected order status {order.status}", settings=settings
        )

    commit_order_sale(db, order)
    payment.status = "captured"
    payment.provider_payment_id = provider_payment_id
    payment.method = method
    payment.raw_status = raw_status
    payment.failure_code = None
    payment.failure_reason = None
    order.status = "paid"
    order.paid_at = _now()
    order.reservation_expires_at = None
    order.notes = None
    db.commit()
    db.refresh(order)
    _send_confirmation(db, order, settings)
    return "paid"


def mark_payment_failed(
    db: Session,
    order: Order,
    payment: Payment,
    *,
    provider_payment_id: str | None,
    failure_code: str | None,
    failure_reason: str | None,
    raw_status: str | None,
) -> str:
    if payment.status == "captured":
        return "ignored"
    payment.status = "failed"
    if provider_payment_id:
        payment.provider_payment_id = provider_payment_id
    payment.failure_code = failure_code
    payment.failure_reason = failure_reason
    payment.raw_status = raw_status
    if order.status in {"created", "awaiting_payment"}:
        release_order_stock(db, order, reason="failed")
        order.status = "payment_failed"
        order.reservation_expires_at = None
    db.commit()
    return "payment_failed"


def _payment_entity(payload: dict[str, Any]) -> dict[str, Any]:
    return (payload.get("payload") or {}).get("payment", {}).get("entity") or {}


def _locked_payment(
    db: Session, provider_order_id: str
) -> tuple[Payment | None, Order | None]:
    """Load a payment and its order under a row lock.

    Two deliveries of the same capture (or a capture and a failure) must not
    both act on the same order. PostgreSQL serialises them on these rows; the
    second caller then sees the already-updated status. SQLite ignores the
    clause and serialises writers at the database level instead.
    """

    payment = db.scalar(
        select(Payment)
        .where(Payment.provider_order_id == provider_order_id)
        .with_for_update()
    )
    if payment is None:
        return None, None
    order = db.get(Order, payment.order_id, with_for_update=True)
    return payment, order


def handle_payment_captured(
    db: Session, payload: dict[str, Any], settings: Settings
) -> str:
    entity = _payment_entity(payload)
    provider_order_id = str(entity.get("order_id") or "").strip()
    provider_payment_id = str(entity.get("id") or "").strip()
    if not provider_order_id or not provider_payment_id:
        return "ignored"
    payment, order = _locked_payment(db, provider_order_id)
    if payment is None or order is None:
        return "ignored"
    return mark_paid(
        db,
        order,
        payment,
        provider_payment_id=provider_payment_id,
        amount_paise=int(entity.get("amount") or 0),
        method=entity.get("method"),
        raw_status=entity.get("status"),
        settings=settings,
    )


def handle_order_paid(db: Session, payload: dict[str, Any], settings: Settings) -> str:
    entity = _payment_entity(payload)
    provider_order_id = str(entity.get("order_id") or "").strip()
    if not provider_order_id:
        order_entity = (payload.get("payload") or {}).get("order", {}).get("entity") or {}
        provider_order_id = str(order_entity.get("id") or "").strip()
    provider_payment_id = str(entity.get("id") or "").strip()
    if not provider_order_id or not provider_payment_id:
        return "ignored"
    payment, order = _locked_payment(db, provider_order_id)
    if payment is None or order is None:
        return "ignored"
    return mark_paid(
        db,
        order,
        payment,
        provider_payment_id=provider_payment_id,
        amount_paise=int(entity.get("amount") or 0),
        method=entity.get("method"),
        raw_status=entity.get("status"),
        settings=settings,
    )


def handle_payment_failed(
    db: Session, payload: dict[str, Any], settings: Settings
) -> str:
    entity = _payment_entity(payload)
    provider_order_id = str(entity.get("order_id") or "").strip()
    if not provider_order_id:
        return "ignored"
    payment, order = _locked_payment(db, provider_order_id)
    if payment is None or order is None:
        return "ignored"
    error = entity.get("error") or {}
    return mark_payment_failed(
        db,
        order,
        payment,
        provider_payment_id=str(entity.get("id") or "").strip() or None,
        failure_code=error.get("code") or entity.get("error_code"),
        failure_reason=error.get("description") or entity.get("error_description"),
        raw_status=entity.get("status"),
    )


def handle_refund_processed(
    db: Session, payload: dict[str, Any], settings: Settings
) -> str:
    entity = (payload.get("payload") or {}).get("refund", {}).get("entity") or {}
    provider_payment_id = str(entity.get("payment_id") or "").strip()
    if not provider_payment_id:
        return "ignored"
    payment = db.scalar(
        select(Payment)
        .where(Payment.provider_payment_id == provider_payment_id)
        .with_for_update()
    )
    if payment is None:
        return "ignored"
    order = db.get(Order, payment.order_id, with_for_update=True)
    if order is None:
        return "ignored"
    payment.refund_id = str(entity.get("id") or payment.refund_id or "")
    payment.refunded_paise = int(entity.get("amount") or payment.refunded_paise or 0)
    payment.status = "refunded"
    order.status = "refunded"
    db.commit()
    return "refunded"


def process_event(db: Session, event_type: str, payload: dict[str, Any], settings: Settings) -> str:
    if event_type == "payment.captured":
        return handle_payment_captured(db, payload, settings)
    if event_type == "order.paid":
        return handle_order_paid(db, payload, settings)
    if event_type == "payment.failed":
        return handle_payment_failed(db, payload, settings)
    if event_type == "refund.processed":
        return handle_refund_processed(db, payload, settings)
    return "ignored"


def verify_payment_hint(
    db: Session,
    order: Order,
    *,
    provider_order_id: str,
    provider_payment_id: str,
    signature: str,
    settings: Settings,
) -> dict[str, Any]:
    """Browser callback hint.

    A valid signature proves Razorpay produced this callback, but it does not
    confirm the payment. Only the signed webhook may move an order to ``paid``.
    """

    gateway = RazorpayGateway(settings)
    verified = gateway.verify_payment_signature(
        order_id=provider_order_id,
        payment_id=provider_payment_id,
        signature=signature,
    )
    if not verified:
        return {
            "verified": False,
            "order_status": order.status,
            "message": "Payment signature did not verify.",
        }
    return {
        "verified": True,
        "order_status": order.status,
        "message": (
            "Signature verified. Waiting for the signed webhook before the order "
            "is marked paid."
            if order.status != "paid"
            else "Payment confirmed by webhook."
        ),
    }
