from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Category(TimestampMixin, Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    products: Mapped[list[Product]] = relationship(back_populates="category")


class Product(TimestampMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint(
            "status IN ('draft', 'published', 'archived')",
            name="ck_products_status",
        ),
        CheckConstraint("price_inr >= 0", name="ck_products_price_non_negative"),
        CheckConstraint("mrp_inr >= 0", name="ck_products_mrp_non_negative"),
    )

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    sku_prefix: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    sku_pattern: Mapped[str | None] = mapped_column(String(64))
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), unique=True, index=True, nullable=False)
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False
    )

    sub_category: Mapped[str | None] = mapped_column(String(120))
    audience: Mapped[str | None] = mapped_column(String(200))
    tier: Mapped[str] = mapped_column(String(20), default="good", nullable=False)
    tier_label: Mapped[str | None] = mapped_column(String(40))
    model_code: Mapped[str | None] = mapped_column(String(20))
    colour: Mapped[str] = mapped_column(String(80), nullable=False)
    colour_code: Mapped[str | None] = mapped_column(String(20))
    colour_hex: Mapped[str] = mapped_column(String(7), nullable=False)
    colourways: Mapped[list | None] = mapped_column(JSON, default=list)
    silhouette: Mapped[str | None] = mapped_column(String(120))
    gender: Mapped[str | None] = mapped_column(String(40))
    age_group: Mapped[str | None] = mapped_column(String(40))
    season: Mapped[str | None] = mapped_column(String(40))
    drop: Mapped[str | None] = mapped_column(String(40))
    launch_date: Mapped[date | None] = mapped_column(Date)
    launch_date_note: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(20), default="draft", index=True, nullable=False)
    name_status: Mapped[str | None] = mapped_column(String(160))

    price_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    mrp_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    sale_price_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    price_basis: Mapped[str | None] = mapped_column(String(200))
    gst_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    gst_rate_pct: Mapped[int | None] = mapped_column(Integer)
    gst_bucket: Mapped[str | None] = mapped_column(String(32))
    gst_amount_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    net_revenue_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    target_landed_cost_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    cost_basis: Mapped[str | None] = mapped_column(String(200))
    gross_margin_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gross_margin_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    margin_target_low_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    margin_target_high_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    margin_target_pct: Mapped[str | None] = mapped_column(String(40))
    discount_flip_threshold_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    discount_flip_note: Mapped[str | None] = mapped_column(Text)

    hsn: Mapped[str | None] = mapped_column(String(20))
    hsn_candidates: Mapped[list | None] = mapped_column(JSON, default=list)
    legal_metrology: Mapped[str | None] = mapped_column(String(200))

    size_run: Mapped[str | None] = mapped_column(String(80))
    size_system: Mapped[str | None] = mapped_column(String(120))
    sku_count: Mapped[int | None] = mapped_column(Integer)
    hero: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    hero_reason: Mapped[str | None] = mapped_column(Text)
    restock_priority: Mapped[str | None] = mapped_column(String(8))

    summary_15w: Mapped[str | None] = mapped_column(String(400))
    description_120w: Mapped[str | None] = mapped_column(Text)
    short_description: Mapped[str | None] = mapped_column(Text)
    long_description: Mapped[str | None] = mapped_column(Text)
    features: Mapped[list | None] = mapped_column(JSON, default=list)
    feature_bullets: Mapped[list | None] = mapped_column(JSON, default=list)
    tags: Mapped[list | None] = mapped_column(JSON, default=list)
    seo_title: Mapped[str | None] = mapped_column(String(120))
    seo_description: Mapped[str | None] = mapped_column(String(320))

    manufacturer: Mapped[str | None] = mapped_column(String(200))
    country_of_origin: Mapped[str | None] = mapped_column(String(120))
    upper_material: Mapped[str | None] = mapped_column(String(200))
    lining_material: Mapped[str | None] = mapped_column(String(200))
    insole_material: Mapped[str | None] = mapped_column(String(200))
    midsole_material: Mapped[str | None] = mapped_column(String(200))
    outsole_material: Mapped[str | None] = mapped_column(String(200))
    sole_compound: Mapped[str | None] = mapped_column(String(200))
    weight_g: Mapped[int | None] = mapped_column(Integer)
    weight_g_status: Mapped[str | None] = mapped_column(String(120))
    lug_depth_mm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    lug_depth_mm_status: Mapped[str | None] = mapped_column(String(120))
    drop_mm: Mapped[int | None] = mapped_column(Integer)
    drop_mm_status: Mapped[str | None] = mapped_column(String(120))
    closure: Mapped[str | None] = mapped_column(String(120))
    heel_height_mm: Mapped[int | None] = mapped_column(Integer)
    heel_height_mm_status: Mapped[str | None] = mapped_column(String(120))
    toe_shape: Mapped[str | None] = mapped_column(String(120))
    last_width: Mapped[str | None] = mapped_column(String(120))
    water_resistance: Mapped[str | None] = mapped_column(String(160))
    fit_note: Mapped[str | None] = mapped_column(Text)
    fit_recommendation: Mapped[str | None] = mapped_column(Text)
    grip_claim: Mapped[str | None] = mapped_column(Text)
    test_claim: Mapped[str | None] = mapped_column(Text)
    care: Mapped[str | None] = mapped_column(Text)
    performance_claims: Mapped[list | None] = mapped_column(JSON, default=list)
    claims: Mapped[list | None] = mapped_column(JSON, default=list)
    images: Mapped[list | None] = mapped_column(JSON, default=list)

    category: Mapped[Category] = relationship(back_populates="products")
    variants: Mapped[list[ProductVariant]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )


class ProductVariant(TimestampMixin, Base):
    __tablename__ = "product_variants"
    __table_args__ = (
        UniqueConstraint("sku", name="uq_product_variants_sku"),
        CheckConstraint("price_inr >= 0", name="ck_variants_price_non_negative"),
        CheckConstraint("launch_stock_qty >= 0", name="ck_variants_stock_non_negative"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True, nullable=False
    )
    sku: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    size_uk: Mapped[str] = mapped_column(String(12), nullable=False)
    size_eu: Mapped[str | None] = mapped_column(String(12))
    size_us_men: Mapped[str | None] = mapped_column(String(12))
    size_us_women: Mapped[str | None] = mapped_column(String(12))
    foot_length_cm: Mapped[Decimal | None] = mapped_column(Numeric(5, 2))
    foot_length_cm_status: Mapped[str | None] = mapped_column(String(120))
    price_inr: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    gst_rate: Mapped[Decimal | None] = mapped_column(Numeric(6, 4))
    net_revenue_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    target_landed_cost_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gross_margin_inr: Mapped[Decimal | None] = mapped_column(Numeric(12, 2))
    gross_margin_pct: Mapped[Decimal | None] = mapped_column(Numeric(6, 2))
    launch_stock_qty: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    launch_stock_status: Mapped[str | None] = mapped_column(String(120))
    stock_status: Mapped[str | None] = mapped_column(String(120))

    product: Mapped[Product] = relationship(back_populates="variants")
    inventory: Mapped[Inventory] = relationship(
        back_populates="variant", cascade="all, delete-orphan", uselist=False
    )
    inventory_events: Mapped[list[InventoryEvent]] = relationship(
        back_populates="variant", cascade="all, delete-orphan"
    )


class Inventory(TimestampMixin, Base):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("variant_id", name="uq_inventory_variant"),
        CheckConstraint("on_hand >= 0", name="ck_inventory_on_hand_non_negative"),
        CheckConstraint("reserved >= 0", name="ck_inventory_reserved_non_negative"),
        CheckConstraint("reserved <= on_hand", name="ck_inventory_reserved_lte_on_hand"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    on_hand: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reserved: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    variant: Mapped[ProductVariant] = relationship(back_populates="inventory")


class InventoryEvent(TimestampMixin, Base):
    __tablename__ = "inventory_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(40), nullable=False)
    quantity_delta: Mapped[int] = mapped_column(Integer, nullable=False)
    reference: Mapped[str | None] = mapped_column(String(160), unique=True)
    note: Mapped[str | None] = mapped_column(Text)

    variant: Mapped[ProductVariant] = relationship(back_populates="inventory_events")


class Cart(TimestampMixin, Base):
    __tablename__ = "carts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    items: Mapped[list[CartItem]] = relationship(
        back_populates="cart", cascade="all, delete-orphan"
    )


class CartItem(TimestampMixin, Base):
    __tablename__ = "cart_items"
    __table_args__ = (
        UniqueConstraint("cart_id", "variant_id", name="uq_cart_items_variant"),
        CheckConstraint("quantity > 0", name="ck_cart_items_quantity_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cart_id: Mapped[int] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"), index=True, nullable=False
    )
    variant_id: Mapped[int] = mapped_column(
        ForeignKey("product_variants.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    reservation_reference: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False
    )
    reservation_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True)
    )

    cart: Mapped[Cart] = relationship(back_populates="items")
    variant: Mapped[ProductVariant] = relationship()
