from __future__ import annotations

import uuid
from decimal import Decimal
from types import SimpleNamespace

from hypothesis import given, settings
from hypothesis import strategies as st
from sqlalchemy import Integer, create_engine, select
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.db import Base
from app.models import Inventory, Order, OrderItem, Payment
from app.services.inventory import OutOfStock, release_stock, reserve_stock
from app.services.money import (
    GST_REDUCED_PCT,
    GST_STANDARD_PCT,
    gst_rate_pct,
    rupees_to_paise,
    split_gst,
)
from app.services.orders import _checkout_snapshot

from .factories import make_category, make_product, make_variant

MONEY_COLUMNS = {"total_paise", "gst_paise", "subtotal_paise", "shipping_paise"}


def _settings() -> Settings:
    return Settings(
        APP_ENV="development",
        RAZORPAY_KEY_ID="rzp_test_mock",
        RAZORPAY_KEY_SECRET="test-key-secret",
        RAZORPAY_WEBHOOK_SECRET="test-webhook-secret",
        RAZORPAY_MOCK=True,
        MAIL_ENABLED=False,
    )


@given(
    line_total=st.integers(min_value=0, max_value=10_000_000),
    rate=st.sampled_from([GST_REDUCED_PCT, GST_STANDARD_PCT]),
)
@settings(max_examples=200, deadline=None)
def test_gst_split_always_adds_back_to_the_line_total(line_total: int, rate: int) -> None:
    taxable, gst = split_gst(line_total, rate)
    assert isinstance(taxable, int) and not isinstance(taxable, bool)
    assert isinstance(gst, int) and not isinstance(gst, bool)
    assert taxable >= 0
    assert gst >= 0
    assert taxable + gst == line_total


@given(
    unit_price_paise=st.integers(min_value=1, max_value=10_000_000),
    quantity=st.integers(min_value=1, max_value=5),
    rate=st.sampled_from([GST_REDUCED_PCT, GST_STANDARD_PCT]),
)
@settings(max_examples=100, deadline=None)
def test_order_snapshot_totals_equal_the_sum_of_lines(
    unit_price_paise: int, quantity: int, rate: int
) -> None:
    product = SimpleNamespace(
        id="TEST-001",
        name="Property Product",
        slug="property-product",
        status="published",
        gst_rate=Decimal(rate) / Decimal(100),
        hsn=None,
    )
    variant = SimpleNamespace(
        id=1,
        sku="PROP-UK7",
        size_uk="UK 7",
        price_inr=Decimal(unit_price_paise) / Decimal(100),
        product=product,
    )
    item = SimpleNamespace(
        variant=variant,
        quantity=quantity,
        reservation_reference=f"cart:{uuid.uuid4().hex}",
    )
    cart = SimpleNamespace(items=[item])

    lines = _checkout_snapshot(cart, _settings())

    assert sum(line["line_total_paise"] for line in lines) == (
        sum(line["taxable_value_paise"] for line in lines)
        + sum(line["gst_paise"] for line in lines)
    )
    for line in lines:
        assert line["line_total_paise"] == unit_price_paise * quantity
        assert line["taxable_value_paise"] + line["gst_paise"] == line[
            "line_total_paise"
        ]
        assert isinstance(line["taxable_value_paise"], int)
        assert isinstance(line["gst_paise"], int)


@given(value=st.decimals(min_value=0, max_value=100000, places=2))
@settings(max_examples=100, deadline=None)
def test_rupees_to_paise_returns_integer_paise(value: Decimal) -> None:
    paise = rupees_to_paise(value)
    assert isinstance(paise, int) and not isinstance(paise, bool)
    assert paise >= 0


@given(unit_price_paise=st.integers(min_value=0, max_value=10_000_000))
@settings(max_examples=100, deadline=None)
def test_gst_rate_is_always_a_known_slab(unit_price_paise: int) -> None:
    assert gst_rate_pct(unit_price_paise) in (GST_REDUCED_PCT, GST_STANDARD_PCT)


def test_money_columns_use_integer_paise_not_float() -> None:
    for model in (Order, OrderItem, Payment):
        for column in model.__table__.columns:
            if column.name.endswith("_paise"):
                assert isinstance(column.type, Integer), (
                    f"{model.__tablename__}.{column.name} must be integer paise"
                )


def test_inventory_columns_are_integers() -> None:
    for name in ("on_hand", "reserved", "version"):
        assert isinstance(Inventory.__table__.columns[name].type, Integer)


@given(
    operations=st.lists(
        st.tuples(
            st.sampled_from(["reserve", "release"]),
            st.integers(min_value=1, max_value=10),
        ),
        max_size=25,
    )
)
@settings(max_examples=25, deadline=None)
def test_stock_never_goes_below_zero_and_reservations_never_exceed_available(
    operations: list[tuple[str, int]],
) -> None:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    try:
        with Session(engine, expire_on_commit=False) as db:
            category = make_category(db, slug=f"cat-{uuid.uuid4().hex}", code="PR")
            product = make_product(
                db,
                category,
                id=f"PROP-{uuid.uuid4().hex[:8]}",
                sku_prefix="PROP",
                slug=f"prop-{uuid.uuid4().hex}",
            )
            variant = make_variant(db, product, sku=f"PROP-{uuid.uuid4().hex}", on_hand=12)

            for index, (action, quantity) in enumerate(operations):
                reference = f"prop:{index}:{uuid.uuid4().hex}"
                try:
                    if action == "reserve":
                        reserve_stock(db, variant.id, quantity, reference=reference)
                    else:
                        release_stock(db, variant.id, quantity, reference=reference)
                except OutOfStock:
                    db.rollback()

                inventory = db.scalar(
                    select(Inventory).where(Inventory.variant_id == variant.id)
                )
                assert inventory is not None
                assert inventory.on_hand >= 0
                assert inventory.reserved >= 0
                assert inventory.reserved <= inventory.on_hand
                assert inventory.on_hand - inventory.reserved >= 0
    finally:
        engine.dispose()
