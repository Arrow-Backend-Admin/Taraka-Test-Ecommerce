"""Transactional email.

Mailpit catches messages on localhost:1025 in development. The confirmation is
plain text so it renders anywhere and never depends on remote assets.

A mail failure must not roll back a confirmed payment. The caller records the
failure and leaves ``confirmation_email_sent_at`` empty.
"""

from __future__ import annotations

import smtplib
from decimal import Decimal
from email.message import EmailMessage

from ..config import Settings
from ..models import Order
from .money import paise_to_rupees


def _group_indian(digits: str) -> str:
    if len(digits) <= 3:
        return digits
    head, tail = digits[:-3], digits[-3:]
    parts: list[str] = []
    while len(head) > 2:
        parts.insert(0, head[-2:])
        head = head[:-2]
    if head:
        parts.insert(0, head)
    return ",".join(parts + [tail])


def format_inr(paise: int) -> str:
    value = paise_to_rupees(paise)
    whole, fraction = f"{value:.2f}".split(".")
    return f"₹{_group_indian(whole)}.{fraction}"


def render_order_confirmation(order: Order) -> str:
    lines = [
        f"Hello {order.customer_name},",
        "",
        f"Payment received for order {order.public_id}.",
        "",
        "Items",
    ]
    for item in order.items:
        lines.append(
            f"- {item.product_name} / UK {item.size_uk} / {item.sku} "
            f"x{item.quantity}: {format_inr(item.line_total_paise)}"
        )
        lines.append(
            f"  Taxable {format_inr(item.taxable_value_paise)} + "
            f"GST {item.gst_rate_pct}% {format_inr(item.gst_paise)}"
        )
    lines.extend(
        [
            "",
            f"Subtotal (ex-GST): {format_inr(order.subtotal_paise)}",
            f"GST: {format_inr(order.gst_paise)}",
            f"Shipping: {format_inr(order.shipping_paise)} (not configured)",
            f"Total paid: {format_inr(order.total_paise)}",
            "",
            "Delivery address",
            order.customer_name,
            order.address_line1,
        ]
    )
    if order.address_line2:
        lines.append(order.address_line2)
    lines.extend(
        [
            f"{order.city}, {order.state} {order.pincode}",
            order.country,
            f"Phone: {order.customer_phone}",
            "",
            "This is a concept store. Shipping, returns and exchanges are not "
            "enabled in this milestone, so no dispatch date is promised.",
        ]
    )
    if "[TO CONFIRM" not in order.seller_gstin:
        lines.extend(
            [
                "",
                f"Seller state: {order.seller_state}",
                f"GSTIN: {order.seller_gstin}",
            ]
        )
    lines.extend(["", "Sāntvana"])
    return "\n".join(lines)


def send_email(
    *, to_email: str, subject: str, body: str, settings: Settings
) -> bool:
    if not settings.mail_enabled:
        return False
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = settings.mail_from
    message["To"] = to_email
    message.set_content(body)

    with smtplib.SMTP(
        settings.smtp_host,
        settings.smtp_port,
        timeout=settings.smtp_timeout_seconds,
    ) as smtp:
        if settings.smtp_starttls:
            smtp.starttls()
        if settings.smtp_username:
            smtp.login(settings.smtp_username, settings.smtp_password or "")
        smtp.send_message(message)
    return True


def send_order_confirmation(order: Order, settings: Settings) -> bool:
    return send_email(
        to_email=order.customer_email,
        subject=f"Order {order.public_id} confirmed — Sāntvana",
        body=render_order_confirmation(order),
        settings=settings,
    )


def money_decimal(paise: int) -> Decimal:
    """Convenience for callers that want a Decimal rupee value."""

    return paise_to_rupees(paise)
