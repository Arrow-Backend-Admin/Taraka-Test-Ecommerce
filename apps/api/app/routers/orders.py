from __future__ import annotations

import json
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..schemas import (
    CheckoutRequest,
    OrderCreatedOut,
    OrderOut,
    PaymentVerifyOut,
    PaymentVerifyRequest,
)
from ..services.cart import CART_COOKIE_NAME, CartNotFound, CartRuleError, require_cart
from ..services.inventory import InventoryNotFound, OutOfStock
from ..services.orders import (
    OrderNotFound,
    OrderStateError,
    PaymentStartError,
    checkout_options,
    create_order,
    create_payment_attempt,
    expire_order,
    expire_orders,
    get_order,
    order_payload,
    verify_payment_hint,
)
from ..services.razorpay import PaymentConfigurationError, RazorpayError, RazorpayGateway
from ..services.webhooks import process_webhook

router = APIRouter(tags=["orders"])


def _token(request: Request, header_token: str | None) -> str | None:
    return request.cookies.get(CART_COOKIE_NAME) or header_token


def _load_order(db: Session, public_id: str):
    try:
        order = get_order(db, public_id)
    except OrderNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if order.status in {"created", "awaiting_payment"}:
        expire_order(db, order)
        db.refresh(order)
    return order


@router.post("/orders", response_model=OrderCreatedOut, status_code=201)
def place_order(
    payload: CheckoutRequest,
    request: Request,
    x_cart_token: str | None = Header(default=None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    try:
        cart = require_cart(db, _token(request, x_cart_token))
        order, payment = create_order(db, cart, payload, settings)
    except CartNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except (OrderStateError, CartRuleError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (OutOfStock, InventoryNotFound) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except PaymentStartError as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "message": str(exc),
                "order_id": exc.public_id,
                "status": "payment_failed",
            },
        ) from exc
    except PaymentConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return {
        **order_payload(order),
        "checkout": checkout_options(order, payment, settings),
    }


@router.get("/orders/{public_id}", response_model=OrderOut)
def read_order(
    public_id: str,
    db: Session = Depends(get_db),
) -> dict:
    order = _load_order(db, public_id)
    # The URL is a capability token until authentication ships. Contact details
    # are masked so a shared link or screenshot does not expose them.
    return order_payload(order, mask_contact=True)


@router.post("/orders/{public_id}/payment", response_model=OrderCreatedOut)
def retry_payment(
    public_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    order = _load_order(db, public_id)
    if order.status == "paid":
        raise HTTPException(status_code=409, detail="Order is already paid")
    if order.status in {"refunded", "refund_pending"}:
        raise HTTPException(status_code=409, detail="Order is being refunded")
    try:
        payment = create_payment_attempt(db, order, settings)
    except OrderStateError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except (PaymentConfigurationError, RazorpayError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return {
        **order_payload(order),
        "checkout": checkout_options(order, payment, settings),
    }


@router.post("/orders/{public_id}/payment-verify", response_model=PaymentVerifyOut)
def verify_payment(
    public_id: str,
    payload: PaymentVerifyRequest,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    order = _load_order(db, public_id)
    known = {payment.provider_order_id for payment in order.payments}
    if payload.razorpay_order_id not in known:
        raise HTTPException(status_code=404, detail="Payment attempt not found")
    return verify_payment_hint(
        db,
        order,
        provider_order_id=payload.razorpay_order_id,
        provider_payment_id=payload.razorpay_payment_id,
        signature=payload.razorpay_signature,
        settings=settings,
    )


@router.post("/orders/{public_id}/mock-pay", response_model=OrderOut)
def mock_pay(
    public_id: str,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    """Local-review shortcut. It signs a fake webhook and uses the real path.

    Refused unless RAZORPAY_MOCK=true and APP_ENV is not production. It never
    touches card data and cannot run in a real deployment.
    """

    if settings.is_production or not settings.razorpay_mock:
        raise HTTPException(status_code=404, detail="Not found")

    order = _load_order(db, public_id)
    if order.status == "paid":
        return order_payload(order)
    payment = next(
        (entry for entry in reversed(order.payments) if entry.status == "created"),
        None,
    )
    if payment is None:
        raise HTTPException(status_code=409, detail="No open payment attempt")

    payment_id = f"pay_mock_{uuid.uuid4().hex[:20]}"
    body = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "entity": "payment",
                    "amount": order.total_paise,
                    "currency": "INR",
                    "status": "captured",
                    "order_id": payment.provider_order_id,
                    "method": "upi",
                    "captured": True,
                }
            }
        },
    }
    raw = json.dumps(body, separators=(",", ":")).encode("utf-8")
    signature = RazorpayGateway(settings).sign_webhook_body(raw)
    process_webhook(
        db,
        raw_body=raw,
        signature=signature,
        event_id_header=f"evt_mock_{uuid.uuid4().hex[:20]}",
        settings=settings,
    )
    order = _load_order(db, public_id)
    return order_payload(order)


@router.post("/orders/expire", response_model=dict)
def expire_stale_orders(
    db: Session = Depends(get_db),
) -> dict:
    """Opportunistic sweep. A cron job can call the same service method."""

    return {"expired": expire_orders(db)}
