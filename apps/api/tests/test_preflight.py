from __future__ import annotations

import pytest

from app.config import Settings
from app.models import InventoryEvent
from app.services.preflight import (
    alembic_head,
    database_revision,
    preflight_failures,
    run_preflight,
)

from .factories import make_category, make_product, make_variant

HEAD = "head-revision"


def _settings(**overrides) -> Settings:
    values = {
        "APP_ENV": "development",
        "RAZORPAY_KEY_ID": "rzp_test_clean",
        "RAZORPAY_KEY_SECRET": "test-key-secret",
        "RAZORPAY_WEBHOOK_SECRET": "test-webhook-secret",
        "RAZORPAY_MOCK": False,
        "MAIL_ENABLED": False,
        "ADMIN_API_TOKEN": None,
        "SELLER_STATE": "Karnataka",
        "SELLER_GSTIN": "29ABCDE1234F1Z5",
        "CORS_ORIGINS": "https://shop.santvana.example",
    }
    values.update(overrides)
    return Settings(_env_file=None, **values)


def _failures(db_session, settings: Settings, *, current: str | None = HEAD) -> list[str]:
    return preflight_failures(
        db_session,
        settings,
        current_revision=current,
        head_revision=HEAD,
    )


def test_preflight_passes_on_a_clean_launch_ready_database(db_session) -> None:
    assert _failures(db_session, _settings()) == []


def test_preflight_fails_when_mock_payments_are_enabled(db_session) -> None:
    failures = _failures(db_session, _settings(RAZORPAY_MOCK=True))
    assert any("mock payments are enabled" in failure for failure in failures)


def test_preflight_fails_when_live_keys_are_used_outside_production(db_session) -> None:
    failures = _failures(
        db_session,
        _settings(
            APP_ENV="development",
            RAZORPAY_KEY_ID="rzp_live_abc",
            RAZORPAY_KEY_SECRET="secret",
        ),
    )
    assert any("live Razorpay keys" in failure for failure in failures)


def test_preflight_fails_when_test_keys_are_used_in_production(db_session) -> None:
    failures = _failures(
        db_session,
        _settings(
            APP_ENV="production",
            RAZORPAY_KEY_ID="rzp_test_abc",
            RAZORPAY_KEY_SECRET="secret",
            RAZORPAY_WEBHOOK_SECRET="hook",
        ),
    )
    assert any("test keys are set in production" in failure for failure in failures)


def test_preflight_fails_when_the_development_inventory_fixture_is_present(
    db_session,
) -> None:
    category = make_category(db_session, slug="fixture-cat", code="FX")
    product = make_product(
        db_session,
        category,
        id="FIX-1",
        sku_prefix="FIX-1",
        slug="fix-one",
    )
    variant = make_variant(db_session, product, sku="FIX-1-UK7", on_hand=5)
    db_session.add(
        InventoryEvent(
            variant_id=variant.id,
            event_type="dev_fixture",
            quantity_delta=5,
            reference="dev-fixture:FIX-1-UK7",
            note="DEV ONLY preview stock fixture",
        )
    )
    db_session.commit()

    failures = _failures(db_session, _settings())
    assert any("development inventory fixture is present" in failure for failure in failures)


def test_preflight_fails_when_a_published_product_has_a_placeholder_image(
    db_session,
) -> None:
    category = make_category(db_session, slug="placeholder-cat", code="PL")
    make_product(
        db_session,
        category,
        id="PLACE-1",
        sku_prefix="PLACE-1",
        slug="place-one",
        status="published",
        images=[
            {
                "role": "main",
                "filename": "placeholder.jpg",
                "is_placeholder": True,
            }
        ],
    )

    failures = _failures(db_session, _settings())
    assert any("uses a placeholder image" in failure for failure in failures)


def test_preflight_fails_when_a_published_product_has_an_unresolved_field(
    db_session,
) -> None:
    category = make_category(db_session, slug="unresolved-cat", code="UN")
    make_product(
        db_session,
        category,
        id="UNRES-1",
        sku_prefix="UNRES-1",
        slug="unres-one",
        status="published",
        short_description="[TO CONFIRM: founder] The real copy.",
    )

    failures = _failures(db_session, _settings())
    assert any("unresolved fields" in failure for failure in failures)


def test_preflight_fails_when_seller_state_is_missing(db_session) -> None:
    failures = _failures(db_session, _settings(SELLER_STATE="[TO CONFIRM: founder]"))
    assert any("seller state" in failure for failure in failures)


def test_preflight_fails_when_seller_gstin_is_missing(db_session) -> None:
    failures = _failures(db_session, _settings(SELLER_GSTIN=""))
    assert any("seller GSTIN" in failure for failure in failures)


def test_preflight_fails_when_the_static_admin_token_is_enabled(db_session) -> None:
    failures = _failures(db_session, _settings(ADMIN_API_TOKEN="static-token"))
    assert any("static admin token is enabled" in failure for failure in failures)


def test_preflight_fails_when_migrations_are_not_at_head(db_session) -> None:
    failures = _failures(db_session, _settings(), current="old-revision")
    assert any("migrations are not at head" in failure for failure in failures)


def test_preflight_fails_when_the_database_has_no_migration_revision(db_session) -> None:
    failures = _failures(db_session, _settings(), current=None)
    assert any("migrations are not at head" in failure for failure in failures)


def test_alembic_head_is_known() -> None:
    head = alembic_head()
    assert head
    assert isinstance(head, str)


def test_run_preflight_reports_an_unstamped_test_database(db_session) -> None:
    # The test schema is created directly from metadata, so Alembic has no
    # revision. The real command must report that rather than assume success.
    failures = run_preflight(db_session, _settings())
    assert any("migrations are not at head" in failure for failure in failures)
    assert database_revision(db_session.connection()) is None
