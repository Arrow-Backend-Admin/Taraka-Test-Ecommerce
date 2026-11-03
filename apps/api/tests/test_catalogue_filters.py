from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from .factories import make_category, make_product, make_variant


def _published_catalogue(db_session):
    sneakers = make_category(db_session)
    boots = make_category(
        db_session, name="Boots", slug="boots", code="BT", sort_order=1
    )

    relay = make_product(
        db_session,
        sneakers,
        id="TEST-RELAY",
        sku_prefix="TEST-RELAY",
        name="Relay Moss",
        slug="relay-moss",
        colour="Chalk",
        colour_hex="#E9E4D8",
        price_inr=Decimal("2299.00"),
        mrp_inr=Decimal("2299.00"),
        sub_category="Running",
        short_description="A light everyday sneaker.",
        status="published",
    )
    make_variant(db_session, relay, sku="TEST-RELAY-UK7", on_hand=4)

    trail = make_product(
        db_session,
        boots,
        id="TEST-TRAIL",
        sku_prefix="TEST-TRAIL",
        name="Trail Boot",
        slug="trail-boot",
        colour="Black",
        colour_hex="#1C1B19",
        price_inr=Decimal("3499.00"),
        mrp_inr=Decimal("3499.00"),
        sub_category="Hiking",
        short_description="A leather hiking boot.",
        status="published",
    )
    make_variant(
        db_session,
        trail,
        sku="TEST-TRAIL-UK9",
        size_uk="UK 9",
        size_eu="EU 43",
        on_hand=0,
    )
    return relay, trail


def test_catalogue_filters_by_category_colour_size_and_price(
    client: TestClient, db_session
) -> None:
    _published_catalogue(db_session)

    everything = client.get("/catalogue").json()
    assert [item["slug"] for item in everything] == ["relay-moss", "trail-boot"]

    by_category = client.get("/catalogue?category=sneakers").json()
    assert [item["slug"] for item in by_category] == ["relay-moss"]

    by_colour = client.get("/catalogue?colour=chalk").json()
    assert [item["slug"] for item in by_colour] == ["relay-moss"]

    by_size = client.get("/catalogue?size=UK%207").json()
    assert [item["slug"] for item in by_size] == ["relay-moss"]

    above = client.get("/catalogue?min_price=3000").json()
    assert [item["slug"] for item in above] == ["trail-boot"]

    below = client.get("/catalogue?max_price=3000").json()
    assert [item["slug"] for item in below] == ["relay-moss"]

    combined = client.get(
        "/catalogue?category=boots&colour=black&min_price=3000&max_price=4000"
    ).json()
    assert [item["slug"] for item in combined] == ["trail-boot"]


def test_catalogue_search_uses_the_shared_fields(
    client: TestClient, db_session
) -> None:
    _published_catalogue(db_session)

    assert [item["slug"] for item in client.get("/catalogue?q=relay").json()] == [
        "relay-moss"
    ]
    assert [item["slug"] for item in client.get("/catalogue?q=hiking").json()] == [
        "trail-boot"
    ]
    assert [item["slug"] for item in client.get("/catalogue?q=leather").json()] == [
        "trail-boot"
    ]
    assert client.get("/catalogue?q=zzzz").json() == []


def test_catalogue_facets_report_counts_and_available_sizes(
    client: TestClient, db_session
) -> None:
    _published_catalogue(db_session)

    facets = client.get("/catalogue/facets").json()
    assert {item["value"] for item in facets["categories"]} == {"sneakers", "boots"}
    assert {item["value"] for item in facets["colours"]} == {"Chalk", "Black"}
    assert facets["sizes"] == [{"value": "UK 7", "count": 1}]
    assert facets["price"] == {"min": 2299.0, "max": 3499.0}

    filtered = client.get("/catalogue/facets?category=boots").json()
    assert {item["value"] for item in filtered["categories"]} == {"boots"}
    assert filtered["sizes"] == []


def test_stock_endpoint_returns_live_availability(
    client: TestClient, db_session
) -> None:
    _published_catalogue(db_session)

    response = client.get("/catalogue/relay-moss/stock")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "relay-moss"
    assert body["sizes"] == [
        {
            "sku": "TEST-RELAY-UK7",
            "size_uk": "UK 7",
            "available": 4,
            "max_reservable": 2,
        }
    ]
    assert body["as_of"]

    assert client.get("/catalogue/missing-product/stock").status_code == 404
