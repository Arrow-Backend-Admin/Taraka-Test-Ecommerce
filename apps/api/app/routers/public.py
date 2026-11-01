from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..schemas import PublicProductDetailOut, PublicProductOut
from ..services.publish import (
    preview_product,
    preview_products,
    public_product,
    public_products,
)
from ..telemetry import telemetry_configured

router = APIRouter(tags=["catalogue"])


@router.get("/health")
def health() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "santvana-api",
        "telemetry_enabled": telemetry_configured(),
    }


@router.get("/catalogue", response_model=list[PublicProductOut])
def list_catalogue(
    preview_drafts: bool = Query(default=False),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    environment = settings.environment
    if preview_drafts:
        return preview_products(db, environment=environment)
    return public_products(db, environment=environment)


@router.get("/catalogue/{slug}", response_model=PublicProductDetailOut)
def get_catalogue_product(
    slug: str,
    preview_drafts: bool = Query(default=False),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    environment = settings.environment
    product = (
        preview_product(db, slug, environment=environment)
        if preview_drafts
        else public_product(db, slug, environment=environment)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or not published")
    return product
