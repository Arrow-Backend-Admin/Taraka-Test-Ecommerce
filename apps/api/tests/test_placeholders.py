from __future__ import annotations

import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.config import Settings, get_settings
from app.main import app
from app.services.publish import (
    PublishBlocked,
    preview_products,
    public_products,
    publish_product,
    published_placeholder_products,
)

from .factories import make_category, make_product, make_variant

ADMIN_HEADERS = {"Authorization": "Bearer test-admin-token"}

PLACEHOLDER_IMAGE = {
    "role": "hero-45",
    "filename": "placeholder_test-product_hero-45_4x5_v00.jpg",
    "url": "/placeholders/placeholder_test-product_hero-45_4x5_v00.jpg",
    "alt": "A pair of plain black leather shoes on a pale background.",
    "is_placeholder": True,
    "aspect": "4:5",
    "placeholder_notice": "Placeholder image, not the actual product",
}


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
        "images": [PLACEHOLDER_IMAGE],
    }
    payload.update(overrides)
    return client.post("/admin/products", headers=ADMIN_HEADERS, json=payload)


def test_preview_drafts_replaces_flags_and_labels_placeholders(
    client: TestClient, db_session
) -> None:
    category = make_category(db_session)
    product = make_product(
        db_session,
        category,
        short_description="[TO CONFIRM: founder]",
        upper_material="[TO CONFIRM: manufacturer]",
        images=[PLACEHOLDER_IMAGE],
        status="draft",
    )
    make_variant(
        db_session,
        product,
        foot_length_cm_status="[TO CONFIRM: manufacturer]",
        on_hand=3,
    )

    assert client.get("/catalogue").json() == []

    response = client.get("/catalogue?preview_drafts=true")
    assert response.status_code == 200
    assert "[TO CONFIRM" not in response.text
    data = response.json()
    assert len(data) == 1
    assert data[0]["preview"] is True
    assert data[0]["status"] == "draft"
    assert data[0]["summary"] == "To be confirmed"
    assert data[0]["images"][0]["is_placeholder"] is True
    assert (
        data[0]["images"][0]["placeholder_notice"]
        == "Placeholder image, not the actual product"
    )

    detail = client.get("/catalogue/test-product?preview_drafts=true")
    assert detail.status_code == 200
    assert "[TO CONFIRM" not in detail.text
    body = detail.json()
    assert body["description"] == "To be confirmed"
    assert body["materials"]["upper"] == "To be confirmed"
    assert body["sizes"][0]["foot_length_note"] == "To be confirmed"
    assert body["images"][0]["alt"].startswith("A pair of plain black leather")


def test_production_publish_blocks_placeholder_images(db_session) -> None:
    category = make_category(db_session)
    product = make_product(db_session, category, images=[PLACEHOLDER_IMAGE])

    with pytest.raises(PublishBlocked) as exc_info:
        publish_product(db_session, product, environment="production")

    assert exc_info.value.reason == "placeholder_images"
    assert "images[0].is_placeholder" in exc_info.value.fields
    db_session.refresh(product)
    assert product.status == "draft"

    publish_product(db_session, product, environment="development")
    db_session.refresh(product)
    assert product.status == "published"

    assert public_products(db_session, environment="production") == []
    assert len(public_products(db_session, environment="development")) == 1
    assert preview_products(db_session, environment="production") == []
    assert published_placeholder_products(db_session) == [product]


def test_admin_publish_and_update_block_placeholders_in_production(
    client: TestClient, db_session
) -> None:
    make_category(db_session)
    created = _create_product(client)
    assert created.status_code == 201, created.text
    product_id = created.json()["id"]

    production = Settings.model_validate(
        {"APP_ENV": "production", "ADMIN_API_TOKEN": "test-admin-token"}
    )
    app.dependency_overrides[get_settings] = lambda: production
    try:
        blocked = client.post(
            f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
        )
        assert blocked.status_code == 409, blocked.text
        detail = blocked.json()["detail"]
        assert detail["reason"] == "placeholder_images"
        assert detail["placeholder_images"] == ["images[0].is_placeholder"]
        assert detail["unresolved_fields"] == []
        assert client.get("/catalogue?preview_drafts=true").json() == []
    finally:
        app.dependency_overrides.pop(get_settings, None)

    assert (
        client.post(
            f"/admin/products/{product_id}/publish", headers=ADMIN_HEADERS
        ).status_code
        == 200
    )

    app.dependency_overrides[get_settings] = lambda: production
    try:
        updated = client.patch(
            f"/admin/products/{product_id}",
            headers=ADMIN_HEADERS,
            json={"images": [PLACEHOLDER_IMAGE]},
        )
        assert updated.status_code == 409, updated.text
        assert updated.json()["detail"]["placeholder_images"] == [
            "images[0].is_placeholder"
        ]
    finally:
        app.dependency_overrides.pop(get_settings, None)


def test_placeholder_metadata_and_files_are_complete() -> None:
    root = Path(__file__).resolve().parents[3]
    metadata = json.loads(
        (root / "brand" / "phase-4" / "placeholder-images.json").read_text(
            encoding="utf-8"
        )
    )
    public_dir = root / "apps" / "storefront" / "public" / "placeholders"
    credits = (root / "brand" / "phase-4" / "image-credits.md").read_text(
        encoding="utf-8"
    )

    assert metadata["notice"] == "Placeholder image, not the actual product"
    assert len(metadata["products"]) == 30
    assert len(metadata["sources"]) == 12
    assert len(metadata["grey"]) == 18
    assert len(metadata["sources"]) + len(metadata["grey"]) == 30

    photos = 0
    grey = 0
    checked = 0
    for product in metadata["products"].values():
        assert len(product["images"]) == 6
        for image in product["images"]:
            checked += 1
            assert image["is_placeholder"] is True
            assert image["filename"].startswith("placeholder_")
            assert image["filename"].endswith("_4x5_v00.jpg")
            assert image["aspect"] == "4:5"
            assert image["alt"]
            assert image["kind"] in {"photo", "image_coming"}
            assert image["qa"]["result"] in {"pass", "no_suitable_source"}
            assert "[TO CONFIRM" not in json.dumps(image)
            assert (public_dir / image["filename"]).is_file()
            assert image["filename"] in credits

            if image["kind"] == "photo":
                photos += 1
                assert image["source"] == "Wikimedia Commons"
                assert image["source_url"].startswith(
                    "https://commons.wikimedia.org/wiki/File:"
                )
                assert image["photographer"]
                assert image["licence_name"] in {"CC0 1.0", "CC BY 4.0"}
                assert image["licence_url"].startswith("https://creativecommons.org/")
                assert image["licence_version"] and image["retrieved_at"]
                assert image["changes"] == "Cropped and resized"
                assert image["attribution"]
                assert image["qa"]["result"] == "pass"
            else:
                grey += 1
                assert image["source"] is None
                assert image["source_url"] is None
                assert image["photographer"] is None
                assert image["licence_name"] is None
                assert image["attribution"] is None
                assert image["image_coming_reason"]
                assert image["qa"]["result"] == "no_suitable_source"

    assert checked == 180
    assert photos == 72
    assert grey == 108

    # Every category/role pair appears exactly once across photos and grey slots.
    slots = {
        (item["category"], item["role"]) for item in metadata["sources"]
    } | {(item["category"], item["role"]) for item in metadata["grey"]}
    assert len(slots) == 30
    assert {item["category"] for item in metadata["grey"]} == {
        "sneakers",
        "running",
        "sandals",
        "boots",
        "everyday",
    }
    assert {item["category"] for item in metadata["sources"]} == {
        "sneakers",
        "sandals",
        "boots",
        "everyday",
    }

