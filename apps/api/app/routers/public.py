from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..schemas import PublicProductDetailOut, PublicProductOut, StockOut
from ..services import catalogue as catalogue_service
from ..services.cart import stock_for_slug
from ..services.publish import (
    is_production,
    preview_product,
    public_product,
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


def _filters(
    *,
    q: str | None,
    category: str | None,
    colour: str | None,
    size: str | None,
    min_price: float | None,
    max_price: float | None,
) -> dict:
    return {
        "query": q,
        "category": category,
        "colour": colour,
        "size": size,
        "min_price": min_price,
        "max_price": max_price,
    }


@router.get("/catalogue", response_model=list[PublicProductOut])
def list_catalogue(
    preview_drafts: bool = Query(default=False),
    q: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=80),
    colour: str | None = Query(default=None, max_length=80),
    size: str | None = Query(default=None, max_length=12),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> list[dict]:
    environment = settings.environment
    products = catalogue_service.filtered_products(
        db,
        preview=preview_drafts,
        **_filters(
            q=q,
            category=category,
            colour=colour,
            size=size,
            min_price=min_price,
            max_price=max_price,
        ),
    )
    return catalogue_service.serialise(
        db, products, preview=preview_drafts, environment=environment
    )


@router.get("/catalogue/facets")
def catalogue_facets(
    preview_drafts: bool = Query(default=False),
    q: str | None = Query(default=None, max_length=120),
    category: str | None = Query(default=None, max_length=80),
    colour: str | None = Query(default=None, max_length=80),
    size: str | None = Query(default=None, max_length=12),
    min_price: float | None = Query(default=None, ge=0),
    max_price: float | None = Query(default=None, ge=0),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> dict:
    if preview_drafts and is_production(settings.environment):
        return {"categories": [], "colours": [], "sizes": [], "price": {"min": None, "max": None}}
    products = catalogue_service.filtered_products(
        db,
        preview=preview_drafts,
        **_filters(
            q=q,
            category=category,
            colour=colour,
            size=size,
            min_price=min_price,
            max_price=max_price,
        ),
    )
    return catalogue_service.facets(products)


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


@router.get("/catalogue/{slug}/stock", response_model=StockOut)
def get_stock(slug: str, db: Session = Depends(get_db)) -> dict:
    stock = stock_for_slug(db, slug)
    if stock is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return stock
