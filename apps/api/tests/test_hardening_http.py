from __future__ import annotations

import logging

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from starlette.applications import Starlette
from starlette.responses import PlainTextResponse
from starlette.routing import Route

from app.config import Settings
from app.main import app
from app.security import SecurityHeadersMiddleware, redact
from app.services.launch import (
    RuntimeConfigError,
    assert_runtime_config,
    runtime_config_failures,
)
from app.services.masking import mask_email, mask_phone
from app.services.orders import new_public_id
from app.services.razorpay import PaymentConfigurationError, assert_payment_config

from .test_orders import _order_with_one_pair


def _settings(**overrides) -> Settings:
    values = {
        "APP_ENV": "development",
        "RAZORPAY_KEY_ID": "rzp_test_mock",
        "RAZORPAY_KEY_SECRET": "test-key-secret",
        "RAZORPAY_WEBHOOK_SECRET": "test-webhook-secret",
        "RAZORPAY_MOCK": True,
        "MAIL_ENABLED": False,
        "CORS_ORIGINS": "http://localhost:3000",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def test_security_headers_are_present_on_api_responses(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert "default-src 'none'" in response.headers["content-security-policy"]
    # HSTS is only meaningful over HTTPS and is production-only here.
    assert "strict-transport-security" not in response.headers


def test_hsts_is_emitted_only_in_production() -> None:
    async def homepage(_request):
        return PlainTextResponse("ok")

    app_under_test = Starlette(routes=[Route("/", homepage)])
    app_under_test.add_middleware(SecurityHeadersMiddleware, production=True)

    with TestClient(app_under_test) as production_client:
        response = production_client.get("/")
    assert response.status_code == 200
    assert "max-age=31536000" in response.headers["strict-transport-security"]


def test_oversized_request_body_is_rejected(client: TestClient) -> None:
    limit = Settings(_env_file=None).max_request_bytes
    response = client.post(
        "/orders",
        content=b"x" * (limit + 1),
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 413
    assert response.json() == {"detail": "Request body is too large"}


def test_normal_request_body_is_not_limited_away(client: TestClient) -> None:
    response = client.get("/health/live")
    assert response.status_code == 200


def test_cors_allows_the_configured_storefront_origin(client: TestClient) -> None:
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_does_not_allow_an_unknown_origin(client: TestClient) -> None:
    response = client.options(
        "/health/live",
        headers={
            "Origin": "http://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.headers.get("access-control-allow-origin") != "http://evil.example"


def test_readiness_returns_503_when_the_database_is_unreachable(
    client: TestClient, monkeypatch
) -> None:
    class BrokenEngine:
        def connect(self):
            raise OSError("database is down")

    monkeypatch.setattr("app.main.engine", BrokenEngine())
    response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json() == {"status": "unavailable", "database": "unreachable"}


def test_liveness_does_not_depend_on_the_database(client: TestClient, monkeypatch) -> None:
    class BrokenEngine:
        def connect(self):
            raise OSError("database is down")

    monkeypatch.setattr("app.main.engine", BrokenEngine())
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_returns_200_when_the_database_answers(client: TestClient) -> None:
    response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "reachable"}


def test_unhandled_error_does_not_leak_a_stack_trace(client: TestClient, monkeypatch) -> None:
    def explode(_db):
        raise RuntimeError("secret internal detail")

    monkeypatch.setattr("app.routers.orders.expire_orders", explode)
    with TestClient(app, raise_server_exceptions=False) as raw_client:
        response = raw_client.post("/orders/expire")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert "Traceback" not in response.text
    assert "secret internal detail" not in response.text
    assert "RuntimeError" not in response.text


def test_public_order_read_masks_contact_details(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)

    response = client.get(f"/orders/{body['public_id']}")
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["customer_email"] == "a***@example.com"
    assert payload["customer_phone"].endswith("3210")
    assert payload["customer_phone"].startswith("*")
    assert "asha@example.com" not in response.text
    assert "98765 43210" not in response.text


def test_unknown_public_order_id_returns_404(client: TestClient) -> None:
    response = client.get("/orders/ord_this_order_does_not_exist")
    assert response.status_code == 404


def test_public_order_ids_are_high_entropy_and_unique() -> None:
    ids = {new_public_id() for _ in range(1000)}
    assert len(ids) == 1000
    for public_id in ids:
        assert public_id.startswith("ord_")
        # 18 random bytes -> 24 base64url characters, i.e. 144 bits.
        assert len(public_id) == len("ord_") + 24
        assert not public_id[4:].isdigit()


def test_a_guessed_sequential_id_cannot_read_another_order(
    client: TestClient, db_session
) -> None:
    body, _provider_order_id = _order_with_one_pair(client, db_session)
    assert client.get(f"/orders/{body['public_id']}").status_code == 200

    # Sequential ids are not a valid capability. The numeric database id must
    # never be accepted as the public order id.
    for guess in ("1", "ord_1", "ord_000000000000000000000000"):
        assert client.get(f"/orders/{guess}").status_code == 404


def test_log_redaction_removes_contact_and_credentials() -> None:
    message = (
        "customer asha@example.com phone +91 98765 43210 "
        "authorization: Bearer abc.def.ghi token=super-secret "
        "card 4111 1111 1111 1111"
    )
    cleaned = redact(message)
    assert "asha@example.com" not in cleaned
    assert "98765 43210" not in cleaned
    assert "abc.def.ghi" not in cleaned
    assert "super-secret" not in cleaned
    assert "4111 1111 1111 1111" not in cleaned
    assert "[REDACTED]" in cleaned
    assert "[REDACTED-CARD]" in cleaned


def test_redacting_filter_scrubs_log_records() -> None:
    from app.security import RedactingFilter

    record = logging.LogRecord(
        "test",
        logging.INFO,
        __file__,
        1,
        "email %s phone %s",
        ("asha@example.com", "+91 98765 43210"),
        None,
    )
    assert RedactingFilter().filter(record) is True
    rendered = record.getMessage()
    assert "asha@example.com" not in rendered
    assert "98765 43210" not in rendered


def test_redacting_formatter_scrubs_traceback_text() -> None:
    from app.security import RedactingFormatter

    try:
        raise RuntimeError("customer asha@example.com token=super-secret")
    except RuntimeError:
        import sys

        record = logging.LogRecord(
            "test",
            logging.ERROR,
            __file__,
            1,
            "order failed",
            (),
            sys.exc_info(),
        )
    rendered = RedactingFormatter().format(record)
    assert "asha@example.com" not in rendered
    assert "super-secret" not in rendered
    assert "Traceback" in rendered


def test_mask_helpers_keep_only_enough_to_recognise() -> None:
    assert mask_email("asha@example.com") == "a***@example.com"
    assert mask_email(None) == "***"
    assert mask_phone("+91 98765 43210") == "********3210"
    assert mask_phone("12") == "***"


def test_settings_reject_an_unknown_environment() -> None:
    with pytest.raises(ValidationError):
        _settings(APP_ENV="qa")


def test_settings_reject_an_insecure_razorpay_base() -> None:
    with pytest.raises(ValidationError):
        _settings(RAZORPAY_API_BASE="http://api.razorpay.com/v1")


def test_settings_reject_blank_smtp_host() -> None:
    with pytest.raises(ValidationError):
        _settings(SMTP_HOST="   ")


def test_settings_reject_an_out_of_range_body_limit() -> None:
    with pytest.raises(ValidationError):
        _settings(MAX_REQUEST_BYTES=10)


def test_settings_reject_an_empty_cors_allow_list() -> None:
    with pytest.raises(ValidationError):
        _settings(CORS_ORIGINS=" , ")


def test_production_refuses_a_static_admin_token() -> None:
    failures = runtime_config_failures(
        _settings(
            APP_ENV="production",
            ADMIN_API_TOKEN="static-token",
            CORS_ORIGINS="https://shop.santvana.example",
        )
    )
    assert any("ADMIN_API_TOKEN" in failure for failure in failures)
    with pytest.raises(RuntimeConfigError):
        assert_runtime_config(
            _settings(
                APP_ENV="production",
                ADMIN_API_TOKEN="static-token",
                CORS_ORIGINS="https://shop.santvana.example",
            )
        )


def test_production_refuses_wildcard_cors() -> None:
    failures = runtime_config_failures(
        _settings(APP_ENV="production", CORS_ORIGINS="*")
    )
    assert any("CORS_ORIGINS" in failure for failure in failures)


def test_development_allows_a_static_admin_token() -> None:
    failures = runtime_config_failures(
        _settings(APP_ENV="development", ADMIN_API_TOKEN="dev-token")
    )
    assert failures == []


def test_production_refuses_mock_payments() -> None:
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(_settings(APP_ENV="production", RAZORPAY_MOCK=True))


def test_production_refuses_test_razorpay_keys() -> None:
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(
            _settings(
                APP_ENV="production",
                RAZORPAY_MOCK=False,
                RAZORPAY_KEY_ID="rzp_test_realish",
                RAZORPAY_KEY_SECRET="secret",
                RAZORPAY_WEBHOOK_SECRET="hook",
            )
        )


def test_live_razorpay_keys_are_refused_outside_production() -> None:
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(
            _settings(
                APP_ENV="staging",
                RAZORPAY_MOCK=False,
                RAZORPAY_KEY_ID="rzp_live_abc",
                RAZORPAY_KEY_SECRET="secret",
            )
        )


def test_production_requires_a_webhook_secret() -> None:
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(
            _settings(
                APP_ENV="production",
                RAZORPAY_MOCK=False,
                RAZORPAY_KEY_ID="rzp_live_abc",
                RAZORPAY_KEY_SECRET="secret",
                RAZORPAY_WEBHOOK_SECRET="",
            )
        )


def test_key_id_and_secret_must_be_set_together() -> None:
    with pytest.raises(PaymentConfigurationError):
        assert_payment_config(
            _settings(
                APP_ENV="development",
                RAZORPAY_MOCK=False,
                RAZORPAY_KEY_ID="rzp_test_only_id",
                RAZORPAY_KEY_SECRET="",
            )
        )
