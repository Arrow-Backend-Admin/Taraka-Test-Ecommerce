from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(description="Load the Phase 3 catalogue into the API database.")
    parser.add_argument("--catalogue", type=Path, default=None, help="Path to products.json")
    parser.add_argument(
        "--placeholders",
        type=Path,
        default=None,
        help="Path to placeholder-images.json (defaults to the Phase 4 set).",
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    parser.add_argument(
        "--create-tables",
        action="store_true",
        help="Create tables directly for local development. Alembic is the production path.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from sqlalchemy import select

    from app.db import Base, SessionLocal, engine
    from app.models import Product
    from app.seed import seed_catalogue
    from app.services.publish import product_unresolved_fields

    if args.create_tables:
        Base.metadata.create_all(engine)

    with SessionLocal() as session:
        counts = seed_catalogue(session, args.catalogue, args.placeholders)
        products = session.scalars(select(Product)).all()
        unresolved = sum(1 for product in products if product_unresolved_fields(product))

    print(
        "Seeded {products} products, {variants} variants, {categories} categories, "
        "{inventory} inventory rows.".format(**counts)
    )
    print(f"Products with unresolved [TO CONFIRM] fields: {unresolved}/{len(products)}")
    print("All seeded products remain draft. Publish is blocked until flags are resolved.")


if __name__ == "__main__":
    main()
