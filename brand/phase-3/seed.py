#!/usr/bin/env python3
"""Seed the Sāntvana catalogue into PostgreSQL with SQLAlchemy 2.0.

The script is idempotent: it upserts products and variants by primary key, so it
can be run more than once against a development database.

Usage:
    # Validate the JSON without touching a database
    python brand/phase-3/seed.py --dry-run

    # Create tables and seed a local PostgreSQL database
    $env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@localhost:5432/santvana"
    python brand/phase-3/seed.py --create-tables

    # Production: run Alembic first, then seed without --create-tables
    python brand/phase-3/seed.py

No database URL or password is hard-coded. DATABASE_URL is required unless
--database-url is passed explicitly.

The models here are a seed-time convenience. In the application, keep the
canonical models in the FastAPI app and import them in the Alembic migration.
"""

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
DEFAULT_JSON = ROOT / "products.json"
SKU_RE = re.compile(r"^[A-Z]{2}-[A-Z]{2,4}-[A-Z]{3}-UK(?:[3-9]|1[0-3])$")


def load_payload(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Catalogue JSON not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_payload(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    products = payload.get("products", [])
    if len(products) != 30:
        errors.append(f"expected 30 products, found {len(products)}")

    categories = {"Sneakers", "Running", "Everyday", "Sandals", "Boots"}
    if {product.get("category") for product in products} != categories:
        errors.append("expected exactly the five launch categories")

    tiers = {"good": 0, "better": 0, "best": 0}
    buckets = {"at_or_below_2500": 0, "above_2500": 0}
    skus: list[str] = []
    for product in products:
        pid = product.get("product_id", "<missing>")
        price = product.get("price_inr")
        rate = product.get("gst_rate")
        if not isinstance(price, int):
            errors.append(f"{pid}: price_inr must be an integer")
            continue
        expected_rate = 0.05 if price <= 2500 else 0.18
        if rate != expected_rate:
            errors.append(f"{pid}: gst_rate {rate} does not match price {price}")
        tiers[product.get("tier")] = tiers.get(product.get("tier"), 0) + 1
        bucket = "at_or_below_2500" if price <= 2500 else "above_2500"
        buckets[bucket] += 1
        variants = product.get("variants", [])
        if len(variants) != 11:
            errors.append(f"{pid}: expected 11 variants, found {len(variants)}")
        for variant in variants:
            sku = variant.get("sku", "")
            skus.append(sku)
            if not SKU_RE.match(sku):
                errors.append(f"{pid}: bad SKU {sku}")
    if tiers != {"good": 15, "better": 10, "best": 5}:
        errors.append(f"tier counts are {tiers}, expected 15/10/5")
    if buckets != {"at_or_below_2500": 15, "above_2500": 15}:
        errors.append(f"GST bucket counts are {buckets}, expected 15/15")
    if len(skus) != 330 or len(set(skus)) != 330:
        errors.append(f"expected 330 unique SKUs, found {len(skus)} rows / {len(set(skus))} unique")
    return errors


def build_models() -> tuple[Any, Any, Any]:
    """Import SQLAlchemy lazily so --dry-run works without it installed."""
    from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text, func
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

    class Base(DeclarativeBase):
        pass

    class Product(Base):
        __tablename__ = "products"

        id: Mapped[str] = mapped_column(String(32), primary_key=True)
        sku_prefix: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
        sku_pattern: Mapped[str] = mapped_column(String(32), nullable=False)
        name: Mapped[str] = mapped_column(String(80), nullable=False)
        slug: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
        category: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
        category_code: Mapped[str] = mapped_column(String(4), nullable=False)
        category_slug: Mapped[str] = mapped_column(String(32), nullable=False)
        tier: Mapped[str] = mapped_column(String(16), nullable=False, index=True)
        tier_label: Mapped[str] = mapped_column(String(16), nullable=False)
        model_code: Mapped[str] = mapped_column(String(16), nullable=False)
        colour: Mapped[str] = mapped_column(String(40), nullable=False)
        colour_code: Mapped[str] = mapped_column(String(8), nullable=False)
        colour_hex: Mapped[str] = mapped_column(String(9), nullable=False)
        silhouette: Mapped[str] = mapped_column(String(60), nullable=False)
        gender: Mapped[str] = mapped_column(String(16), nullable=False)
        age_group: Mapped[str] = mapped_column(String(16), nullable=False)
        season: Mapped[str] = mapped_column(String(24), nullable=False)
        drop: Mapped[str] = mapped_column(String(24), nullable=False)
        launch_date: Mapped[str] = mapped_column(String(64), nullable=False)
        status: Mapped[str] = mapped_column(String(24), nullable=False)
        name_status: Mapped[str] = mapped_column(String(120), nullable=False)
        price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
        mrp_inr: Mapped[int] = mapped_column(Integer, nullable=False)
        price_basis: Mapped[str] = mapped_column(String(40), nullable=False)
        gst_rate: Mapped[Any] = mapped_column(Numeric(4, 2), nullable=False)
        gst_rate_pct: Mapped[int] = mapped_column(Integer, nullable=False)
        gst_bucket: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
        gst_amount_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        net_revenue_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        target_landed_cost_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        cost_basis: Mapped[str] = mapped_column(String(80), nullable=False)
        gross_margin_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        gross_margin_pct: Mapped[Any] = mapped_column(Numeric(6, 2), nullable=False)
        margin_target_low_pct: Mapped[int] = mapped_column(Integer, nullable=False)
        margin_target_high_pct: Mapped[int] = mapped_column(Integer, nullable=False)
        margin_target_pct: Mapped[str] = mapped_column(String(16), nullable=False)
        discount_flip_threshold_pct: Mapped[Any | None] = mapped_column(Numeric(6, 2), nullable=True)
        discount_flip_note: Mapped[str] = mapped_column(Text, nullable=False)
        size_run: Mapped[str] = mapped_column(String(24), nullable=False)
        size_system: Mapped[str] = mapped_column(String(40), nullable=False)
        sku_count: Mapped[int] = mapped_column(Integer, nullable=False)
        hero: Mapped[bool] = mapped_column(Boolean, nullable=False, index=True)
        hero_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
        restock_priority: Mapped[str] = mapped_column(String(2), nullable=False)
        short_description: Mapped[str] = mapped_column(Text, nullable=False)
        long_description: Mapped[str] = mapped_column(Text, nullable=False)
        features: Mapped[Any] = mapped_column(JSON, nullable=False)
        tags: Mapped[Any] = mapped_column(JSON, nullable=False)
        seo_title: Mapped[str] = mapped_column(String(160), nullable=False)
        seo_description: Mapped[str] = mapped_column(Text, nullable=False)
        manufacturer: Mapped[str] = mapped_column(String(120), nullable=False)
        country_of_origin: Mapped[str] = mapped_column(String(120), nullable=False)
        upper_material: Mapped[str] = mapped_column(String(120), nullable=False)
        lining_material: Mapped[str] = mapped_column(String(120), nullable=False)
        insole_material: Mapped[str] = mapped_column(String(120), nullable=False)
        midsole_material: Mapped[str] = mapped_column(String(120), nullable=False)
        outsole_material: Mapped[str] = mapped_column(String(120), nullable=False)
        sole_compound: Mapped[str] = mapped_column(String(120), nullable=False)
        weight_g: Mapped[str] = mapped_column(String(80), nullable=False)
        lug_depth_mm: Mapped[str] = mapped_column(String(80), nullable=False)
        drop_mm: Mapped[str] = mapped_column(String(80), nullable=False)
        closure: Mapped[str] = mapped_column(String(80), nullable=False)
        heel_height_mm: Mapped[str] = mapped_column(String(80), nullable=False)
        toe_shape: Mapped[str] = mapped_column(String(120), nullable=False)
        last_width: Mapped[str] = mapped_column(String(120), nullable=False)
        water_resistance: Mapped[str] = mapped_column(String(120), nullable=False)
        fit_note: Mapped[str] = mapped_column(Text, nullable=False)
        fit_recommendation: Mapped[str] = mapped_column(Text, nullable=False)
        grip_claim: Mapped[str] = mapped_column(Text, nullable=False)
        test_claim: Mapped[str] = mapped_column(Text, nullable=False)
        care: Mapped[str] = mapped_column(Text, nullable=False)
        hsn: Mapped[str] = mapped_column(String(80), nullable=False)
        hsn_candidates: Mapped[Any] = mapped_column(JSON, nullable=False)
        legal_metrology: Mapped[str] = mapped_column(String(120), nullable=False)
        performance_claims: Mapped[Any] = mapped_column(JSON, nullable=False)
        claims: Mapped[Any] = mapped_column(JSON, nullable=False)
        images: Mapped[Any] = mapped_column(JSON, nullable=False)
        created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
        updated_at: Mapped[Any] = mapped_column(
            DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
        )

        variants = relationship(
            "ProductVariant",
            back_populates="product",
            cascade="all, delete-orphan",
            passive_deletes=True,
        )

    class ProductVariant(Base):
        __tablename__ = "product_variants"

        sku: Mapped[str] = mapped_column(String(32), primary_key=True)
        product_id: Mapped[str] = mapped_column(
            ForeignKey("products.id", ondelete="CASCADE"), nullable=False, index=True
        )
        size_uk: Mapped[str] = mapped_column(String(16), nullable=False)
        size_eu: Mapped[str] = mapped_column(String(16), nullable=False)
        size_us_men: Mapped[str] = mapped_column(String(16), nullable=False)
        size_us_women: Mapped[str] = mapped_column(String(16), nullable=False)
        foot_length_cm: Mapped[Any] = mapped_column(Numeric(4, 1), nullable=False)
        foot_length_cm_status: Mapped[str] = mapped_column(String(80), nullable=False)
        price_inr: Mapped[int] = mapped_column(Integer, nullable=False)
        gst_rate: Mapped[Any] = mapped_column(Numeric(4, 2), nullable=False)
        net_revenue_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        target_landed_cost_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        gross_margin_inr: Mapped[Any] = mapped_column(Numeric(10, 2), nullable=False)
        gross_margin_pct: Mapped[Any] = mapped_column(Numeric(6, 2), nullable=False)
        stock_status: Mapped[str] = mapped_column(String(24), nullable=False)
        created_at: Mapped[Any] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

        product = relationship("Product", back_populates="variants")

    return Base, Product, ProductVariant


def seed(payload: dict[str, Any], database_url: str, create_tables: bool) -> int:
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import Session
    except ImportError:
        print("SQLAlchemy is not installed. Install it with: pip install 'SQLAlchemy>=2.0'")
        return 1

    Base, Product, ProductVariant = build_models()
    engine = create_engine(database_url, future=True)
    if create_tables:
        Base.metadata.create_all(engine)

    product_count = 0
    variant_count = 0
    with Session(engine) as session:
        for product in payload["products"]:
            product_data = {key: value for key, value in product.items() if key != "variants"}
            product_data["id"] = product_data.pop("product_id")
            session.merge(Product(**product_data))
            session.flush()
            product_count += 1
            for variant in product["variants"]:
                variant_data = dict(variant)
                variant_data["product_id"] = product_data["id"]
                variant_data["foot_length_cm"] = float(variant_data["foot_length_cm"])
                session.merge(ProductVariant(**variant_data))
                variant_count += 1
        session.commit()

    print(f"Seeded {product_count} products and {variant_count} variants.")
    print("Tables: products, product_variants. Run Alembic in production; use --create-tables only in development.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed the Sāntvana Phase 3 catalogue.")
    parser.add_argument("--json", type=Path, default=DEFAULT_JSON, help="Path to products.json")
    parser.add_argument("--database-url", default=None, help="SQLAlchemy database URL; defaults to DATABASE_URL")
    parser.add_argument("--create-tables", action="store_true", help="Create tables before seeding (development only)")
    parser.add_argument("--dry-run", action="store_true", help="Validate the JSON without a database")
    args = parser.parse_args()

    payload = load_payload(args.json)
    errors = validate_payload(payload)
    if errors:
        print(f"FAIL: {len(errors)} catalogue validation error(s)")
        for error in errors[:40]:
            print(f"- {error}")
        return 1

    if args.dry_run:
        print("PASS: catalogue JSON is valid; no database connection made.")
        print("30 products, 330 SKUs, 15 at/below ₹2,500 and 15 above.")
        print("Set DATABASE_URL or pass --database-url to seed.")
        return 0

    database_url = args.database_url or os.environ.get("DATABASE_URL")
    if not database_url:
        parser.error("Set DATABASE_URL (for example: postgresql+psycopg://user:pass@localhost:5432/santvana) or pass --database-url.")

    return seed(payload, database_url, args.create_tables)


if __name__ == "__main__":
    raise SystemExit(main())
