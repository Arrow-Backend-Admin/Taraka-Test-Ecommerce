"""Shared launch checks.

The CLI script and the live-payment startup guard must agree on what "ready to
launch" means: no published product may use a placeholder image or carry an
unresolved ``[TO CONFIRM]`` field.
"""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Product
from .publish import product_unresolved_fields, published_placeholder_products


class LaunchCheckFailed(RuntimeError):
    def __init__(self, failures: list[str]) -> None:
        self.failures = failures
        super().__init__("Launch check failed: " + "; ".join(failures))


def launch_failures(db: Session) -> list[str]:
    failures: list[str] = []
    published = db.scalars(
        select(Product).where(Product.status == "published").order_by(Product.name)
    ).all()
    for product in published_placeholder_products(db):
        failures.append(
            f"placeholder image: {product.id} ({product.name}) — "
            "replace with real product photography before launch"
        )
    for product in published:
        unresolved = product_unresolved_fields(product)
        if unresolved:
            failures.append(
                f"unresolved fields: {product.id} ({product.name}) — "
                + ", ".join(unresolved)
            )
    return failures


def assert_launch_ready(db: Session) -> None:
    failures = launch_failures(db)
    if failures:
        raise LaunchCheckFailed(failures)
