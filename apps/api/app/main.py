from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from .config import get_settings
from .db import SessionLocal, engine
from .routers import admin, cart, orders, public, webhooks
from .security import (
    RequestSizeLimitMiddleware,
    SecurityHeadersMiddleware,
    install_log_redaction,
)
from .services.launch import assert_launch_ready, assert_runtime_config
from .services.razorpay import assert_payment_config
from .telemetry import configure_telemetry

settings = get_settings()
logger = logging.getLogger("santvana.api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Fail fast on dangerous deployment configuration, before the first request.
    assert_runtime_config(settings)
    assert_payment_config(settings)
    if settings.uses_live_razorpay_keys:
        with SessionLocal() as db:
            assert_launch_ready(db)
    yield
    # Graceful shutdown: stop handing out pooled connections and let in-flight
    # work finish before the process exits.
    engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Catalogue, inventory, guest cart and checkout API for the Sāntvana concept storefront.",
    lifespan=lifespan,
)

# Order matters: the size limit runs before routing, then CORS, then headers.
app.add_middleware(
    SecurityHeadersMiddleware,
    production=settings.is_production,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Cart-Token"],
)
app.add_middleware(RequestSizeLimitMiddleware, max_bytes=settings.max_request_bytes)

install_log_redaction()


@app.exception_handler(Exception)
async def unhandled_exception(_request: Request, exc: Exception) -> JSONResponse:
    # Log the type and a redacted message, never a stack trace to the client.
    logger.exception("Unhandled API error: %s", type(exc).__name__)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


app.include_router(public.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(webhooks.router)
app.include_router(admin.router)

configure_telemetry(app)


@app.get("/health/live")
def liveness() -> dict[str, str]:
    """The process is running. It does not depend on any external service."""

    return {"status": "ok"}


@app.get("/health/ready")
def readiness() -> JSONResponse:
    """The process can serve traffic: the database answers a trivial query."""

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - readiness must never raise
        logger.warning("Readiness check failed: %s", type(exc).__name__)
        return JSONResponse(
            status_code=503,
            content={"status": "unavailable", "database": "unreachable"},
        )
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "database": "reachable"},
    )


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "santvana-api",
        "version": "0.1.0",
        "catalogue": "/catalogue",
        "health": "/health",
        "live": "/health/live",
        "ready": "/health/ready",
        "docs": "/docs",
    }
