from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select

from app.models import Cart, Inventory, ProductVariant

from .factories import make_category, make_product, make_variant


def _make_product(db_session, **overrides):
    category = make_category(
        db_session,
        name=overrides.pop("category_name", "Sneakers"),
        slug=overrides.pop("category_slug", "sneakers"),
        code=overrides.pop("category_code", "SN"),
    )
    return make_product(
        db_session,
        category,
        status="published",
        price_inr=Decimal("2299.00"),
        mrp_inr=Decimal("2299.00"),
        **overrides,
    )


def _new_cart(client: TestClient) -> str:
    response = client.post("/cart")
    assert response.status_code == 201, response.text
    return response.json()["token"]


def _add(client: TestClient, token: str, sku: str, quantity: int = 1):
    return client.post(
        "/cart/items",
        headers={"X-Cart-Token": token},
        json={"sku": sku, "quantity": quantity},
    )


def _reserved(db_session, sku: str) -> int:
    db_session.expire_all()
    variant = db_session.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    inventory = db_session.scalar(
        select(Inventory).where(Inventory.variant_id == variant.id)
    )
    return inventory.reserved


def test_cart_add_update_and_remove_reserves_stock(
    client: TestClient, db_session
) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=5)

    token = _new_cart(client)
    added = _add(client, token, "RELAY-UK7", 2)
    assert added.status_code == 200, added.text
    body = added.json()
    assert body["token"] == token
    assert body["status"] == "active"
    assert body["total_units"] == 2
    assert body["subtotal_inr"] == 4598.0
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["available"] == 3
    assert body["rules"]["checkout"] == "not available in this milestone"
    assert _reserved(db_session, "RELAY-UK7") == 2

    read = client.get("/cart", headers={"X-Cart-Token": token})
    assert read.status_code == 200
    assert read.json()["items"][0]["quantity"] == 2

    item_id = body["items"][0]["id"]
    updated = client.patch(
        f"/cart/items/{item_id}",
        headers={"X-Cart-Token": token},
        json={"quantity": 3},
    )
    assert updated.status_code == 200, updated.text
    assert updated.json()["items"][0]["quantity"] == 3
    assert _reserved(db_session, "RELAY-UK7") == 3

    removed = client.delete(
        f"/cart/items/{item_id}", headers={"X-Cart-Token": token}
    )
    assert removed.status_code == 200, removed.text
    assert removed.json()["items"] == []
    assert _reserved(db_session, "RELAY-UK7") == 0


def test_cart_enforces_line_cart_and_unit_limits(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    for index, size in enumerate(["UK 6", "UK 7", "UK 8", "UK 9", "UK 10", "UK 11"]):
        make_variant(
            db_session,
            product,
            sku=f"RELAY-{index}",
            size_uk=size,
            on_hand=10,
        )

    token = _new_cart(client)
    assert _add(client, token, "RELAY-0", 5).status_code == 200
    too_many_on_line = _add(client, token, "RELAY-0", 1)
    assert too_many_on_line.status_code == 400
    assert "Maximum 5 units per size" in too_many_on_line.json()["detail"]

    assert _add(client, token, "RELAY-1", 5).status_code == 200
    over_cart = _add(client, token, "RELAY-2", 1)
    assert over_cart.status_code == 400
    assert "Maximum 10 units per cart" in over_cart.json()["detail"]

    other = _new_cart(client)
    for index in range(5):
        assert _add(client, other, f"RELAY-{index}", 1).status_code == 200
    over_lines = _add(client, other, "RELAY-5", 1)
    assert over_lines.status_code == 400
    assert "Maximum 5 lines per cart" in over_lines.json()["detail"]


def test_cart_prevents_overselling_the_last_unit(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=1)

    first = _new_cart(client)
    second = _new_cart(client)
    assert _add(client, first, "RELAY-UK7", 1).status_code == 200
    blocked = _add(client, second, "RELAY-UK7", 1)
    assert blocked.status_code == 409
    assert "does not have 1 available" in blocked.json()["detail"]

    item_id = client.get("/cart", headers={"X-Cart-Token": first}).json()["items"][0][
        "id"
    ]
    assert (
        client.delete(f"/cart/items/{item_id}", headers={"X-Cart-Token": first}).status_code
        == 200
    )
    assert _add(client, second, "RELAY-UK7", 1).status_code == 200


def test_cart_rejects_unknown_sku_and_missing_token(client: TestClient) -> None:
    token = _new_cart(client)
    assert client.get("/cart").status_code == 404
    assert _add(client, "not-a-token", "RELAY-UK7").status_code == 404
    unknown = _add(client, token, "MISSING-SKU")
    assert unknown.status_code == 400
    assert "Unknown SKU" in unknown.json()["detail"]


def test_expired_cart_releases_its_reservation(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=2)

    token = _new_cart(client)
    assert _add(client, token, "RELAY-UK7", 2).status_code == 200
    assert _reserved(db_session, "RELAY-UK7") == 2

    cart = db_session.scalar(select(Cart).where(Cart.token == token))
    cart.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    expired = client.get("/cart", headers={"X-Cart-Token": token})
    assert expired.status_code == 200, expired.text
    body = expired.json()
    assert body["status"] == "expired"
    assert body["items"] == []
    assert body["expires_at"] is None
    assert _reserved(db_session, "RELAY-UK7") == 0

    blocked = _add(client, token, "RELAY-UK7", 1)
    assert blocked.status_code == 400
    assert "no longer active" in blocked.json()["detail"]
