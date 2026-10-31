from __future__ import annotations

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.models import Category, Inventory, Product, ProductVariant


def make_category(session: Session, **overrides: Any) -> Category:
    values = {
        "name": "Sneakers",
        "slug": "sneakers",
        "code": "SN",
        "sort_order": 0,
    }
    values.update(overrides)
    category = Category(**values)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


def make_product(session: Session, category: Category, **overrides: Any) -> Product:
    values = {
        "id": "TEST-001",
        "sku_prefix": "TEST-001",
        "name": "Test Product",
        "slug": "test-product",
        "category_id": category.id,
        "colour": "Chalk",
        "colour_hex": "#E9E4D8",
        "tier": "good",
        "tier_label": "Good",
        "price_inr": Decimal("2299.00"),
        "mrp_inr": Decimal("2299.00"),
        "short_description": "A clean test product.",
        "status": "draft",
    }
    values.update(overrides)
    product = Product(**values)
    session.add(product)
    session.commit()
    session.refresh(product)
    return product


def make_variant(
    session: Session,
    product: Product,
    *,
    sku: str = "TEST-001-UK7",
    on_hand: int = 0,
    reserved: int = 0,
    **overrides: Any,
) -> ProductVariant:
    values = {
        "product_id": product.id,
        "sku": sku,
        "size_uk": "UK 7",
        "size_eu": "EU 40",
        "size_us_men": "US 8",
        "size_us_women": "US 10",
        "price_inr": Decimal("2299.00"),
        "launch_stock_qty": 0,
        "stock_status": "not_allocated",
    }
    values.update(overrides)
    variant = ProductVariant(**values)
    session.add(variant)
    session.flush()
    session.add(
        Inventory(
            variant_id=variant.id,
            on_hand=on_hand,
            reserved=reserved,
            version=0,
        )
    )
    session.commit()
    session.refresh(variant)
    return variant
