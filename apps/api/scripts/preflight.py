from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fail fast if the deployment is not ready to launch."
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from app.config import get_settings
    from app.db import SessionLocal
    from app.services.preflight import run_preflight

    settings = get_settings()
    with SessionLocal() as session:
        failures = run_preflight(session, settings)

    if not failures:
        print("Preflight passed: configuration, catalogue and migrations are launch-ready.")
        return 0

    print("Preflight failed:")
    for failure in failures:
        print(f"  - {failure}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
