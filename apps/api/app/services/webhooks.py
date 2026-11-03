"""Signed Razorpay webhook intake.

The raw request body is verified before it is parsed. The provider event id is
unique, so a replay is acknowledged without touching stock or payment state. A
previously failed event may be retried by the provider and is reprocessed.

Only this path may mark an order paid. The browser callback is a UI hint.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import WebhookEvent
from .orders import process_event
from .razorpay import RazorpayGateway


class WebhookSignatureError(Exception):
    pass


class WebhookPayloadError(Exception):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def process_webhook(
    db: Session,
    *,
    raw_body: bytes,
    signature: str,
    event_id_header: str | None,
    settings: Settings,
) -> dict[str, Any]:
    gateway = RazorpayGateway(settings)
    if not gateway.verify_webhook_signature(body=raw_body, signature=signature):
        raise WebhookSignatureError("Invalid Razorpay webhook signature")

    try:
        payload = json.loads(raw_body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WebhookPayloadError("Webhook body is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise WebhookPayloadError("Webhook body must be a JSON object")

    event_type = str(payload.get("event") or "unknown")
    event_id = (
        (event_id_header or "").strip()
        or str(payload.get("id") or "").strip()
        or hashlib.sha256(raw_body).hexdigest()
    )

    event = WebhookEvent(
        provider="razorpay",
        event_id=event_id,
        event_type=event_type,
        status="received",
        payload=payload,
    )
    db.add(event)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        existing = db.scalar(
            select(WebhookEvent).where(WebhookEvent.event_id == event_id)
        )
        if existing is None:
            raise
        if existing.status == "processed":
            return {"status": "duplicate", "event_id": event_id}
        if existing.status == "received":
            # Another worker is handling this delivery. Treat it as a replay.
            return {"status": "duplicate", "event_id": event_id}
        existing.status = "received"
        existing.error = None
        db.commit()
        event = existing

    try:
        outcome = process_event(db, event.event_type, payload, settings)
    except Exception as exc:  # noqa: BLE001 - provider retries failed events
        db.rollback()
        failed = db.scalar(select(WebhookEvent).where(WebhookEvent.event_id == event_id))
        if failed is not None:
            failed.status = "failed"
            failed.error = str(exc)[:2000]
            db.commit()
        raise

    event.status = "processed"
    event.processed_at = _now()
    event.error = None
    db.commit()
    return {"status": outcome, "event_id": event_id}
