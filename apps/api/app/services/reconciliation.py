"""Nightly reconciliation across orders, payments and inventory.

The checks are read-only. They do not repair data; they report mismatches so a
human can decide. A non-empty report means the caller should exit non-zero.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from ..models import Inventory, InventoryEvent, Order, Payment

PAID_OR_AFTER = {"paid", "refund_pending", "refunded"}


def reconcile(db: Session) -> list[str]:
    problems: list[str] = []
    problems.extend(_order_totals(db))
    problems.extend(_order_payment_state(db))
    problems.extend(_inventory_state(db))
    problems.extend(_order_stock_events(db))
    return problems


def _order_totals(db: Session) -> list[str]:
    problems: list[str] = []
    orders = (
        db.scalars(
            select(Order).options(joinedload(Order.items)).order_by(Order.id)
        )
        .unique()
        .all()
    )
    for order in orders:
        lines_total = sum(item.line_total_paise for item in order.items)
        taxable_total = sum(item.taxable_value_paise for item in order.items)
        gst_total = sum(item.gst_paise for item in order.items)
        if order.total_paise != lines_total + order.shipping_paise:
            problems.append(
                f"order {order.public_id}: total_paise {order.total_paise} != "
                f"lines {lines_total} + shipping {order.shipping_paise}"
            )
        if order.subtotal_paise != taxable_total:
            problems.append(
                f"order {order.public_id}: subtotal_paise {order.subtotal_paise} "
                f"!= sum of taxable values {taxable_total}"
            )
        if order.gst_paise != gst_total:
            problems.append(
                f"order {order.public_id}: gst_paise {order.gst_paise} != "
                f"sum of line GST {gst_total}"
            )
        for item in order.items:
            if item.line_total_paise != item.unit_price_paise * item.quantity:
                problems.append(
                    f"order {order.public_id} line {item.sku}: line total "
                    f"{item.line_total_paise} != unit {item.unit_price_paise} "
                    f"× {item.quantity}"
                )
            if item.taxable_value_paise + item.gst_paise != item.line_total_paise:
                problems.append(
                    f"order {order.public_id} line {item.sku}: taxable + GST "
                    f"does not equal line total"
                )
            if item.gst_rate_pct not in (5, 18):
                problems.append(
                    f"order {order.public_id} line {item.sku}: unknown GST rate "
                    f"{item.gst_rate_pct}"
                )
    return problems


def _order_payment_state(db: Session) -> list[str]:
    problems: list[str] = []
    orders = (
        db.scalars(
            select(Order)
            .options(joinedload(Order.items), joinedload(Order.payments))
            .order_by(Order.id)
        )
        .unique()
        .all()
    )
    for order in orders:
        captured = [p for p in order.payments if p.status == "captured"]
        if order.status == "paid":
            if not captured:
                problems.append(
                    f"order {order.public_id}: status paid but no captured payment"
                )
            if order.paid_at is None:
                problems.append(
                    f"order {order.public_id}: status paid but paid_at is empty"
                )
            for item in order.items:
                if item.stock_state != "sold":
                    problems.append(
                        f"order {order.public_id} line {item.sku}: paid order "
                        f"line is {item.stock_state}, expected sold"
                    )
        for payment in captured:
            if order.status not in PAID_OR_AFTER:
                problems.append(
                    f"order {order.public_id}: captured payment "
                    f"{payment.provider_payment_id} but order status is "
                    f"{order.status}"
                )
            if payment.amount_paise != order.total_paise:
                problems.append(
                    f"order {order.public_id}: captured amount "
                    f"{payment.amount_paise} != order total {order.total_paise}"
                )
        for payment in order.payments:
            if payment.refunded_paise > payment.amount_paise:
                problems.append(
                    f"order {order.public_id}: refunded {payment.refunded_paise} "
                    f"exceeds paid {payment.amount_paise}"
                )
            if (
                payment.needs_review
                and payment.refunded_paise < payment.amount_paise
            ):
                problems.append(
                    f"order {order.public_id}: payment flagged for review "
                    f"({payment.review_reason or 'no reason'}) and only "
                    f"{payment.refunded_paise} of {payment.amount_paise} refunded"
                )
    return problems


def _inventory_state(db: Session) -> list[str]:
    problems: list[str] = []
    rows = db.scalars(select(Inventory).order_by(Inventory.variant_id)).all()
    for row in rows:
        if row.on_hand < 0:
            problems.append(
                f"inventory variant {row.variant_id}: on_hand {row.on_hand} is negative"
            )
        if row.reserved < 0:
            problems.append(
                f"inventory variant {row.variant_id}: reserved {row.reserved} is negative"
            )
        if row.reserved > row.on_hand:
            problems.append(
                f"inventory variant {row.variant_id}: reserved {row.reserved} "
                f"exceeds on_hand {row.on_hand}"
            )
    return problems


def _order_stock_events(db: Session) -> list[str]:
    problems: list[str] = []
    events = db.scalars(select(InventoryEvent)).all()
    references = {event.reference for event in events if event.reference}

    expected_reserved: dict[int, int] = defaultdict(int)
    for event in events:
        if event.event_type in {"reservation", "release"}:
            expected_reserved[event.variant_id] -= event.quantity_delta
        elif event.event_type == "sale":
            expected_reserved[event.variant_id] += event.quantity_delta

    for variant_id, expected in expected_reserved.items():
        row = db.scalar(select(Inventory).where(Inventory.variant_id == variant_id))
        if row is None:
            problems.append(
                f"inventory events reference variant {variant_id} with no inventory row"
            )
            continue
        if row.reserved != expected:
            problems.append(
                f"inventory variant {variant_id}: reserved {row.reserved} != "
                f"event-derived reserved {expected}"
            )

    orders = (
        db.scalars(
            select(Order).options(joinedload(Order.items)).order_by(Order.id)
        )
        .unique()
        .all()
    )
    for order in orders:
        for item in order.items:
            if item.stock_state == "sold":
                sale_reference = f"{item.reservation_reference}:sale"
                if sale_reference not in references:
                    problems.append(
                        f"order {order.public_id} line {item.sku}: sold line has "
                        f"no sale inventory event ({sale_reference})"
                    )
            if item.stock_state == "reserved" and item.reservation_reference not in references:
                problems.append(
                    f"order {order.public_id} line {item.sku}: reserved line has "
                    f"no reservation inventory event"
                )
    return problems


def summary(problems: list[str]) -> dict[str, Any]:
    return {"ok": not problems, "mismatch_count": len(problems), "problems": problems}
