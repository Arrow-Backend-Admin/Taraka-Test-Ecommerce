from __future__ import annotations

import json
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import Category, Inventory, InventoryEvent, Product, ProductVariant
from .services.publish import UNRESOLVED_RE

DEFAULT_CATALOGUE = Path(__file__).resolve().parents[3] / "brand" / "phase-3" / "products.json"
DEFAULT_AUDIENCE = "Urban India, 22–34, unisex"


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float, Decimal)):
        return Decimal(str(value))
    if isinstance(value, str):
        try:
            return Decimal(value.strip())
        except InvalidOperation:
            return None
    return None


def _integer(value: Any) -> int | None:
    number = _decimal(value)
    if number is None:
        return None
    return int(number)


def _unresolved_status(value: Any) -> str | None:
    if isinstance(value, str) and UNRESOLVED_RE.search(value):
        return value
    return None


def _launch_date(value: Any) -> tuple[date | None, str | None]:
    if isinstance(value, str):
        try:
            return date.fromisoformat(value), None
        except ValueError:
            return None, value if UNRESOLVED_RE.search(value) else None
    return None, None


def _safe_feature_bullets(features: Any) -> list[str]:
    if not isinstance(features, list):
        return []
    return [
        feature
        for feature in features
        if isinstance(feature, str) and not UNRESOLVED_RE.search(feature)
    ][:5]


def _upsert_category(
    session: Session, slug: str, name: str, code: str, sort_order: int
) -> Category:
    category = session.scalar(select(Category).where(Category.slug == slug))
    if category is None:
        category = Category(name=name, slug=slug, code=code, sort_order=sort_order)
        session.add(category)
    else:
        category.name = name
        category.code = code
        category.sort_order = sort_order
    session.flush()
    return category


def _product_values(item: dict[str, Any], category_id: int) -> dict[str, Any]:
    launch_date, launch_date_note = _launch_date(item.get("launch_date"))
    features = item.get("features") or []
    colourways = item.get("colourways")
    if not colourways:
        colourways = [{"name": item["colour"], "hex": item["colour_hex"]}]

    return {
        "sku_prefix": item["sku_prefix"],
        "sku_pattern": item.get("sku_pattern"),
        "name": item["name"],
        "slug": item["slug"],
        "category_id": category_id,
        "sub_category": item.get("sub_category"),
        "audience": item.get("audience") or DEFAULT_AUDIENCE,
        "tier": item.get("tier", "good"),
        "tier_label": item.get("tier_label"),
        "model_code": item.get("model_code"),
        "colour": item["colour"],
        "colour_code": item.get("colour_code"),
        "colour_hex": item["colour_hex"],
        "colourways": colourways,
        "silhouette": item.get("silhouette"),
        "gender": item.get("gender"),
        "age_group": item.get("age_group"),
        "season": item.get("season"),
        "drop": item.get("drop"),
        "launch_date": launch_date,
        "launch_date_note": launch_date_note,
        "name_status": item.get("name_status"),
        "price_inr": _decimal(item["price_inr"]),
        "mrp_inr": _decimal(item["mrp_inr"]),
        "sale_price_inr": _decimal(item.get("sale_price_inr")),
        "price_basis": item.get("price_basis"),
        "gst_rate": _decimal(item.get("gst_rate")),
        "gst_rate_pct": _integer(item.get("gst_rate_pct")),
        "gst_bucket": item.get("gst_bucket"),
        "gst_amount_inr": _decimal(item.get("gst_amount_inr")),
        "net_revenue_inr": _decimal(item.get("net_revenue_inr")),
        "target_landed_cost_inr": _decimal(item.get("target_landed_cost_inr")),
        "cost_basis": item.get("cost_basis"),
        "gross_margin_inr": _decimal(item.get("gross_margin_inr")),
        "gross_margin_pct": _decimal(item.get("gross_margin_pct")),
        "margin_target_low_pct": _decimal(item.get("margin_target_low_pct")),
        "margin_target_high_pct": _decimal(item.get("margin_target_high_pct")),
        "margin_target_pct": item.get("margin_target_pct"),
        "discount_flip_threshold_pct": _decimal(item.get("discount_flip_threshold_pct")),
        "discount_flip_note": item.get("discount_flip_note"),
        "hsn": item.get("hsn"),
        "hsn_candidates": item.get("hsn_candidates") or [],
        "legal_metrology": item.get("legal_metrology"),
        "size_run": item.get("size_run"),
        "size_system": item.get("size_system"),
        "sku_count": _integer(item.get("sku_count")),
        "hero": bool(item.get("hero")),
        "hero_reason": item.get("hero_reason"),
        "restock_priority": item.get("restock_priority"),
        "summary_15w": item.get("summary_15w"),
        "description_120w": item.get("description_120w"),
        "short_description": item.get("short_description"),
        "long_description": item.get("long_description"),
        "features": features,
        "feature_bullets": item.get("feature_bullets") or _safe_feature_bullets(features),
        "tags": item.get("tags") or [],
        "seo_title": item.get("seo_title"),
        "seo_description": item.get("seo_description"),
        "manufacturer": item.get("manufacturer"),
        "country_of_origin": item.get("country_of_origin"),
        "upper_material": item.get("upper_material"),
        "lining_material": item.get("lining_material"),
        "insole_material": item.get("insole_material"),
        "midsole_material": item.get("midsole_material"),
        "outsole_material": item.get("outsole_material"),
        "sole_compound": item.get("sole_compound"),
        "weight_g": _integer(item.get("weight_g")),
        "weight_g_status": _unresolved_status(item.get("weight_g")),
        "lug_depth_mm": _decimal(item.get("lug_depth_mm")),
        "lug_depth_mm_status": _unresolved_status(item.get("lug_depth_mm")),
        "drop_mm": _integer(item.get("drop_mm")),
        "drop_mm_status": _unresolved_status(item.get("drop_mm")),
        "closure": item.get("closure"),
        "heel_height_mm": _integer(item.get("heel_height_mm")),
        "heel_height_mm_status": _unresolved_status(item.get("heel_height_mm")),
        "toe_shape": item.get("toe_shape"),
        "last_width": item.get("last_width"),
        "water_resistance": item.get("water_resistance"),
        "fit_note": item.get("fit_note"),
        "fit_recommendation": item.get("fit_recommendation"),
        "grip_claim": item.get("grip_claim"),
        "test_claim": item.get("test_claim"),
        "care": item.get("care"),
        "performance_claims": item.get("performance_claims") or [],
        "claims": item.get("claims") or [],
        "images": item.get("images") or [],
    }


def _variant_values(item: dict[str, Any], *, creating: bool) -> dict[str, Any]:
    values = {
        "size_uk": item["size_uk"],
        "size_eu": item.get("size_eu"),
        "size_us_men": item.get("size_us_men"),
        "size_us_women": item.get("size_us_women"),
        "foot_length_cm": _decimal(item.get("foot_length_cm")),
        "foot_length_cm_status": item.get("foot_length_cm_status"),
        "price_inr": _decimal(item["price_inr"]),
        "gst_rate": _decimal(item.get("gst_rate")),
        "net_revenue_inr": _decimal(item.get("net_revenue_inr")),
        "target_landed_cost_inr": _decimal(item.get("target_landed_cost_inr")),
        "gross_margin_inr": _decimal(item.get("gross_margin_inr")),
        "gross_margin_pct": _decimal(item.get("gross_margin_pct")),
        "stock_status": item.get("stock_status"),
    }
    if creating:
        values["launch_stock_qty"] = _integer(item.get("launch_stock_qty")) or 0
        values["launch_stock_status"] = (
            item.get("launch_stock_status") or "[TO CONFIRM: founder]"
        )
    return values


def seed_catalogue(session: Session, catalogue_path: str | Path | None = None) -> dict[str, int]:
    path = Path(catalogue_path) if catalogue_path else DEFAULT_CATALOGUE
    payload = json.loads(path.read_text(encoding="utf-8"))
    products = payload.get("products")
    if not isinstance(products, list) or not products:
        raise ValueError(f"No products found in {path}")

    category_order: dict[str, int] = {}
    for item in products:
        slug = item["category_slug"]
        if slug not in category_order:
            category_order[slug] = len(category_order)

    counts = {"categories": 0, "products": 0, "variants": 0, "inventory": 0}
    try:
        for item in products:
            category = _upsert_category(
                session,
                item["category_slug"],
                item["category"],
                item["category_code"],
                category_order[item["category_slug"]],
            )
            counts["categories"] = len(
                session.scalars(select(Category.id)).all()
            )

            product = session.get(Product, item["product_id"])
            creating = product is None
            if product is None:
                product = Product(id=item["product_id"], status="draft")
                session.add(product)
            for key, value in _product_values(item, category.id).items():
                setattr(product, key, value)
            session.flush()
            counts["products"] += 1

            for variant_item in item.get("variants", []):
                variant = session.scalar(
                    select(ProductVariant).where(ProductVariant.sku == variant_item["sku"])
                )
                variant_creating = variant is None
                if variant is None:
                    variant = ProductVariant(
                        sku=variant_item["sku"], product_id=product.id
                    )
                    session.add(variant)
                for key, value in _variant_values(
                    variant_item, creating=variant_creating
                ).items():
                    setattr(variant, key, value)
                session.flush()
                counts["variants"] += 1

                if variant.inventory is None:
                    inventory = Inventory(
                        variant=variant,
                        on_hand=variant.launch_stock_qty,
                        reserved=0,
                        version=0,
                    )
                    session.add(inventory)
                    counts["inventory"] += 1

                reference = f"seed:{variant.sku}"
                exists = session.scalar(
                    select(InventoryEvent.id).where(InventoryEvent.reference == reference)
                )
                if exists is None:
                    session.add(
                        InventoryEvent(
                            variant=variant,
                            event_type="seed",
                            quantity_delta=0,
                            reference=reference,
                            note="Phase 3 catalogue seed; launch stock is not allocated.",
                        )
                    )
        session.commit()
    except Exception:
        session.rollback()
        raise
    return counts
