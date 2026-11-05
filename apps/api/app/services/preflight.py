"""One-command launch preflight.

Every check is a launch blocker. The command is intentionally boring: it reads
configuration and the database, prints each failure, and exits non-zero. It does
not mutate data and it does not try to fix anything.
"""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.script import ScriptDirectory
from sqlalchemy import func, select
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Session

from ..config import Settings
from ..models import InventoryEvent, Product
from .launch import runtime_config_failures
from .publish import (
    product_unresolved_fields,
    published_placeholder_products,
)

API_ROOT = Path(__file__).resolve().parents[2]


def alembic_head() -> str | None:
    config = Config(str(API_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(API_ROOT / "alembic"))
    script = ScriptDirectory.from_config(config)
    return script.get_current_head()


def database_revision(connection: Connection) -> str | None:
    context = MigrationContext.configure(connection)
    return context.get_current_revision()


def preflight_failures(
    db: Session,
    settings: Settings,
    *,
    current_revision: str | None,
    head_revision: str | None,
) -> list[str]:
    failures: list[str] = []

    if settings.razorpay_mock:
        failures.append("mock payments are enabled (RAZORPAY_MOCK=true)")
    if settings.uses_live_razorpay_keys and not settings.is_production:
        failures.append("live Razorpay keys are set outside production")
    if settings.uses_test_razorpay_keys and settings.is_production:
        failures.append("Razorpay test keys are set in production")
    failures.extend(runtime_config_failures(settings))

    dev_fixture = db.scalar(
        select(func.count(InventoryEvent.id)).where(
            InventoryEvent.reference.like("dev-fixture:%")
        )
    )
    if dev_fixture:
        failures.append(
            f"development inventory fixture is present ({dev_fixture} event(s))"
        )

    for product in published_placeholder_products(db):
        failures.append(
            f"published product {product.id} ({product.name}) uses a placeholder image"
        )

    published = db.scalars(
        select(Product).where(Product.status == "published").order_by(Product.name)
    ).all()
    for product in published:
        unresolved = product_unresolved_fields(product)
        if unresolved:
            failures.append(
                f"published product {product.id} ({product.name}) has unresolved "
                f"fields: {', '.join(unresolved)}"
            )

    seller_state = (settings.seller_state or "").strip()
    seller_gstin = (settings.seller_gstin or "").strip()
    if not seller_state or "[TO CONFIRM" in seller_state.upper():
        failures.append("seller state is missing or unresolved")
    if not seller_gstin or "[TO CONFIRM" in seller_gstin.upper():
        failures.append("seller GSTIN is missing or unresolved")

    if (settings.admin_api_token or "").strip():
        failures.append(
            "static admin token is enabled; authentication must replace it before launch"
        )

    if not current_revision or current_revision != head_revision:
        failures.append(
            "database migrations are not at head "
            f"(current={current_revision or 'none'}, head={head_revision or 'none'})"
        )

    return failures


def run_preflight(db: Session, settings: Settings) -> list[str]:
    connection = db.connection()
    return preflight_failures(
        db,
        settings,
        current_revision=database_revision(connection),
        head_revision=alembic_head(),
    )
