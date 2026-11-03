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

    from app.db import SessionLocal
    from app.services.launch import launch_failures

    with SessionLocal() as session:
        failures = launch_failures(session)

    if failures:
        print("LAUNCH CHECK FAILED")
        for failure in failures:
            print(f"- {failure}")
        print(f"\nFailures: {len(failures)}.")
        return 1

    print("LAUNCH CHECK PASSED")
    print("No published product uses a placeholder image.")
    print("No unresolved [TO CONFIRM] fields in published products.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
