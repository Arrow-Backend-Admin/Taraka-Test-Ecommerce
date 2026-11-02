"""Catalogue filtering, faceting and search.

PostgreSQL uses native full-text search (``to_tsvector`` / ``plainto_tsquery``).
SQLite, which the test suite and local fallback use, gets a case-insensitive
substring search across the same fields. Both paths share the same filters.
"""

from __future__ import annotations

import re
from collections import Counter
from decimal import Decimal
from typing import Any

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, joinedload

from ..models import Category, Product, ProductVariant
from .publish import (
    is_production,
    product_has_placeholder_image,
    to_preview_product,
    to_public_product,
)

SEARCH_FIELDS = (
    "name",
    "sub_category",
    "colour",
    "short_description",
    "long_description",
)


def _text_document() -> Any:
    parts = [func.coalesce(getattr(Product, field), "") for field in SEARCH_FIELDS]
    document = parts[0]
    for part in parts[1:]:
        document = document + " " + part
    return func.to_tsvector("english", document)


def _search_filter(db: Session, query: str) -> Any:
    dialect = db.get_bind().dialect.name
    if dialect == "postgresql":
        return _text_document().op("@@")(func.plainto_tsquery("english", query))
    pattern = f"%{query}%"
    clauses = [getattr(Product, field).ilike(pattern) for field in SEARCH_FIELDS]
    return or_(*clauses)


def _base_query(*, preview: bool) -> Any:
    statement = select(Product).options(
        joinedload(Product.category),
        joinedload(Product.variants).joinedload(ProductVariant.inventory),
    )
    if not preview:
        statement = statement.where(Product.status == "published")
    return statement


def filtered_products(
    db: Session,
    *,
    preview: bool = False,
    query: str | None = None,
    category: str | None = None,
    colour: str | None = None,
    size: str | None = None,
    min_price: Decimal | None = None,
    max_price: Decimal | None = None,
) -> list[Product]:
    statement = _base_query(preview=preview)
    if category:
        statement = statement.join(Product.category).where(Category.slug == category)
    if colour:
        statement = statement.where(func.lower(Product.colour) == colour.strip().lower())
    if size:
        statement = statement.where(
            Product.variants.any(ProductVariant.size_uk == size.strip())
        )
    if min_price is not None:
        statement = statement.where(Product.price_inr >= min_price)
    if max_price is not None:
        statement = statement.where(Product.price_inr <= max_price)
    if query and query.strip():
        statement = statement.where(_search_filter(db, query.strip()))
        if db.get_bind().dialect.name == "postgresql":
            statement = statement.order_by(
                func.ts_rank(
                    _text_document(), func.plainto_tsquery("english", query.strip())
                ).desc(),
                Product.name,
            )
        else:
            statement = statement.order_by(Product.name)
    else:
        statement = statement.order_by(Product.name)
    return list(db.scalars(statement).unique().all())


def serialise(
    db: Session, products: list[Product], *, preview: bool, environment: str | None
) -> list[dict[str, Any]]:
    if preview and is_production(environment):
        return []
    result: list[dict[str, Any]] = []
    production = is_production(environment)
    for product in products:
        if not preview and production and product_has_placeholder_image(product):
            continue
        payload = (
            to_preview_product(product)
            if preview
            else to_public_product(product)
        )
        if payload is not None:
            result.append(payload)
    return result


def facets(products: list[Product]) -> dict[str, Any]:
    category_counts: Counter[tuple[str, str]] = Counter()
    colour_counts: Counter[tuple[str, str]] = Counter()
    size_counts: Counter[str] = Counter()
    prices: list[Decimal] = []
    for product in products:
        if product.category is not None:
            category_counts[(product.category.slug, product.category.name)] += 1
        colour_counts[(product.colour, product.colour_hex)] += 1
        prices.append(product.price_inr)
        for variant in product.variants:
            inventory = variant.inventory
            available = (
                max(inventory.on_hand - inventory.reserved, 0) if inventory else 0
            )
            if available > 0:
                size_counts[variant.size_uk] += 1

    def size_key(value: str) -> tuple[float, str]:
        match = re.search(r"\d+(?:\.\d+)?", value)
        if match is None:
            return (999.0, value)
        return (float(match.group()), value)

    return {
        "categories": [
            {"value": slug, "label": label, "count": count}
            for (slug, label), count in sorted(
                category_counts.items(), key=lambda item: (-item[1], item[0][1])
            )
        ],
        "colours": [
            {"value": name, "hex": hex_value, "count": count}
            for (name, hex_value), count in sorted(
                colour_counts.items(), key=lambda item: (-item[1], item[0][0])
            )
        ],
        "sizes": [
            {"value": value, "count": count}
            for value, count in sorted(size_counts.items(), key=lambda item: size_key(item[0]))
        ],
        "price": {
            "min": float(min(prices)) if prices else None,
            "max": float(max(prices)) if prices else None,
        },
    }
