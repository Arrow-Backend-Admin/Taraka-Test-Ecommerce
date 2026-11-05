"""Injection and XSS checks for the public surface.

The API is JSON-only and uses bound SQLAlchemy parameters, so these tests are
guards against a future regression (raw SQL, string formatting, HTML rendering)
rather than a claim that the current code is immune to every attack.
"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.models import Product

from .factories import make_category, make_product, make_variant
from .test_orders import _add, _checkout, _new_cart, _payload

SQL_PAYLOADS = [
    "' OR 1=1 --",
    "'; DROP TABLE products; --",
    '" OR ""="',
    "' UNION SELECT id, name FROM products --",
]

XSS_PAYLOAD = "<script>alert(1)</script>"


def _published_product(db_session):
    category = make_category(db_session)
    product = make_product(
        db_session,
        category,
        name="Relay Moss",
        slug="relay-moss",
        status="published",
        short_description="A light everyday sneaker.",
    )
    make_variant(db_session, product, sku="RELAY-UK7", on_hand=5)
    return product


def test_catalogue_search_does_not_execute_sql(
    client: TestClient, db_session
) -> None:
    _published_product(db_session)

    for payload in SQL_PAYLOADS:
        response = client.get("/catalogue", params={"q": payload})
        assert response.status_code == 200, response.text
        # The table still answers a normal query after every payload.
        assert [item["slug"] for item in client.get("/catalogue").json()] == [
            "relay-moss"
        ]

    assert db_session.scalar(select(func.count(Product.id))) == 1


def test_catalogue_filters_do_not_execute_sql(
    client: TestClient, db_session
) -> None:
    _published_product(db_session)

    for key in ("category", "colour", "size"):
        for payload in SQL_PAYLOADS:
            response = client.get("/catalogue", params={key: payload})
            # Either the filter treats it as a plain (non-matching) value or
            # schema length limits reject it. Neither may reach SQL unbound.
            assert response.status_code in (200, 422), response.text
            if response.status_code == 200:
                assert response.json() == []

    # Numeric filters reject a non-number with 422 rather than passing it to SQL.
    for key in ("min_price", "max_price"):
        response = client.get(
            "/catalogue", params={key: "0; DROP TABLE products"}
        )
        assert response.status_code == 422, response.text

    assert db_session.scalar(select(func.count(Product.id))) == 1


def test_xss_payload_is_returned_as_json_data_not_html(
    client: TestClient, db_session
) -> None:
    _published_product(db_session)
    _new_cart(client)
    _add(client, "RELAY-UK7", 1)
    created = _checkout(client, _payload(customer_name=XSS_PAYLOAD))

    response = client.get(f"/orders/{created['public_id']}")
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("application/json")
    # The payload round-trips as a JSON string. It is data, not markup.
    assert response.json()["customer_name"] == XSS_PAYLOAD
    assert not response.text.lstrip().startswith("<script")
    assert "<html" not in response.text.lower()


def test_storefront_never_uses_dangerously_set_inner_html() -> None:
    root = Path(__file__).resolve().parents[3] / "apps" / "storefront"
    offenders = [
        str(path.relative_to(root))
        for path in root.rglob("*.tsx")
        if "dangerouslySetInnerHTML" in path.read_text(encoding="utf-8")
    ]
    assert offenders == [], (
        "storefront renders raw HTML; use text nodes or sanitise first: "
        + ", ".join(offenders)
    )
