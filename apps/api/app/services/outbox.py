"""Durable email outbox.

A confirmation row is written in the same transaction that marks the order
paid. If SMTP is down, the payment stays captured and the row stays pending for
the dispatcher. This is the difference between "email failed" and "payment
failed" — they must never be the same event.
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import EmailOutbox, Order
from .mail import render_order_confirmation, send_email


def _now() -> datetime:
    return datetime.now(timezone.utc)


def enqueue_confirmation(db: Session, order: Order) -> EmailOutbox:
    existing = db.scalar(
        select(EmailOutbox).where(EmailOutbox.order_id == order.id)
    )
    if existing is not None:
        return existing
    row = EmailOutbox(
        order_id=order.id,
        to_email=order.customer_email,
        subject=f"Order {order.public_id} confirmed — Sāntvana",
        body=render_order_confirmation(order),
        status="pending",
    )
    db.add(row)
    db.flush()
    return row


def dispatch_row(db: Session, row: EmailOutbox, settings: Settings) -> bool:
    if row.status == "sent":
        return True
    try:
        sent = send_email(
            to_email=row.to_email,
            subject=row.subject,
            body=row.body,
            settings=settings,
        )
    except Exception as exc:  # noqa: BLE001 - SMTP must never undo a payment
        row.attempts += 1
        row.last_error = str(exc)[:2000]
        if row.attempts >= settings.outbox_max_attempts:
            row.status = "failed"
        db.commit()
        return False

    if not sent:
        # MAIL_ENABLED=false: leave the row pending rather than pretending.
        return False

    row.status = "sent"
    row.sent_at = _now()
    row.last_error = None
    order = db.get(Order, row.order_id)
    if order is not None:
        order.confirmation_email_sent_at = row.sent_at
    db.commit()
    return True


def dispatch_pending(
    db: Session,
    settings: Settings,
    *,
    limit: int = 50,
    order_id: int | None = None,
) -> int:
    query = select(EmailOutbox).where(EmailOutbox.status == "pending")
    if order_id is not None:
        query = query.where(EmailOutbox.order_id == order_id)
    rows = db.scalars(query.order_by(EmailOutbox.id).limit(limit)).all()
    sent = 0
    for row in rows:
        if dispatch_row(db, row, settings):
            sent += 1
    return sent
