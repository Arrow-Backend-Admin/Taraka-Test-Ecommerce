from __future__ import annotations

from sqlalchemy import func, select

from app.models import Category, Inventory, InventoryEvent, Product, ProductVariant
from app.seed import seed_catalogue
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
