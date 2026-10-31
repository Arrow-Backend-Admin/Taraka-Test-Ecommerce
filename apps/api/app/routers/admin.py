from __future__ import annotations

import secrets
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..config import Settings, get_settings
from ..db import get_db
from ..models import Category, Inventory, InventoryEvent, Product, ProductVariant
from ..schemas import (
    AdminProductSummary,
    CategoryCreate,
    CategoryOut,
    CategoryUpdate,
    InventoryAdjust,
    ProductCreate,
    ProductUpdate,
    PublishResult,
    VariantCreate,
    VariantUpdate,
)
from ..services.inventory import (
    InventoryNotFound,
    OutOfStock,
    adjust_stock,
    get_inventory_by_sku,
    list_events,
)
from ..services.publish import (
    PublishBlocked,
    admin_product_payload,
    product_unresolved_fields,
    publish_product,
    unpublish_product,
)


def require_admin(
    authorization: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if not settings.admin_api_token:
        raise HTTPException(
            status_code=503,
            detail="Admin API disabled. Set ADMIN_API_TOKEN in the API environment.",
        )
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if not secrets.compare_digest(token, settings.admin_api_token):
        raise HTTPException(status_code=401, detail="Invalid bearer token")


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

PRODUCT_COLUMNS = {column.name for column in Product.__table__.columns}
VARIANT_COLUMNS = {column.name for column in ProductVariant.__table__.columns}


def _commit(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=409, detail="Database constraint failed") from exc


def _get_category(db: Session, slug: str) -> Category:
    category = db.scalar(select(Category).where(Category.slug == slug))
    if category is None:
        raise HTTPException(status_code=404, detail=f"Category {slug} not found")
    return category


def _get_product(db: Session, product_id: str) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product {product_id} not found")
    return product


def _get_variant(db: Session, sku: str) -> ProductVariant:
    variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    if variant is None:
        raise HTTPException(status_code=404, detail=f"Variant {sku} not found")
    return variant


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _variant_payload(variant: ProductVariant) -> dict[str, Any]:
    inventory = variant.inventory
    return {
        "id": variant.id,
        "product_id": variant.product_id,
        "sku": variant.sku,
        "size_uk": variant.size_uk,
        "size_eu": variant.size_eu,
        "size_us_men": variant.size_us_men,
        "size_us_women": variant.size_us_women,
        "foot_length_cm": _json_value(variant.foot_length_cm),
        "foot_length_cm_status": variant.foot_length_cm_status,
        "price_inr": _json_value(variant.price_inr),
        "gst_rate": _json_value(variant.gst_rate),
        "net_revenue_inr": _json_value(variant.net_revenue_inr),
        "target_landed_cost_inr": _json_value(variant.target_landed_cost_inr),
        "gross_margin_inr": _json_value(variant.gross_margin_inr),
        "gross_margin_pct": _json_value(variant.gross_margin_pct),
        "launch_stock_qty": variant.launch_stock_qty,
        "launch_stock_status": variant.launch_stock_status,
        "stock_status": variant.stock_status,
        "inventory": {
            "on_hand": inventory.on_hand if inventory else 0,
            "reserved": inventory.reserved if inventory else 0,
            "available": max((inventory.on_hand - inventory.reserved), 0)
            if inventory
            else 0,
            "version": inventory.version if inventory else 0,
        },
    }


def _inventory_payload(variant: ProductVariant, inventory: Inventory) -> dict[str, Any]:
    return {
        "sku": variant.sku,
        "on_hand": inventory.on_hand,
        "reserved": inventory.reserved,
        "available": max(inventory.on_hand - inventory.reserved, 0),
        "version": inventory.version,
    }


def _event_payload(event: InventoryEvent) -> dict[str, Any]:
    return {
        "id": event.id,
        "variant_id": event.variant_id,
        "event_type": event.event_type,
        "quantity_delta": event.quantity_delta,
        "reference": event.reference,
        "note": event.note,
        "created_at": event.created_at.isoformat() if event.created_at else None,
    }


@router.get("/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return list(
        db.scalars(select(Category).order_by(Category.sort_order, Category.name)).all()
    )


@router.post("/categories", response_model=CategoryOut, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    category = Category(**payload.model_dump())
    db.add(category)
    _commit(db)
    db.refresh(category)
    return category


@router.get("/categories/{slug}", response_model=CategoryOut)
def get_category(slug: str, db: Session = Depends(get_db)) -> Category:
    return _get_category(db, slug)


@router.patch("/categories/{slug}", response_model=CategoryOut)
def update_category(
    slug: str, payload: CategoryUpdate, db: Session = Depends(get_db)
) -> Category:
    category = _get_category(db, slug)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    _commit(db)
    db.refresh(category)
    return category


@router.delete("/categories/{slug}", status_code=204)
def delete_category(slug: str, db: Session = Depends(get_db)) -> None:
    category = _get_category(db, slug)
    if category.products:
        raise HTTPException(status_code=409, detail="Category still has products")
    db.delete(category)
    _commit(db)


@router.get("/products", response_model=list[AdminProductSummary])
def list_products(
    status_filter: str | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    statement = select(Product).order_by(Product.name)
    if status_filter:
        statement = statement.where(Product.status == status_filter)
    products = db.scalars(statement).all()
    return [
        {
            "id": product.id,
            "name": product.name,
            "slug": product.slug,
            "status": product.status,
            "category": product.category.name,
            "price_inr": float(product.price_inr),
            "variant_count": len(product.variants),
            "unresolved_count": len(product_unresolved_fields(product)),
        }
        for product in products
    ]


@router.post("/products", status_code=201)
def create_product(
    payload: ProductCreate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    data = payload.model_dump()
    category_slug = data.pop("category_slug")
    data.pop("status", None)
    data = {key: value for key, value in data.items() if key in PRODUCT_COLUMNS}
    category = _get_category(db, category_slug)
    product = Product(category_id=category.id, status="draft", **data)
    db.add(product)
    _commit(db)
    db.refresh(product)
    return admin_product_payload(product)


@router.get("/products/{product_id}")
def get_product(product_id: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    return admin_product_payload(_get_product(db, product_id))


@router.patch("/products/{product_id}")
def update_product(
    product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    product = _get_product(db, product_id)
    data = payload.model_dump(exclude_unset=True)
    category_slug = data.pop("category_slug", None)

    for forbidden in ("id", "status", "created_at", "updated_at"):
        if forbidden in data:
            raise HTTPException(
                status_code=400,
                detail=f"{forbidden} cannot be changed here; use the publish endpoints",
            )

    data = {key: value for key, value in data.items() if key in PRODUCT_COLUMNS}
    if category_slug:
        product.category_id = _get_category(db, category_slug).id
    for key, value in data.items():
        setattr(product, key, value)

    if product.status == "published":
        unresolved = product_unresolved_fields(product)
        if unresolved:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Unpublish before adding unresolved fields",
                    "unresolved_fields": unresolved,
                },
            )

    _commit(db)
    db.refresh(product)
    return admin_product_payload(product)


@router.delete("/products/{product_id}", status_code=204)
def delete_product(product_id: str, db: Session = Depends(get_db)) -> None:
    product = _get_product(db, product_id)
    if product.status == "published":
        raise HTTPException(status_code=409, detail="Unpublish before deleting")
    db.delete(product)
    _commit(db)


@router.post("/products/{product_id}/publish", response_model=PublishResult)
def publish(product_id: str, db: Session = Depends(get_db)) -> PublishResult:
    product = _get_product(db, product_id)
    try:
        publish_product(db, product)
    except PublishBlocked as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Product has unresolved fields",
                "unresolved_fields": exc.fields,
            },
        ) from exc
    return PublishResult(
        id=product.id,
        status=product.status,
        unresolved_fields=product_unresolved_fields(product),
    )


@router.post("/products/{product_id}/unpublish", response_model=PublishResult)
def unpublish(product_id: str, db: Session = Depends(get_db)) -> PublishResult:
    product = _get_product(db, product_id)
    unpublish_product(db, product)
    return PublishResult(
        id=product.id,
        status=product.status,
        unresolved_fields=product_unresolved_fields(product),
    )


@router.get("/products/{product_id}/variants")
def list_variants(
    product_id: str, db: Session = Depends(get_db)
) -> list[dict[str, Any]]:
    product = _get_product(db, product_id)
    return [_variant_payload(variant) for variant in product.variants]


@router.post("/products/{product_id}/variants", status_code=201)
def create_variant(
    product_id: str, payload: VariantCreate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    product = _get_product(db, product_id)
    data = payload.model_dump()
    data.pop("product_id", None)
    data = {key: value for key, value in data.items() if key in VARIANT_COLUMNS}
    variant = ProductVariant(product=product, **data)
    db.add(variant)

    if product.status == "published":
        unresolved = product_unresolved_fields(product)
        if unresolved:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Unpublish before adding a variant with unresolved fields",
                    "unresolved_fields": unresolved,
                },
            )

    inventory = Inventory(
        variant=variant,
        on_hand=variant.launch_stock_qty,
        reserved=0,
        version=0,
    )
    db.add(inventory)
    db.add(
        InventoryEvent(
            variant=variant,
            event_type="seed",
            quantity_delta=variant.launch_stock_qty,
            reference=f"admin:{variant.sku}:initial",
            note="Admin variant creation; launch stock loaded into inventory.",
        )
    )
    _commit(db)
    db.refresh(variant)
    return _variant_payload(variant)


@router.patch("/variants/{sku}")
def update_variant(
    sku: str, payload: VariantUpdate, db: Session = Depends(get_db)
) -> dict[str, Any]:
    variant = _get_variant(db, sku)
    data = payload.model_dump(exclude_unset=True)

    if "sku" in data and data["sku"] != variant.sku:
        raise HTTPException(status_code=400, detail="SKU cannot be changed")
    for forbidden in ("id", "product_id", "sku", "created_at", "updated_at"):
        data.pop(forbidden, None)
    data = {key: value for key, value in data.items() if key in VARIANT_COLUMNS}

    new_launch_stock = data.pop("launch_stock_qty", None)
    if new_launch_stock is not None:
        inventory = variant.inventory
        if inventory is None:
            inventory = Inventory(variant=variant, on_hand=0, reserved=0, version=0)
            db.add(inventory)
        if new_launch_stock < inventory.reserved:
            raise HTTPException(
                status_code=409,
                detail="Launch stock cannot be below reserved units",
            )
        delta = new_launch_stock - inventory.on_hand
        inventory.on_hand = new_launch_stock
        inventory.version += 1
        if delta:
            db.add(
                InventoryEvent(
                    variant=variant,
                    event_type="adjustment",
                    quantity_delta=delta,
                    reference=None,
                    note="Admin launch stock update",
                )
            )
        variant.launch_stock_qty = new_launch_stock

    for key, value in data.items():
        setattr(variant, key, value)

    if variant.product.status == "published":
        unresolved = product_unresolved_fields(variant.product)
        if unresolved:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail={
                    "message": "Unpublish before adding unresolved fields",
                    "unresolved_fields": unresolved,
                },
            )

    _commit(db)
    db.refresh(variant)
    return _variant_payload(variant)


@router.delete("/variants/{sku}", status_code=204)
def delete_variant(sku: str, db: Session = Depends(get_db)) -> None:
    variant = _get_variant(db, sku)
    if variant.product.status == "published":
        raise HTTPException(status_code=409, detail="Unpublish before deleting a variant")
    if variant.inventory and variant.inventory.reserved:
        raise HTTPException(status_code=409, detail="Release reservations before deleting")
    db.delete(variant)
    _commit(db)


@router.get("/inventory/{sku}")
def get_inventory(sku: str, db: Session = Depends(get_db)) -> dict[str, Any]:
    variant = _get_variant(db, sku)
    try:
        inventory = get_inventory_by_sku(db, sku)
    except InventoryNotFound as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _inventory_payload(variant, inventory)


@router.post("/inventory/{sku}/adjust")
def adjust_inventory(
    sku: str, payload: InventoryAdjust, db: Session = Depends(get_db)
) -> dict[str, Any]:
    variant = _get_variant(db, sku)
    try:
        inventory = adjust_stock(
            db,
            variant.id,
            payload.quantity_delta,
            note=payload.note,
        )
    except (InventoryNotFound, OutOfStock, ValueError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return _inventory_payload(variant, inventory)


@router.get("/inventory/{sku}/events")
def inventory_events(sku: str, db: Session = Depends(get_db)) -> list[dict[str, Any]]:
    variant = _get_variant(db, sku)
    return [_event_payload(event) for event in list_events(db, variant.id)]
