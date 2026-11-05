"""Signed Razorpay webhook intake.

The raw request body is verified before it is parsed. The provider event id is
unique, so a replay is acknowledged without touching stock or payment state. A
previously failed event may be retried by the provider and is reprocessed.

Only this path may mark an order paid. The browser callback is a UI hint.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import WebhookEvent
from .orders import process_event
from .razorpay import RazorpayGateway
from .resilience import run_with_db_retry


class WebhookSignatureError(Exception):
    pass


class WebhookPayloadError(Exception):
    pass


# A worker that dies after storing the event but before finishing leaves the row
# at ``received``. The provider retry must be allowed to finish the job, so a
# ``received`` row older than this lease is reclaimed instead of being called a
# duplicate. The window is long enough that a live worker is never raced.
RECEIVED_LEASE = timedelta(minutes=5)


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _is_stale_received(event: WebhookEvent) -> bool:
    created_at = event.created_at
    if created_at is None:
        return True
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    return _now() - created_at > RECEIVED_LEASE


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
        if existing.status == "received" and not _is_stale_received(existing):
            # Another worker is handling this delivery. Treat it as a replay.
            return {"status": "duplicate", "event_id": event_id}
        # ``failed``, or a ``received`` row whose worker died: reclaim and retry.
        existing.status = "received"
        existing.error = None
        db.commit()
        event = existing

    try:
        # The event row is already committed, so the provider gets a 2xx only
        # after the delivery is durably stored. Retrying here covers transient
        # PostgreSQL serialization failures, not a logical failure.
        outcome = run_with_db_retry(
            db, lambda: process_event(db, event.event_type, payload, settings)
        )
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
