from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Release stock held by orders whose payment window has closed."
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from app.db import SessionLocal
    from app.services.orders import expire_orders

    with SessionLocal() as session:
        expired = expire_orders(session)

    print(f"Expired {expired} order(s); their stock reservations were released.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
