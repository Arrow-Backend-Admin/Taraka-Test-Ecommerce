from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import admin, cart, public
from .telemetry import configure_telemetry

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Catalogue, publish guard and inventory API for the Sāntvana concept storefront.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Cart-Token"],
)

app.include_router(public.router)
app.include_router(cart.router)
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
