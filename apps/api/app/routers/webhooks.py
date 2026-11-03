from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..services.razorpay import RazorpayGateway
from ..services.webhooks import (
    WebhookPayloadError,
    WebhookSignatureError,
    process_webhook,
)

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("/razorpay")
async def razorpay_webhook(
    request: Request,
    x_razorpay_signature: str | None = Header(default=None),
    x_razorpay_event_id: str | None = Header(default=None),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> JSONResponse:
    gateway = RazorpayGateway(settings)
    if not gateway.webhook_configured:
        raise HTTPException(status_code=503, detail="Webhook secret is not configured")
    if not x_razorpay_signature:
        raise HTTPException(status_code=400, detail="Missing webhook signature")

    raw_body = await request.body()
    try:
        result = process_webhook(
            db,
            raw_body=raw_body,
            signature=x_razorpay_signature,
            event_id_header=x_razorpay_event_id,
            settings=settings,
        )
    except WebhookSignatureError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except WebhookPayloadError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # noqa: BLE001 - 500 tells Razorpay to retry
        raise HTTPException(
            status_code=500, detail="Webhook processing failed; retry is safe"
        ) from exc

    return JSONResponse(status_code=200, content=result)
