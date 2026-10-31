from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..schemas import PublicProductDetailOut, PublicProductOut
from ..services.publish import public_product, public_products
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
def list_catalogue(db: Session = Depends(get_db)) -> list[dict]:
    return public_products(db)


@router.get("/catalogue/{slug}", response_model=PublicProductDetailOut)
def get_catalogue_product(slug: str, db: Session = Depends(get_db)) -> dict:
    product = public_product(db, slug)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found or not published")
    return product
