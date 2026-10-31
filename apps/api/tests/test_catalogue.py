from __future__ import annotations

from fastapi.testclient import TestClient

from .factories import make_category

ADMIN_HEADERS = {"Authorization": "Bearer test-admin-token"}


def _create_product(client: TestClient, **overrides):
    payload = {
        "id": "TEST-001",
        "sku_prefix": "TEST-001",
        "name": "Test Product",
        "slug": "test-product",
        "category_slug": "sneakers",
        "price_inr": 2299,
        "mrp_inr": 2299,
        "colour": "Chalk",
        "colour_hex": "#E9E4D8",
        "tier": "good",
        "tier_label": "Good",
        "short_description": "A clean test product.",
    }
    payload.update(overrides)
    return client.post("/admin/products", headers=ADMIN_HEADERS, json=payload)


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_admin_requires_token(client: TestClient) -> None:
    assert client.get("/admin/products").status_code == 401
    assert (
        client.get(
            "/admin/products", headers={"Authorization": "Bearer wrong-token"}
        ).status_code
        == 401
    )


def test_publish_then_storefront_lists_safe_product(client: TestClient, db_session) -> None:
    make_category(db_session)

    created = _create_product(client)
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]
    assert created.json()["status"] == "draft"
    assert created.json()["unresolved_fields"] == []

    published = client.post(
        f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
    )
    assert published.status_code == 200, published.text
    assert published.json()["status"] == "published"

    catalogue = client.get("/catalogue")
    assert catalogue.status_code == 200
    assert "[TO CONFIRM" not in catalogue.text
    data = catalogue.json()
    assert len(data) == 1
    assert data[0]["id"] == "TEST-001"
    assert data[0]["summary"] == "A clean test product."
    assert data[0]["category"] == "Sneakers"

    detail = client.get("/catalogue/test-product")
    assert detail.status_code == 200
    assert "[TO CONFIRM" not in detail.text
    assert detail.json()["id"] == "TEST-001"


def test_publish_guard_blocks_unresolved_fields(client: TestClient, db_session) -> None:
    make_category(db_session)

    created = _create_product(
        client, upper_material="[TO CONFIRM: manufacturer]"
    )
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    published = client.post(
        f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
    )
    assert published.status_code == 409
    detail = published.json()["detail"]
    assert "upper_material" in detail["unresolved_fields"]

    product = client.get(f"/admin/products/{product_id}", headers=ADMIN_HEADERS)
    assert product.json()["status"] == "draft"
    assert client.get("/catalogue").json() == []


def test_publish_guard_scans_variant_fields(client: TestClient, db_session) -> None:
    make_category(db_session)

    created = _create_product(client)
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    variant = client.post(
        f"/admin/products/{product_id}/variants",
        headers=ADMIN_HEADERS,
        json={
            "sku": "TEST-001-UK7",
            "size_uk": "UK 7",
            "price_inr": 2299,
            "launch_stock_qty": 0,
            "launch_stock_status": "[TO CONFIRM: founder]",
        },
    )
    assert variant.status_code == 201, variant.text

    published = client.post(
        f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
    )
    assert published.status_code == 409
    fields = published.json()["detail"]["unresolved_fields"]
    assert "variants.TEST-001-UK7.launch_stock_status" in fields


def test_published_product_rejects_flagged_variant(
    client: TestClient, db_session
) -> None:
    make_category(db_session)
    created = _create_product(client)
    product_id = created.json()["id"]
    assert (
        client.post(
            f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
        ).status_code
        == 200
    )

    variant = client.post(
        f"/admin/products/{product_id}/variants",
        headers=ADMIN_HEADERS,
        json={
            "sku": "TEST-001-UK8",
            "size_uk": "UK 8",
            "price_inr": 2299,
            "launch_stock_qty": 0,
            "launch_stock_status": "[TO CONFIRM: founder]",
        },
    )
    assert variant.status_code == 409
    assert "launch_stock_status" in variant.text

    detail = client.get("/catalogue/test-product")
    assert detail.status_code == 200
    assert detail.json()["sizes"] == []


def test_forced_published_unresolved_product_is_hidden(
    client: TestClient, db_session
) -> None:
    category = make_category(db_session)
    from .factories import make_product

    make_product(
        db_session,
        category,
        upper_material="[TO CONFIRM: manufacturer]",
        status="published",
    )

    response = client.get("/catalogue")
    assert response.status_code == 200
    assert response.json() == []
    assert "[TO CONFIRM" not in response.text
