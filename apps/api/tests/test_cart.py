from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from app.db import get_db
from app.main import app
from app.models import Cart, Inventory, ProductVariant
from app.services.cart import CART_COOKIE_NAME, hash_cart_token

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
    raw = response.cookies.get(CART_COOKIE_NAME)
    assert raw, "cart cookie was not set"
    return raw


def _add(client: TestClient, sku: str, quantity: int = 1):
    return client.post("/cart/items", json={"sku": sku, "quantity": quantity})


def _reserved(db_session, sku: str) -> int:
    db_session.expire_all()
    variant = db_session.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
    inventory = db_session.scalar(
        select(Inventory).where(Inventory.variant_id == variant.id)
    )
    return inventory.reserved


def _isolated_client(db_engine, ip: str | None = None) -> TestClient:
    """A second browser: its own cookie jar, same database and app.

    ``ip`` sets the client address the API sees. Reservation caps are per IP,
    so tests that need a fresh allowance must pass a different address.
    """

    factory = sessionmaker(bind=db_engine, expire_on_commit=False)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    if ip:
        return TestClient(app, client=(ip, 50000))
    return TestClient(app)


def test_cart_cookie_is_http_only_and_the_token_is_hashed(
    client: TestClient, db_session
) -> None:
    response = client.post("/cart")
    assert response.status_code == 201, response.text
    set_cookie = response.headers["set-cookie"]
    assert CART_COOKIE_NAME in set_cookie
    assert "HttpOnly" in set_cookie
    assert "SameSite=lax" in set_cookie

    raw = response.cookies.get(CART_COOKIE_NAME)
    assert raw
    assert "token" not in response.json()

    cart = db_session.scalar(select(Cart))
    assert cart is not None
    assert cart.token_hash == hash_cart_token(raw)
    assert cart.token_hash != raw
    assert len(cart.token_hash) == 64

    # The browser jar sends the cookie automatically.
    assert client.get("/cart").status_code == 200

    # A forged raw token that was never issued cannot be used.
    client.cookies.clear()
    assert client.get("/cart").status_code == 404


def test_cart_add_update_and_remove_reserves_stock(
    client: TestClient, db_session
) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=20)

    _new_cart(client)
    added = _add(client, "RELAY-UK7", 2)
    assert added.status_code == 200, added.text
    body = added.json()
    assert body["status"] == "active"
    assert body["total_units"] == 2
    assert body["subtotal_inr"] == 4598.0
    assert body["items"][0]["quantity"] == 2
    assert body["items"][0]["available"] == 18
    assert body["items"][0]["max_reservable"] == 4
    assert "Milestone 3" in body["rules"]["checkout"]
    assert _reserved(db_session, "RELAY-UK7") == 2

    read = client.get("/cart")
    assert read.status_code == 200
    assert read.json()["items"][0]["quantity"] == 2

    item_id = body["items"][0]["id"]
    updated = client.patch(f"/cart/items/{item_id}", json={"quantity": 3})
    assert updated.status_code == 200, updated.text
    assert updated.json()["items"][0]["quantity"] == 3
    assert _reserved(db_session, "RELAY-UK7") == 3

    removed = client.delete(f"/cart/items/{item_id}")
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
            on_hand=40,
        )

    _new_cart(client)
    assert _add(client, "RELAY-0", 5).status_code == 200
    too_many_on_line = _add(client, "RELAY-0", 1)
    assert too_many_on_line.status_code == 400
    assert "Maximum 5 units per size" in too_many_on_line.json()["detail"]

    assert _add(client, "RELAY-1", 5).status_code == 200
    over_cart = _add(client, "RELAY-2", 1)
    assert over_cart.status_code == 400
    assert "Maximum 10 units per cart" in over_cart.json()["detail"]

    other = _isolated_client(db_session.bind, "198.51.100.7")
    try:
        _new_cart(other)
        for index in range(5):
            assert _add(other, f"RELAY-{index}", 1).status_code == 200
        over_lines = _add(other, "RELAY-5", 1)
        assert over_lines.status_code == 400
        assert "Maximum 5 lines per cart" in over_lines.json()["detail"]
    finally:
        other.close()


def test_cart_prevents_overselling_the_last_unit(
    client: TestClient, db_session
) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=1)

    second = _isolated_client(db_session.bind)
    try:
        _new_cart(client)
        _new_cart(second)
        assert _add(client, "RELAY-UK7", 1).status_code == 200
        blocked = _add(second, "RELAY-UK7", 1)
        assert blocked.status_code == 409
        assert "does not have 1 available" in blocked.json()["detail"]

        item_id = client.get("/cart").json()["items"][0]["id"]
        assert client.delete(f"/cart/items/{item_id}").status_code == 200
        assert _add(second, "RELAY-UK7", 1).status_code == 200
    finally:
        second.close()


def test_cart_rejects_unknown_sku_and_missing_token(client: TestClient) -> None:
    assert client.get("/cart").status_code == 404
    _new_cart(client)
    unknown = _add(client, "MISSING-SKU")
    assert unknown.status_code == 400
    assert "Unknown SKU" in unknown.json()["detail"]


def test_expired_cart_releases_its_reservation(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=20)

    raw = _new_cart(client)
    assert _add(client, "RELAY-UK7", 2).status_code == 200
    assert _reserved(db_session, "RELAY-UK7") == 2

    cart = db_session.scalar(select(Cart).where(Cart.token_hash == hash_cart_token(raw)))
    cart.expires_at = datetime.now(timezone.utc) - timedelta(minutes=1)
    db_session.commit()

    expired = client.get("/cart")
    assert expired.status_code == 200, expired.text
    body = expired.json()
    assert body["status"] == "expired"
    assert body["items"] == []
    assert body["expires_at"] is None
    assert _reserved(db_session, "RELAY-UK7") == 0

    blocked = _add(client, "RELAY-UK7", 1)
    assert blocked.status_code == 400
    assert "no longer active" in blocked.json()["detail"]


def test_per_ip_total_reservation_cap(client: TestClient, db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK6", size_uk="UK 6", on_hand=40)
    make_variant(db_session, product, sku="RELAY-UK7", size_uk="UK 7", on_hand=40)

    second = _isolated_client(db_session.bind)
    try:
        _new_cart(client)
        _new_cart(second)
        assert _add(client, "RELAY-UK6", 5).status_code == 200
        assert _add(client, "RELAY-UK7", 5).status_code == 200
        blocked = _add(second, "RELAY-UK6", 1)
        assert blocked.status_code == 400
        assert "Maximum 10 reserved units per IP" in blocked.json()["detail"]
    finally:
        second.close()


def test_per_size_reservation_cap_is_twenty_percent_with_a_floor(
    client: TestClient, db_session
) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=10)

    _new_cart(client)
    assert _add(client, "RELAY-UK7", 2).status_code == 200
    blocked = _add(client, "RELAY-UK7", 1)
    assert blocked.status_code == 400
    assert "Maximum 2 reserved units for this size per IP" in blocked.json()["detail"]


def test_a_different_ip_gets_its_own_cap(db_session) -> None:
    product = _make_product(db_session, name="Relay Moss", slug="relay-moss")
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=10)

    first = _isolated_client(db_session.bind, "203.0.113.10")
    second = _isolated_client(db_session.bind, "203.0.113.11")
    try:
        _new_cart(first)
        _new_cart(second)
        assert _add(first, "RELAY-UK7", 2).status_code == 200
        # The first IP holds the whole 20% cap. A different IP still has room.
        assert _add(second, "RELAY-UK7", 2).status_code == 200
    finally:
        first.close()
        second.close()
