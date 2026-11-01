from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Fail the launch check if a published product still uses a "
            "placeholder image or contains an unresolved field."
        )
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from sqlalchemy import select

    from app.db import SessionLocal
    from app.models import Product
    from app.services.publish import (
        product_unresolved_fields,
        published_placeholder_products,
    )

    failures: list[str] = []
    with SessionLocal() as session:
        published = session.scalars(
            select(Product).where(Product.status == "published").order_by(Product.name)
        ).all()
        placeholder_products = published_placeholder_products(session)
        for product in placeholder_products:
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

    if failures:
        print("LAUNCH CHECK FAILED")
        for failure in failures:
            print(f"- {failure}")
        print(
            f"\nPublished products checked: {len(published)}. "
            f"Failures: {len(failures)}."
        )
        return 1

    print("LAUNCH CHECK PASSED")
    print(f"Published products checked: {len(published)}. No placeholder images.")
    print("No unresolved [TO CONFIRM] fields in published products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
