from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import SessionLocal
from .routers import admin, cart, orders, public, webhooks
from .services.launch import assert_launch_ready
from .services.razorpay import assert_payment_config
from .telemetry import configure_telemetry

settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Refuse dangerous payment configurations before serving a request. Live
    # keys additionally require the launch check to pass.
    assert_payment_config(settings)
    if settings.uses_live_razorpay_keys:
        with SessionLocal() as db:
            assert_launch_ready(db)
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Catalogue, inventory, guest cart and checkout API for the Sāntvana concept storefront.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Cart-Token"],
)

app.include_router(public.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(webhooks.router)
app.include_router(admin.router)

configure_telemetry(app)


@app.get("/")
def root() -> dict[str, str]:
    return {
        "service": "santvana-api",
        "version": "0.1.0",
        "catalogue": "/catalogue",
        "health": "/health",
        "docs": "/docs",
    }
