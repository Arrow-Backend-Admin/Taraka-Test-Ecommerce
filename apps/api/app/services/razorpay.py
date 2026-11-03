"""Razorpay hosted checkout client.

The API never sees card data. It creates a Razorpay order, the browser opens
Razorpay's hosted checkout, and payment is confirmed only by a signed webhook.

Keys come from the environment (or a local ``.env``) and are never logged. A
``rzp_live_`` key is refused outside production, and mock mode is refused in
production.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import uuid
from dataclasses import dataclass
from typing import Any
from urllib import error as urlerror
from urllib import request as urlrequest

from ..config import Settings


class PaymentConfigurationError(RuntimeError):
    pass


class RazorpayError(RuntimeError):
    pass


def assert_payment_config(settings: Settings) -> None:
    """Refuse dangerous payment configurations before the app starts."""

    key_id = (settings.razorpay_key_id or "").strip()
    key_secret = (settings.razorpay_key_secret or "").strip()
    webhook_secret = (settings.razorpay_webhook_secret or "").strip()

    if settings.razorpay_mock and settings.is_production:
        raise PaymentConfigurationError(
            "RAZORPAY_MOCK must be false when APP_ENV=production"
        )
    if settings.uses_live_razorpay_keys and not settings.is_production:
        raise PaymentConfigurationError(
            "Live Razorpay keys (rzp_live_) are refused unless APP_ENV=production"
        )
    if bool(key_id) != bool(key_secret):
        raise PaymentConfigurationError(
            "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be set together"
        )
    if settings.is_production:
        if not key_id or not key_secret:
            raise PaymentConfigurationError(
                "Razorpay keys are required when APP_ENV=production"
            )
        if not webhook_secret:
            raise PaymentConfigurationError(
                "RAZORPAY_WEBHOOK_SECRET is required when APP_ENV=production"
            )


@dataclass
class RazorpayGateway:
    settings: Settings

    @property
    def configured(self) -> bool:
        return bool(
            (self.settings.razorpay_key_id or "").strip()
            and (self.settings.razorpay_key_secret or "").strip()
        )

    @property
    def webhook_configured(self) -> bool:
        return bool((self.settings.razorpay_webhook_secret or "").strip())

    def _auth_header(self) -> str:
        raw = (
            f"{(self.settings.razorpay_key_id or '').strip()}:"
            f"{(self.settings.razorpay_key_secret or '').strip()}"
        ).encode("utf-8")
        return "Basic " + base64.b64encode(raw).decode("ascii")

    def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        url = self.settings.razorpay_api_base.rstrip("/") + path
        body = json.dumps(payload).encode("utf-8")
        request = urlrequest.Request(
            url,
            data=body,
            method="POST",
            headers={
                "Authorization": self._auth_header(),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )
        try:
            with urlrequest.urlopen(request, timeout=20) as response:  # noqa: S310
                return json.loads(response.read().decode("utf-8"))
        except urlerror.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RazorpayError(
                f"Razorpay returned {exc.code}: {detail[:500]}"
            ) from exc
        except urlerror.URLError as exc:
            raise RazorpayError(f"Could not reach Razorpay: {exc.reason}") from exc
        except json.JSONDecodeError as exc:
            raise RazorpayError("Razorpay returned an unreadable response") from exc

    def create_order(
        self, *, amount_paise: int, receipt: str, notes: dict[str, str] | None = None
    ) -> dict[str, Any]:
        if not self.configured and not self.settings.razorpay_mock:
            raise PaymentConfigurationError(
                "Razorpay keys are not configured. Set RAZORPAY_KEY_ID and "
                "RAZORPAY_KEY_SECRET, or use RAZORPAY_MOCK=true locally."
            )
        if amount_paise <= 0:
            raise RazorpayError("Razorpay order amount must be positive")
        if self.settings.razorpay_mock:
            return {
                "id": f"order_mock_{uuid.uuid4().hex[:20]}",
                "entity": "order",
                "amount": amount_paise,
                "amount_paid": 0,
                "amount_due": amount_paise,
                "currency": "INR",
                "receipt": receipt,
                "status": "created",
                "notes": notes or {},
            }
        return self._post(
            "/orders",
            {
                "amount": amount_paise,
                "currency": "INR",
                "receipt": receipt,
                "notes": notes or {},
            },
        )

    def refund(
        self,
        *,
        payment_id: str,
        amount_paise: int,
        notes: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        if self.settings.razorpay_mock:
            return {
                "id": f"rfnd_mock_{uuid.uuid4().hex[:20]}",
                "entity": "refund",
                "payment_id": payment_id,
                "amount": amount_paise,
                "currency": "INR",
                "status": "processed",
                "notes": notes or {},
            }
        if not self.configured:
            raise PaymentConfigurationError("Razorpay keys are not configured")
        return self._post(
            f"/payments/{payment_id}/refund",
            {"amount": amount_paise, "notes": notes or {}},
        )

    def verify_payment_signature(
        self, *, order_id: str, payment_id: str, signature: str
    ) -> bool:
        secret = (self.settings.razorpay_key_secret or "").strip()
        if not secret or not signature:
            return False
        expected = hmac.new(
            secret.encode("utf-8"),
            f"{order_id}|{payment_id}".encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def verify_webhook_signature(self, *, body: bytes, signature: str) -> bool:
        secret = (self.settings.razorpay_webhook_secret or "").strip()
        if not secret or not signature:
            return False
        expected = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
        return hmac.compare_digest(expected, signature)

    def sign_webhook_body(self, body: bytes) -> str:
        """Test and mock helper. Never expose this through an API route."""

        secret = (self.settings.razorpay_webhook_secret or "").strip()
        if not secret:
            raise PaymentConfigurationError("RAZORPAY_WEBHOOK_SECRET is not set")
        return hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
