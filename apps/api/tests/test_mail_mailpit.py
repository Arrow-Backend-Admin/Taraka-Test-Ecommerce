"""Mail path checks against a real Mailpit container.

These tests are skipped unless ``MAILPIT_URL`` is set, so the normal fast suite
does not need Docker. CI starts Mailpit and sets ``MAILPIT_URL``.

The important guarantee is not "email always sends". It is "email failure never
changes the payment outcome". The last test proves that with a real refused SMTP
connection, not a mock.
"""

from __future__ import annotations

import json
import os
import time
import uuid
from urllib import request as urlrequest

import pytest
from sqlalchemy import select

from app.config import Settings, get_settings
from app.models import EmailOutbox
from app.services.mail import send_email

from .test_orders import _order_with_one_pair

MAILPIT_URL = (os.environ.get("MAILPIT_URL") or "").rstrip("/")
SMTP_HOST = os.environ.get("MAILPIT_SMTP_HOST", "127.0.0.1")
SMTP_PORT = int(os.environ.get("MAILPIT_SMTP_PORT", "1025"))

requires_mailpit = pytest.mark.skipif(
    not MAILPIT_URL,
    reason="MAILPIT_URL is not set; start Mailpit to run this test",
)


def _settings(**overrides) -> Settings:
    values = {
        "APP_ENV": "development",
        "MAIL_ENABLED": True,
        "SMTP_HOST": SMTP_HOST,
        "SMTP_PORT": SMTP_PORT,
        "SMTP_USERNAME": None,
        "SMTP_PASSWORD": None,
        "SMTP_STARTTLS": False,
        "MAIL_FROM": "orders@santvana.example",
        "RAZORPAY_KEY_ID": "rzp_test_mock",
        "RAZORPAY_KEY_SECRET": "test-key-secret",
        "RAZORPAY_WEBHOOK_SECRET": "test-webhook-secret",
        "RAZORPAY_MOCK": True,
        "ADMIN_API_TOKEN": "test-admin-token",
        "CORS_ORIGINS": "http://localhost:3000",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def _messages() -> list[dict]:
    with urlrequest.urlopen(f"{MAILPIT_URL}/api/v1/messages", timeout=5) as response:
        payload = json.loads(response.read().decode("utf-8"))
    return payload.get("messages") or []


def _wait_for_subject(subject: str, timeout: float = 10.0) -> dict | None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for message in _messages():
            if str(message.get("Subject") or "").startswith(subject):
                return message
        time.sleep(0.25)
    return None


@requires_mailpit
def test_smtp_delivers_to_mailpit() -> None:
    subject = f"Mailpit integration {uuid.uuid4()}"
    sent = send_email(
        to_email="asha@example.com",
        subject=subject,
        body="Plain text confirmation body.",
        settings=_settings(),
    )
    assert sent is True

    message = _wait_for_subject(subject)
    assert message is not None, f"Mailpit did not receive {subject!r}"
    assert message.get("To", [{}])[0].get("Address") == "asha@example.com"


@requires_mailpit
def test_confirmation_email_is_sent_after_a_captured_payment(
    client, db_session
) -> None:
    settings = _settings()
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: settings
    try:
        body, _provider_order_id = _order_with_one_pair(client, db_session)
        response = client.post(f"/orders/{body['public_id']}/mock-pay")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "paid"
    finally:
        app.dependency_overrides.pop(get_settings, None)

    subject = f"Order {body['public_id']} confirmed"
    message = _wait_for_subject(subject, timeout=10.0)
    assert message is not None, "the order confirmation never reached Mailpit"

    db_session.expire_all()
    order = _order(db_session, body["public_id"])
    row = db_session.scalar(
        select(EmailOutbox).where(EmailOutbox.order_id == order.id)
    )
    assert row is not None
    assert row.status == "sent"
    assert order.confirmation_email_sent_at is not None


def test_refused_smtp_connection_does_not_undo_a_captured_payment(
    client, db_session
) -> None:
    # Port 1 is not an SMTP server on the test host. smtplib raises a real
    # connection error, exercising the same failure a dead mail server gives.
    settings = _settings(SMTP_HOST="127.0.0.1", SMTP_PORT=1, SMTP_TIMEOUT_SECONDS=2)
    from app.main import app

    app.dependency_overrides[get_settings] = lambda: settings
    try:
        body, _provider_order_id = _order_with_one_pair(client, db_session)
        response = client.post(f"/orders/{body['public_id']}/mock-pay")
        assert response.status_code == 200, response.text
        assert response.json()["status"] == "paid"
    finally:
        app.dependency_overrides.pop(get_settings, None)

    db_session.expire_all()
    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert order.paid_at is not None

    row = db_session.scalar(
        select(EmailOutbox).where(EmailOutbox.order_id == order.id)
    )
    assert row is not None
    assert row.status == "pending"
    assert row.attempts >= 1
    assert row.last_error
    assert order.confirmation_email_sent_at is None


def _order(db_session, public_id: str):
    from app.models import Order

    return db_session.scalar(select(Order).where(Order.public_id == public_id))
