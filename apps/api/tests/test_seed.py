from __future__ import annotations

import pytest
from sqlalchemy import func, select

from app.config import Settings
from app.models import Category, Inventory, InventoryEvent, Product, ProductVariant
from app.seed import seed_catalogue, seed_dev_inventory
from app.services.copy import contains_banned_copy
from app.services.publish import product_unresolved_fields


def test_seed_loads_phase_3_catalogue_and_is_idempotent(db_session) -> None:
    first = seed_catalogue(db_session)
    assert first["products"] == 30
    assert first["variants"] == 330
    assert first["categories"] == 5
    assert first["inventory"] == 330

    second = seed_catalogue(db_session)
    assert second["products"] == 30
    assert second["variants"] == 330
    assert second["categories"] == 5
    assert second["inventory"] == 0

    assert db_session.scalar(select(func.count()).select_from(Product)) == 30
    assert db_session.scalar(select(func.count()).select_from(ProductVariant)) == 330
    assert db_session.scalar(select(func.count()).select_from(Inventory)) == 330
    assert db_session.scalar(select(func.count()).select_from(InventoryEvent)) == 330
    assert db_session.scalar(select(func.count()).select_from(Category)) == 5

    products = db_session.scalars(select(Product)).all()
    assert all(product.status == "draft" for product in products)
    assert all(product_unresolved_fields(product) for product in products)
    assert all(len(product.images or []) == 6 for product in products)
    assert all(
        image.get("is_placeholder") is True
        for product in products
        for image in (product.images or [])
    )
    assert all(not contains_banned_copy(product.summary_15w) for product in products)
    assert all(not contains_banned_copy(product.description_120w) for product in products)
    assert all(not contains_banned_copy(product.features) for product in products)


def test_dev_inventory_fixture_is_flagged_and_idempotent(db_session) -> None:
    counts = seed_catalogue(db_session, dev_inventory=True)
    assert counts["dev_inventory"] == 330

    variants = db_session.scalars(select(ProductVariant)).all()
    assert all(variant.launch_stock_qty == 0 for variant in variants)
    events = db_session.scalars(
        select(InventoryEvent).where(InventoryEvent.event_type == "dev_fixture")
    ).all()
    assert len(events) == 330
    assert all(event.reference.startswith("dev-fixture:") for event in events)
    assert all("not launch stock" in (event.note or "").lower() for event in events)

    on_hand = db_session.scalar(select(func.sum(Inventory.on_hand)))
    assert on_hand == 1794

    second = seed_catalogue(db_session, dev_inventory=True)
    assert second["dev_inventory"] == 0
    assert db_session.scalar(select(func.sum(Inventory.on_hand))) == on_hand


def test_dev_inventory_refuses_production(db_session, monkeypatch) -> None:
    seed_catalogue(db_session)
    production = Settings.model_validate(
        {"APP_ENV": "production", "ADMIN_API_TOKEN": "test-admin-token"}
    )
    monkeypatch.setattr("app.seed.get_settings", lambda: production)

    with pytest.raises(RuntimeError, match="APP_ENV=production"):
        seed_dev_inventory(db_session)

    assert (
        db_session.scalar(
            select(func.count())
            .select_from(InventoryEvent)
            .where(InventoryEvent.event_type == "dev_fixture")
        )
        == 0
    )
