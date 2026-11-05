from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import WebhookEvent
from app.services.webhooks import RECEIVED_LEASE

from .test_orders import (
    _captured_body,
    _expire_order,
    _failed_body,
    _inventory,
    _order,
    _order_with_one_pair,
    _payment,
    _post_webhook,
)


def _entity(body: dict) -> dict:
    return body["payload"]["payment"]["entity"]


def test_partial_capture_without_amount_is_ignored(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(provider_order_id, "pay_partial_amount", body["total_paise"])
    _entity(payload).pop("amount")

    response = _post_webhook(client, payload, event_id="evt_partial_amount")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ignored"

    order = _order(db_session, body["public_id"])
    assert order.status == "awaiting_payment"
    assert _inventory(db_session, "RELAY-UK7").reserved == 1


def test_partial_capture_without_currency_is_ignored(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(provider_order_id, "pay_partial_currency", body["total_paise"])
    _entity(payload).pop("currency")

    response = _post_webhook(client, payload, event_id="evt_partial_currency")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ignored"
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"


def test_currency_mismatch_is_flagged_for_review_and_never_confirmed(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(provider_order_id, "pay_wrong_currency", body["total_paise"])
    _entity(payload)["currency"] = "USD"

    response = _post_webhook(client, payload, event_id="evt_wrong_currency")
    assert response.status_code == 200, response.text
    assert response.json()["status"] == "refund_pending"

    order = _order(db_session, body["public_id"])
    payment = _payment(db_session, provider_order_id)
    assert order.status == "refund_pending"
    assert payment.needs_review is True
    assert "currency mismatch" in (payment.review_reason or "")
    assert payment.failure_code == "currency_mismatch"
    # The amount is recorded exactly as captured for the manual refund.
    assert payment.amount_paise == body["total_paise"]
    # The reservation was not sold.
    assert _inventory(db_session, "RELAY-UK7").on_hand == 10


def test_amount_mismatch_is_flagged_for_review(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(
        provider_order_id, "pay_wrong_amount_review", body["total_paise"] + 1
    )

    response = _post_webhook(client, payload, event_id="evt_wrong_amount_review")
    assert response.status_code == 200, response.text
    payment = _payment(db_session, provider_order_id)
    assert payment.needs_review is True
    assert "amount mismatch" in (payment.review_reason or "")
    assert _order(db_session, body["public_id"]).status != "paid"


def test_capture_then_failure_is_ignored_so_paid_stays_paid(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_ordered_1", body["total_paise"]),
        event_id="evt_ordered_capture",
    )
    assert captured.json()["status"] == "paid"

    # A late failure delivery for the same payment must not undo the capture.
    late_failure = _post_webhook(
        client,
        _failed_body(provider_order_id, "pay_ordered_1"),
        event_id="evt_ordered_failure",
    )
    assert late_failure.status_code == 200, late_failure.text
    assert late_failure.json()["status"] == "ignored"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert {item.stock_state for item in order.items} == {"sold"}
    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 9
    assert inventory.reserved == 0


def test_upi_pending_then_captured_confirms_only_on_capture(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    pending = _captured_body(provider_order_id, "pay_upi_pending", body["total_paise"])
    pending["event"] = "payment.authorized"
    _entity(pending)["status"] = "authorized"
    _entity(pending)["captured"] = False

    first = _post_webhook(client, pending, event_id="evt_upi_pending")
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "ignored"
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"

    captured = _captured_body(provider_order_id, "pay_upi_pending", body["total_paise"])
    second = _post_webhook(client, captured, event_id="evt_upi_captured")
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "paid"
    assert _order(db_session, body["public_id"]).status == "paid"


def test_webhook_event_is_stored_before_processing(
    client: TestClient, db_session, monkeypatch
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(provider_order_id, "pay_durable", body["total_paise"])

    def explode(*_args, **_kwargs):
        raise RuntimeError("simulated worker crash")

    monkeypatch.setattr("app.services.webhooks.process_event", explode)

    response = _post_webhook(client, payload, event_id="evt_durable")
    assert response.status_code == 500
    assert "retry is safe" in response.json()["detail"]

    db_session.expire_all()
    event = db_session.scalar(
        select(WebhookEvent).where(WebhookEvent.event_id == "evt_durable")
    )
    assert event is not None
    assert event.status == "failed"
    assert "simulated worker crash" in (event.error or "")

    # The order was never confirmed by the failed worker.
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"


def test_late_capture_after_expiry_is_re_reserved_or_refunded(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    _expire_order(db_session, body["public_id"])
    assert client.post("/orders/expire").json() == {"expired": 1}

    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_late_hardening", body["total_paise"]),
        event_id="evt_late_hardening",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "paid"
    assert _order(db_session, body["public_id"]).status == "paid"


def test_stale_received_event_is_reclaimed_after_worker_crash(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(
        provider_order_id, "pay_stale_worker", body["total_paise"]
    )

    # A worker stored the delivery, then died before processing it. No HTTP
    # handler ran, so only the durable row survives.
    db_session.add(
        WebhookEvent(
            provider="razorpay",
            event_id="evt_stale_worker",
            event_type="payment.captured",
            status="received",
            payload=payload,
            created_at=datetime.now(timezone.utc) - RECEIVED_LEASE - timedelta(minutes=1),
        )
    )
    db_session.commit()

    retried = _post_webhook(client, payload, event_id="evt_stale_worker")
    assert retried.status_code == 200, retried.text
    assert retried.json()["status"] == "paid"
    assert _order(db_session, body["public_id"]).status == "paid"

    db_session.expire_all()
    event = db_session.scalar(
        select(WebhookEvent).where(WebhookEvent.event_id == "evt_stale_worker")
    )
    assert event is not None
    assert event.status == "processed"


def test_fresh_received_event_is_treated_as_an_in_flight_duplicate(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(
        provider_order_id, "pay_in_flight", body["total_paise"]
    )

    db_session.add(
        WebhookEvent(
            provider="razorpay",
            event_id="evt_in_flight",
            event_type="payment.captured",
            status="received",
            payload=payload,
            created_at=datetime.now(timezone.utc),
        )
    )
    db_session.commit()

    replay = _post_webhook(client, payload, event_id="evt_in_flight")
    assert replay.status_code == 200, replay.text
    assert replay.json()["status"] == "duplicate"
    # The live worker owns it; this delivery must not touch the order.
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"


def test_order_paid_before_capture_is_ignored_then_capture_confirms(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    order_only = {
        "event": "order.paid",
        "payload": {
            "order": {
                "entity": {
                    "id": provider_order_id,
                    "status": "paid",
                    "amount_paid": body["total_paise"],
                }
            }
        },
    }

    first = _post_webhook(client, order_only, event_id="evt_order_paid_first")
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "ignored"
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"

    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_after_order_paid", body["total_paise"]),
        event_id="evt_capture_after_order_paid",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "paid"
    assert _order(db_session, body["public_id"]).status == "paid"
