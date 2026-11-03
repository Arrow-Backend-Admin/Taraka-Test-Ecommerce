from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


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
    max_reservable: int = 0


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
    max_reservable: int = 0
    reservation_expires_at: datetime | None


class CartOut(BaseModel):
    status: str
    expires_at: datetime | None
    items: list[CartItemOut]
    subtotal_inr: float
    total_units: int
    reservation_minutes: int
    rules: dict[str, int | float | str]

INDIAN_STATES = (
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
)
STATE_LOOKUP = {state.lower(): state for state in INDIAN_STATES}
STATE_ALIASES = {
    "nct of delhi": "Delhi",
    "new delhi": "Delhi",
    "orissa": "Odisha",
    "pondicherry": "Puducherry",
    "uttaranchal": "Uttarakhand",
    "jammu & kashmir": "Jammu and Kashmir",
    "andaman & nicobar islands": "Andaman and Nicobar Islands",
    "dadra & nagar haveli and daman & diu": "Dadra and Nagar Haveli and Daman and Diu",
    "dadra and nagar haveli": "Dadra and Nagar Haveli and Daman and Diu",
    "daman and diu": "Dadra and Nagar Haveli and Daman and Diu",
}


class IndianAddress(BaseModel):
    line1: str = Field(min_length=5, max_length=200)
    line2: str | None = Field(default=None, max_length=200)
    city: str = Field(min_length=2, max_length=80)
    state: str = Field(min_length=2, max_length=80)
    pincode: str
    country: str = "India"

    @field_validator("line1", "line2", "city")
    @classmethod
    def _strip_text(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = " ".join(value.split())
        return cleaned or None

    @field_validator("state")
    @classmethod
    def _known_state(cls, value: str) -> str:
        key = " ".join(value.strip().lower().split())
        canonical = STATE_LOOKUP.get(key) or STATE_ALIASES.get(key)
        if canonical is None:
            raise ValueError("Use an Indian state or union territory name")
        return canonical

    @field_validator("pincode")
    @classmethod
    def _indian_pincode(cls, value: str) -> str:
        cleaned = re.sub(r"\s+", "", value)
        if not re.fullmatch(r"[1-9][0-9]{5}", cleaned):
            raise ValueError("Pincode must be six digits and cannot start with 0")
        return cleaned

    @field_validator("country")
    @classmethod
    def _india_only(cls, value: str) -> str:
        if value.strip().lower() not in {"india", "in", "bharat"}:
            raise ValueError("Shipping is limited to India")
        return "India"


class CheckoutRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=120)
    customer_email: str = Field(max_length=254)
    customer_phone: str
    address: IndianAddress

    @field_validator("customer_name")
    @classmethod
    def _strip_name(cls, value: str) -> str:
        cleaned = " ".join(value.split())
        if len(cleaned) < 2:
            raise ValueError("Enter a full name")
        return cleaned

    @field_validator("customer_email")
    @classmethod
    def _email(cls, value: str) -> str:
        cleaned = value.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", cleaned):
            raise ValueError("Enter a valid email address")
        return cleaned

    @field_validator("customer_phone")
    @classmethod
    def _indian_mobile(cls, value: str) -> str:
        cleaned = re.sub(r"[\s\-()]", "", value)
        if cleaned.startswith("+91"):
            cleaned = cleaned[3:]
        elif cleaned.startswith("91") and len(cleaned) == 12:
            cleaned = cleaned[2:]
        elif cleaned.startswith("0") and len(cleaned) == 11:
            cleaned = cleaned[1:]
        if not re.fullmatch(r"[6-9][0-9]{9}", cleaned):
            raise ValueError("Enter a 10-digit Indian mobile number")
        return cleaned


class OrderAddressOut(BaseModel):
    line1: str
    line2: str | None
    city: str
    state: str
    pincode: str
    country: str


class OrderSellerOut(BaseModel):
    state: str
    gstin: str


class OrderItemOut(BaseModel):
    product_name: str
    product_slug: str
    sku: str
    size_uk: str
    quantity: int
    unit_price_paise: int
    line_total_paise: int
    taxable_value_paise: int
    gst_paise: int
    gst_rate_pct: int


class OrderPaymentOut(BaseModel):
    provider_order_id: str
    status: str
    amount_paise: int
    method: str | None


class OrderOut(BaseModel):
    public_id: str
    status: str
    currency: str
    created_at: datetime
    paid_at: datetime | None
    expired_at: datetime | None
    reservation_expires_at: datetime | None
    customer_name: str
    customer_email: str
    customer_phone: str
    address: OrderAddressOut
    seller: OrderSellerOut
    items: list[OrderItemOut]
    subtotal_paise: int
    gst_paise: int
    shipping_paise: int
    total_paise: int
    latest_payment: OrderPaymentOut | None
    next_action: str
    message: str


class PaymentCheckoutOut(BaseModel):
    provider: str
    key_id: str | None
    order_id: str
    amount_paise: int
    currency: str
    name: str
    description: str
    mock: bool
    prefill: dict[str, str]


class OrderCreatedOut(OrderOut):
    checkout: PaymentCheckoutOut | None = None


class PaymentVerifyRequest(BaseModel):
    razorpay_order_id: str = Field(min_length=1, max_length=120)
    razorpay_payment_id: str = Field(min_length=1, max_length=120)
    razorpay_signature: str = Field(min_length=1, max_length=256)


class PaymentVerifyOut(BaseModel):
    verified: bool
    order_status: str
    message: str


class WebhookAck(BaseModel):
    status: str
    event_id: str | None = None
