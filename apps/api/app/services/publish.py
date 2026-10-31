from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Product, ProductVariant

UNRESOLVED_MARKER = "[TO CONFIRM"
UNRESOLVED_RE = re.compile(r"\[TO CONFIRM", re.IGNORECASE)


class PublishBlocked(Exception):
    def __init__(self, fields: list[str]) -> None:
        self.fields = fields
        super().__init__("Product has unresolved fields: " + ", ".join(fields))


def is_unresolved(value: Any) -> bool:
    return isinstance(value, str) and bool(UNRESOLVED_RE.search(value))


def safe_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return str(value)
    return None if is_unresolved(value) else value


def _walk_unresolved(value: Any, path: str, out: list[str]) -> None:
    if isinstance(value, str):
        if is_unresolved(value):
            out.append(path)
        return
    if isinstance(value, dict):
        for key, child in value.items():
            _walk_unresolved(child, f"{path}.{key}" if path else str(key), out)
        return
    if isinstance(value, (list, tuple, set)):
        for index, child in enumerate(value):
            _walk_unresolved(child, f"{path}[{index}]", out)


def _unresolved_columns(obj: Any, prefix: str = "") -> list[str]:
    out: list[str] = []
    for column in obj.__table__.columns:
        if column.name in {"created_at", "updated_at"}:
            continue
        _walk_unresolved(getattr(obj, column.name), f"{prefix}{column.name}", out)
    return out


def product_unresolved_fields(product: Product) -> list[str]:
    fields = _unresolved_columns(product)
    for variant in product.variants:
        fields.extend(_unresolved_columns(variant, prefix=f"variants.{variant.sku}."))
    return sorted(set(fields))


def publish_product(db: Session, product: Product) -> Product:
    fields = product_unresolved_fields(product)
    if fields:
        raise PublishBlocked(fields)
    product.status = "published"
    db.commit()
    db.refresh(product)
    return product


def unpublish_product(db: Session, product: Product) -> Product:
    product.status = "draft"
    db.commit()
    db.refresh(product)
    return product


def _safe_list(values: Any) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    result: list[str] = []
    for value in values:
        text = safe_text(value)
        if text:
            result.append(text)
    return result


def _first_image(product: Product) -> str | None:
    images = product.images or []
    if not isinstance(images, list):
        return None
    for image in images:
        if isinstance(image, dict):
            filename = safe_text(image.get("filename"))
            if filename:
                return filename
    return None


def _available(variant: ProductVariant) -> int:
    if variant.inventory is None:
        return 0
    return max(variant.inventory.on_hand - variant.inventory.reserved, 0)


def to_public_product(product: Product, detail: bool = False) -> dict[str, Any] | None:
    """Return a storefront-safe product, or None if any flag remains.

    The publish guard should make this impossible. The check is defence in
    depth: a published row with an unresolved field is hidden, never rendered.
    """

    if product_unresolved_fields(product):
        return None

    summary = safe_text(product.summary_15w or product.short_description)
    category_name = safe_text(product.category.name) if product.category else None
    features = _safe_list(product.feature_bullets or product.features)[:5]

    payload: dict[str, Any] = {
        "id": product.id,
        "name": safe_text(product.name) or product.id,
        "slug": safe_text(product.slug) or product.id,
        "category": category_name or "Catalogue",
        "sub_category": safe_text(product.sub_category),
        "audience": safe_text(product.audience),
        "tier": product.tier,
        "tier_label": safe_text(product.tier_label),
        "colour": safe_text(product.colour) or "Colour pending",
        "colour_hex": safe_text(product.colour_hex) or "#D9CBB4",
        "price_inr": float(product.price_inr),
        "mrp_inr": float(product.mrp_inr),
        "summary": summary,
        "hero": product.hero,
        "image": _first_image(product),
        "features": features,
    }

    if not detail:
        return payload

    materials: dict[str, str] = {}
    for label, value in {
        "upper": product.upper_material,
        "lining": product.lining_material,
        "insole": product.insole_material,
        "midsole": product.midsole_material,
        "outsole": product.outsole_material,
    }.items():
        text = safe_text(value)
        if text:
            materials[label] = text

    sizes = []
    for variant in sorted(product.variants, key=lambda item: item.id):
        sizes.append(
            {
                "sku": variant.sku,
                "size_uk": variant.size_uk,
                "size_eu": safe_text(variant.size_eu),
                "size_us_men": safe_text(variant.size_us_men),
                "size_us_women": safe_text(variant.size_us_women),
                "foot_length_cm": float(variant.foot_length_cm)
                if variant.foot_length_cm is not None
                else None,
                "price_inr": float(variant.price_inr),
                "available": _available(variant),
            }
        )

    payload.update(
        {
            "description": safe_text(product.description_120w or product.long_description),
            "sizes": sizes,
            "materials": materials,
            "fit_notes": safe_text(product.fit_recommendation or product.fit_note),
            "care": safe_text(product.care),
            "seo_title": safe_text(product.seo_title),
            "seo_description": safe_text(product.seo_description),
        }
    )
    return payload


def public_products(db: Session) -> list[dict[str, Any]]:
    products = db.scalars(
        select(Product).where(Product.status == "published").order_by(Product.name)
    ).all()
    result: list[dict[str, Any]] = []
    for product in products:
        public = to_public_product(product)
        if public is not None:
            result.append(public)
    return result


def public_product(db: Session, slug: str) -> dict[str, Any] | None:
    product = db.scalar(
        select(Product).where(Product.slug == slug, Product.status == "published")
    )
    if product is None:
        return None
    return to_public_product(product, detail=True)


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def admin_product_payload(product: Product) -> dict[str, Any]:
    data = {
        column.name: _json_value(getattr(product, column.name))
        for column in product.__table__.columns
        if column.name not in {"created_at", "updated_at"}
    }
    return {
        "id": product.id,
        "name": product.name,
        "slug": product.slug,
        "status": product.status,
        "category": {
            "id": product.category.id,
            "name": product.category.name,
            "slug": product.category.slug,
            "code": product.category.code,
            "description": product.category.description,
            "sort_order": product.category.sort_order,
        },
        "price_inr": float(product.price_inr),
        "mrp_inr": float(product.mrp_inr),
        "colour": product.colour,
        "colour_hex": product.colour_hex,
        "tier": product.tier,
        "unresolved_fields": product_unresolved_fields(product),
        "data": data,
    }
