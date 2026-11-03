from __future__ import annotations

import copy
import hashlib
import hmac
import json
import os
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from app.config import Settings, get_settings
from app.models import Inventory, Order, Payment, ProductVariant, WebhookEvent
from app.services.razorpay import (
    PaymentConfigurationError,
    RazorpayGateway,
    assert_payment_config,
)

from .factories import make_category, make_product, make_variant

CHECKOUT = {
    "customer_name": "Asha Rao",
    "customer_email": "asha@example.com",
    "customer_phone": "+91 98765 43210",
    "address": {
        "line1": "12 Lake View Road",
        "line2": "Indiranagar",
        "city": "Bengaluru",
        "state": "Karnataka",
        "pincode": "560038",
        "country": "India",
    },
}


def _make_product(db_session, **overrides):
    category = make_category(
        db_session,
        name=overrides.pop("category_name", "Sneakers"),
        slug=overrides.pop("category_slug", "sneakers"),
        code=overrides.pop("category_code", "SN"),
    )
    values = {
        "status": "published",
        "price_inr": Decimal("2299.00"),
        "mrp_inr": Decimal("2299.00"),
    }
    values.update(overrides)
    return make_product(db_session, category, **values)


def _new_cart(client: TestClient) -> None:
    response = client.post("/cart")
    assert response.status_code == 201, response.text


def _add(client: TestClient, sku: str, quantity: int = 1) -> None:
    response = client.post("/cart/items", json={"sku": sku, "quantity": quantity})
    assert response.status_code == 200, response.text


def _payload(**overrides) -> dict:
    payload = copy.deepcopy(CHECKOUT)
    address = overrides.pop("address", None)
    if address:
        payload["address"].update(address)
    payload.update(overrides)
    return payload


def _place_order(client: TestClient, payload: dict | None = None):
    return client.post("/orders", json=payload or _payload())


def _checkout(client: TestClient, payload: dict | None = None) -> dict:
    response = _place_order(client, payload)
    assert response.status_code == 201, response.text
    return response.json()


def _inventory(db_session, sku: str) -> Inventory:
    db_session.expire_all()
    variant = db_session.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    assert variant is not None
    inventory = db_session.scalar(
        select(Inventory).where(Inventory.variant_id == variant.id)
    )
    assert inventory is not None
    return inventory


def _order(db_session, public_id: str) -> Order:
    db_session.expire_all()
    order = db_session.scalar(select(Order).where(Order.public_id == public_id))
    assert order is not None
    return order


def _payment(db_session, provider_order_id: str) -> Payment:
    db_session.expire_all()
    payment = db_session.scalar(
        select(Payment).where(Payment.provider_order_id == provider_order_id)
    )
    assert payment is not None
    return payment


def _expire_order(db_session, public_id: str) -> None:
    order = _order(db_session, public_id)
    order.reservation_expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()


def _captured_body(
    provider_order_id: str,
    payment_id: str,
    amount_paise: int,
    *,
    event: str = "payment.captured",
) -> dict:
    return {
        "event": event,
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "entity": "payment",
                    "amount": amount_paise,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": provider_order_id,
                    "method": "upi",
                    "captured": True,
                }
            }
        },
    }


def _failed_body(provider_order_id: str, payment_id: str) -> dict:
    return {
        "event": "payment.failed",
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "entity": "payment",
                    "amount": 0,
                    "currency": "INR",
                    "status": "failed",
                    "order_id": provider_order_id,
                    "error": {
                        "code": "BAD_REQUEST_ERROR",
                        "description": "Payment was declined by the issuer",
                    },
                }
            }
        },
    }


def _post_webhook(
    client: TestClient,
    body: dict,
    *,
    event_id: str,
    signature: str | None = None,
):
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    if signature is None:
        signature = RazorpayGateway(get_settings()).sign_webhook_body(raw)
    return client.post(
        "/webhooks/razorpay",
        content=raw,
        headers={
            "Content-Type": "application/json",
            "X-Razorpay-Signature": signature,
            "X-Razorpay-Event-Id": event_id,
        },
    )


def _order_with_one_pair(client: TestClient, db_session, *, on_hand: int = 10):
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=on_hand)
    _new_cart(client)
    _add(client, "RELAY-UK7", 1)
    body = _checkout(client)
    return body, body["checkout"]["order_id"]


def test_order_uses_database_prices_and_splits_gst_per_line(
    client: TestClient, db_session
) -> None:
    cheap = _make_product(
        db_session, name="Relay Moss", slug="relay-moss", price_inr=Decimal("2299.00")
    )
    make_variant(db_session, cheap, sku="RELAY-UK7", size_uk="UK 7", on_hand=10)
    premium = _make_product(
        db_session,
        id="TEST-002",
        sku_prefix="TEST-002",
        name="Ridge Boot",
        slug="ridge-boot",
        category_name="Boots",
        category_slug="boots",
        category_code="BT",
        price_inr=Decimal("2999.00"),
    )
    make_variant(
        db_session,
        premium,
        sku="RIDGE-UK8",
        size_uk="UK 8",
        on_hand=10,
        price_inr=Decimal("2999.00"),
    )

    _new_cart(client)
    _add(client, "RELAY-UK7", 2)
    _add(client, "RIDGE-UK8", 1)

    # The browser cannot choose the amount. This extra field is ignored.
    body = _checkout(client, _payload(total_paise=1, subtotal_paise=1))

    assert body["status"] == "awaiting_payment"
    assert body["currency"] == "INR"
    # 2 x ₹2,299 + 1 x ₹2,999 = ₹7,597.
    assert body["total_paise"] == 759_700
    assert body["shipping_paise"] == 0
    assert body["subtotal_paise"] + body["gst_paise"] == body["total_paise"]

    by_sku = {item["sku"]: item for item in body["items"]}
    assert by_sku["RELAY-UK7"]["unit_price_paise"] == 229_900
    assert by_sku["RELAY-UK7"]["line_total_paise"] == 459_800
    assert by_sku["RELAY-UK7"]["gst_rate_pct"] == 5
    assert by_sku["RELAY-UK7"]["gst_paise"] == 21_895
    assert by_sku["RELAY-UK7"]["taxable_value_paise"] == 437_905
    assert by_sku["RIDGE-UK8"]["gst_rate_pct"] == 18
    assert by_sku["RIDGE-UK8"]["gst_paise"] == 45_747
    assert by_sku["RIDGE-UK8"]["taxable_value_paise"] == 254_153
    assert body["gst_paise"] == 67_642

    # Seller details stay founder placeholders; no GSTIN is invented.
    assert body["seller"]["state"] == "[TO CONFIRM: founder]"
    assert body["seller"]["gstin"] == "[TO CONFIRM: founder]"

    # The stock hold moved from the cart to the order.
    order = _order(db_session, body["public_id"])
    assert order.status == "awaiting_payment"
    assert {item.stock_state for item in order.items} == {"reserved"}
    assert _inventory(db_session, "RELAY-UK7").reserved == 2
    assert _inventory(db_session, "RIDGE-UK8").reserved == 1

    # Reading the order inside the payment window must not expire it.
    read = client.get(f"/orders/{body['public_id']}")
    assert read.status_code == 200
    assert read.json()["status"] == "awaiting_payment"
    assert read.json()["next_action"] == "pay"


def test_checkout_requires_an_active_cart(client: TestClient) -> None:
    assert _place_order(client).status_code == 404


def test_checkout_rejects_invalid_indian_address_and_phone(client: TestClient) -> None:
    invalid_payloads = [
        _payload(address={"pincode": "012345"}),
        _payload(address={"pincode": "56003"}),
        _payload(address={"state": "California"}),
        _payload(address={"country": "Nepal"}),
        _payload(customer_phone="12345"),
        _payload(customer_phone="+1 415 555 0100"),
        _payload(customer_email="not-an-email"),
        _payload(customer_name="A"),
    ]
    for payload in invalid_payloads:
        response = _place_order(client, payload)
        assert response.status_code == 422, (payload, response.text)


def test_checkout_normalises_phone_state_and_pincode(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=10)

    _new_cart(client)
    _add(client, "RELAY-UK7", 1)
    body = _checkout(
        client,
        _payload(
            customer_phone="098765 43210",
            address={"state": "karnataka", "pincode": "560 038"},
        ),
    )
    assert body["customer_phone"] == "9876543210"
    assert body["address"]["state"] == "Karnataka"
    assert body["address"]["pincode"] == "560038"


def test_webhook_with_a_bad_signature_is_rejected(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    webhook = _captured_body(provider_order_id, "pay_bad_sig", body["total_paise"])

    response = _post_webhook(
        client, webhook, event_id="evt_bad_sig", signature="deadbeef"
    )
    assert response.status_code == 400
    assert "signature" in response.json()["detail"].lower()

    assert _order(db_session, body["public_id"]).status == "awaiting_payment"
    assert _inventory(db_session, "RELAY-UK7").reserved == 1
    assert db_session.scalar(select(WebhookEvent)) is None


def test_replayed_webhook_is_idempotent(client: TestClient, db_session) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    webhook = _captured_body(provider_order_id, "pay_replay", body["total_paise"])

    first = _post_webhook(client, webhook, event_id="evt_replay")
    assert first.status_code == 200, first.text
    assert first.json()["status"] == "paid"

    second = _post_webhook(client, webhook, event_id="evt_replay")
    assert second.status_code == 200, second.text
    assert second.json()["status"] == "duplicate"

    # A different event id carrying the same payment must also be a no-op.
    third = _post_webhook(client, webhook, event_id="evt_replay_again")
    assert third.status_code == 200, third.text
    assert third.json()["status"] == "already_paid"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert order.paid_at is not None
    assert {item.stock_state for item in order.items} == {"sold"}

    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 9
    assert inventory.reserved == 0

    assert len(db_session.scalars(select(WebhookEvent)).all()) == 2
    assert _payment(db_session, provider_order_id).status == "captured"


def test_failed_payment_releases_stock_and_retry_can_pay(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    failed = _post_webhook(
        client,
        _failed_body(provider_order_id, "pay_failed"),
        event_id="evt_failed",
    )
    assert failed.status_code == 200, failed.text
    assert failed.json()["status"] == "payment_failed"

    order = _order(db_session, body["public_id"])
    assert order.status == "payment_failed"
    assert {item.stock_state for item in order.items} == {"released"}
    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 10
    assert inventory.reserved == 0

    retry = client.post(f"/orders/{body['public_id']}/payment")
    assert retry.status_code == 200, retry.text
    retried = retry.json()
    assert retried["status"] == "awaiting_payment"
    new_provider_order_id = retried["checkout"]["order_id"]
    assert new_provider_order_id != provider_order_id
    assert _inventory(db_session, "RELAY-UK7").reserved == 1

    captured = _post_webhook(
        client,
        _captured_body(new_provider_order_id, "pay_retry", retried["total_paise"]),
        event_id="evt_retry_captured",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "paid"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 9
    assert inventory.reserved == 0


def test_expired_order_releases_stock(client: TestClient, db_session) -> None:
    body, _ = _order_with_one_pair(client, db_session)
    _expire_order(db_session, body["public_id"])

    sweep = client.post("/orders/expire")
    assert sweep.status_code == 200
    assert sweep.json() == {"expired": 1}

    order = _order(db_session, body["public_id"])
    assert order.status == "expired"
    assert order.expired_at is not None
    assert {item.stock_state for item in order.items} == {"released"}
    assert _inventory(db_session, "RELAY-UK7").reserved == 0

    # A second sweep finds nothing to do.
    assert client.post("/orders/expire").json() == {"expired": 0}


def test_late_payment_after_expiry_reserves_again(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    _expire_order(db_session, body["public_id"])
    assert client.post("/orders/expire").json() == {"expired": 1}
    assert _inventory(db_session, "RELAY-UK7").reserved == 0

    # The customer paid just after the window closed. Stock is still there, so
    # the order is re-reserved and confirmed rather than refunded.
    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_late", body["total_paise"]),
        event_id="evt_late_capture",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "paid"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert {item.stock_state for item in order.items} == {"sold"}
    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 9
    assert inventory.reserved == 0


def test_late_payment_when_stock_is_gone_is_refunded(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    _expire_order(db_session, body["public_id"])
    assert client.post("/orders/expire").json() == {"expired": 1}

    inventory = _inventory(db_session, "RELAY-UK7")
    inventory.on_hand = 0
    db_session.commit()

    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_late_gone", body["total_paise"]),
        event_id="evt_late_gone",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "refunded"

    order = _order(db_session, body["public_id"])
    assert order.status == "refunded"
    payment = _payment(db_session, provider_order_id)
    assert payment.status == "refunded"
    assert payment.refunded_paise == body["total_paise"]
    assert payment.refund_id
    assert _inventory(db_session, "RELAY-UK7").on_hand == 0


def test_amount_mismatch_is_refunded_not_marked_paid(
    client: TestClient, db_session
) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)

    captured = _post_webhook(
        client,
        _captured_body(provider_order_id, "pay_wrong_amount", body["total_paise"] - 100),
        event_id="evt_wrong_amount",
    )
    assert captured.status_code == 200, captured.text
    assert captured.json()["status"] == "refunded"

    order = _order(db_session, body["public_id"])
    assert order.status == "refunded"
    payment = _payment(db_session, provider_order_id)
    assert payment.failure_code == "amount_mismatch"
    assert payment.status == "refunded"
    # Stock was never sold; the reservation was released by the refund path.
    assert _inventory(db_session, "RELAY-UK7").on_hand == 10


def test_browser_payment_verify_is_only_a_hint(client: TestClient, db_session) -> None:
    body, provider_order_id = _order_with_one_pair(client, db_session)
    settings = get_settings()
    payment_id = "pay_browser_hint"
    good_signature = hmac.new(
        (settings.razorpay_key_secret or "").encode("utf-8"),
        f"{provider_order_id}|{payment_id}".encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    verified = client.post(
        f"/orders/{body['public_id']}/payment-verify",
        json={
            "razorpay_order_id": provider_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": good_signature,
        },
    )
    assert verified.status_code == 200, verified.text
    assert verified.json()["verified"] is True
    assert verified.json()["order_status"] == "awaiting_payment"

    # A valid browser signature does not confirm the order.
    assert _order(db_session, body["public_id"]).status == "awaiting_payment"

    bad = client.post(
        f"/orders/{body['public_id']}/payment-verify",
        json={
            "razorpay_order_id": provider_order_id,
            "razorpay_payment_id": payment_id,
            "razorpay_signature": "0" * 64,
        },
    )
    assert bad.status_code == 200
    assert bad.json()["verified"] is False


def test_double_submit_is_rejected(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=10)
    _new_cart(client)
    _add(client, "RELAY-UK7", 1)

    first = _place_order(client)
    assert first.status_code == 201, first.text
    second = _place_order(client)
    assert second.status_code == 409
    assert "no longer active" in second.json()["detail"].lower()

    assert len(db_session.scalars(select(Order)).all()) == 1


def test_mock_pay_goes_through_the_signed_webhook_path(
    client: TestClient, db_session
) -> None:
    body, _ = _order_with_one_pair(client, db_session)

    paid = client.post(f"/orders/{body['public_id']}/mock-pay")
    assert paid.status_code == 200, paid.text
    assert paid.json()["status"] == "paid"

    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    assert _inventory(db_session, "RELAY-UK7").on_hand == 9

    # Calling it again is harmless.
    again = client.post(f"/orders/{body['public_id']}/mock-pay")
    assert again.status_code == 200
    assert again.json()["status"] == "paid"
    assert _inventory(db_session, "RELAY-UK7").on_hand == 9


def test_live_keys_are_refused_outside_production() -> None:
    settings = Settings(
        APP_ENV="development",
        RAZORPAY_KEY_ID="rzp_live_example",
        RAZORPAY_KEY_SECRET="secret",
        RAZORPAY_WEBHOOK_SECRET="webhook-secret",
        RAZORPAY_MOCK=False,
    )
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(settings)


def test_mock_mode_is_refused_in_production() -> None:
    settings = Settings(
        APP_ENV="production",
        RAZORPAY_KEY_ID="rzp_test_example",
        RAZORPAY_KEY_SECRET="secret",
        RAZORPAY_WEBHOOK_SECRET="webhook-secret",
        RAZORPAY_MOCK=True,
    )
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(settings)


def test_production_requires_a_webhook_secret() -> None:
    settings = Settings(
        APP_ENV="production",
        RAZORPAY_KEY_ID="rzp_test_example",
        RAZORPAY_KEY_SECRET="secret",
        RAZORPAY_WEBHOOK_SECRET="",
        RAZORPAY_MOCK=False,
    )
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(settings)


@pytest.mark.skipif(
    not os.environ.get("TEST_DATABASE_URL"),
    reason="needs PostgreSQL row locks; run with TEST_DATABASE_URL set",
)
def test_concurrent_duplicate_captures_sell_stock_once(
    client: TestClient, db_session, db_engine
) -> None:
    """Two deliveries of the same capture must not sell the pair twice."""

    import threading
    from concurrent.futures import ThreadPoolExecutor

    from sqlalchemy.orm import sessionmaker

    from app.services.orders import handle_payment_captured

    body, provider_order_id = _order_with_one_pair(client, db_session)
    payload = _captured_body(provider_order_id, "pay_concurrent", body["total_paise"])
    settings = get_settings()
    barrier = threading.Barrier(2)
    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def deliver(index: int) -> str:
        with factory() as session:
            barrier.wait(timeout=10)
            try:
                return handle_payment_captured(session, payload, settings)
            except Exception as exc:  # noqa: BLE001 - surfaced in the assertion
                return f"error: {exc}"

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(deliver, range(2)))

    assert sorted(results) == ["already_paid", "paid"]
    order = _order(db_session, body["public_id"])
    assert order.status == "paid"
    inventory = _inventory(db_session, "RELAY-UK7")
    assert inventory.on_hand == 9
    assert inventory.reserved == 0
