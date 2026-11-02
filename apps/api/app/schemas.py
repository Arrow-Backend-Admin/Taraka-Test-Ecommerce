from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CategoryCreate(BaseModel):
    name: str
    slug: str
    code: str
    description: str | None = None
    sort_order: int = 0


class CategoryUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    code: str | None = None
    description: str | None = None
    sort_order: int | None = None


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    slug: str
    code: str
    description: str | None
    sort_order: int


class ProductCreate(BaseModel):
    """Core product fields. Extra keys map to model columns when present."""

    model_config = ConfigDict(extra="allow")

    id: str
    sku_prefix: str
    name: str
    slug: str
    category_slug: str
    price_inr: Decimal
    mrp_inr: Decimal
    colour: str
    colour_hex: str
    tier: str = "good"
    tier_label: str | None = None
    short_description: str | None = None
    long_description: str | None = None
    launch_date: date | None = None


class ProductUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    sku_prefix: str | None = None
    name: str | None = None
    slug: str | None = None
    category_slug: str | None = None
    price_inr: Decimal | None = None
    mrp_inr: Decimal | None = None
    colour: str | None = None
    colour_hex: str | None = None
    tier: str | None = None
    tier_label: str | None = None
    short_description: str | None = None
    long_description: str | None = None
    launch_date: date | None = None


class VariantCreate(BaseModel):
    model_config = ConfigDict(extra="allow")

    sku: str
    size_uk: str
    price_inr: Decimal
    size_eu: str | None = None
    size_us_men: str | None = None
    size_us_women: str | None = None
    foot_length_cm: Decimal | None = None
    foot_length_cm_status: str | None = None
    gst_rate: Decimal | None = None
    net_revenue_inr: Decimal | None = None
    target_landed_cost_inr: Decimal | None = None
    gross_margin_inr: Decimal | None = None
    gross_margin_pct: Decimal | None = None
    launch_stock_qty: int = 0
    launch_stock_status: str | None = None
    stock_status: str | None = None


class VariantUpdate(BaseModel):
    model_config = ConfigDict(extra="allow")

    size_uk: str | None = None
    price_inr: Decimal | None = None
    size_eu: str | None = None
    size_us_men: str | None = None
    size_us_women: str | None = None
    foot_length_cm: Decimal | None = None
    foot_length_cm_status: str | None = None
    gst_rate: Decimal | None = None
    net_revenue_inr: Decimal | None = None
    target_landed_cost_inr: Decimal | None = None
    gross_margin_inr: Decimal | None = None
    gross_margin_pct: Decimal | None = None
    launch_stock_qty: int | None = None
    launch_stock_status: str | None = None
    stock_status: str | None = None


class InventoryAdjust(BaseModel):
    quantity_delta: int
    note: str | None = None


class PublishResult(BaseModel):
    id: str
    status: str
    unresolved_fields: list[str] = Field(default_factory=list)


class AdminProductSummary(BaseModel):
    id: str
    name: str
    slug: str
    status: str
    category: str
    price_inr: float
    variant_count: int
    unresolved_count: int


class PublicImageOut(BaseModel):
    role: str
    filename: str
    url: str | None
    alt: str
    is_placeholder: bool
    aspect: str = "4:5"
    placeholder_notice: str | None = None
    kind: str = "photo"
    changes: str | None = None
    source: str | None = None
    source_title: str | None = None
    source_url: str | None = None
    photographer: str | None = None
    licence_name: str | None = None
    licence_url: str | None = None
    attribution: str | None = None
    qa_result: str | None = None


class PublicVariantOut(BaseModel):
    sku: str
    size_uk: str
    size_eu: str | None
    size_us_men: str | None
    size_us_women: str | None
    foot_length_cm: float | None
    foot_length_note: str | None = None
    price_inr: float
    available: int


class PublicProductOut(BaseModel):
    id: str
    name: str
    slug: str
    category: str
    sub_category: str | None
    audience: str | None
    colour: str
    colour_hex: str
    price_inr: float
    mrp_inr: float
    summary: str | None
    hero: bool
    image: str | None
    images: list[PublicImageOut] = Field(default_factory=list)
    status: str
    preview: bool = False
    features: list[str] = Field(default_factory=list)
    unresolved_fields: list[str] = Field(default_factory=list)


class PublicProductDetailOut(PublicProductOut):
    description: str | None
    sizes: list[PublicVariantOut] = Field(default_factory=list)
    materials: dict[str, str] = Field(default_factory=dict)
    fit_notes: str | None
    care: str | None
    seo_title: str | None
    seo_description: str | None


class AdminProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    slug: str
    status: str
    category: CategoryOut
    price_inr: Decimal
    mrp_inr: Decimal
    colour: str
    colour_hex: str
    tier: str
    unresolved_fields: list[str] = Field(default_factory=list)
    data: dict[str, Any] = Field(default_factory=dict)


class StockSizeOut(BaseModel):
    sku: str
    size_uk: str
    available: int


class StockOut(BaseModel):
    slug: str
    sizes: list[StockSizeOut]
    as_of: datetime


class CartItemAdd(BaseModel):
    sku: str
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=0)


class CartItemOut(BaseModel):
    id: int
    sku: str
    name: str
    slug: str
    size_uk: str
    quantity: int
    unit_price: float
    line_total: float
    available: int
    reservation_expires_at: datetime | None


class CartOut(BaseModel):
    token: str
    status: str
    expires_at: datetime | None
    items: list[CartItemOut]
    subtotal_inr: float
    total_units: int
    reservation_minutes: int
    rules: dict[str, int | str]
