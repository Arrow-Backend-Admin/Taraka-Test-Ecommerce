from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

API_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(API_ROOT))


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Compare orders, payments, inventory and inventory_events. "
            "Exits non-zero when any mismatch is found."
        )
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON report instead of one line per mismatch.",
    )
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from app.db import SessionLocal
    from app.services.reconciliation import reconcile, summary

    with SessionLocal() as session:
        problems = reconcile(session)

    if args.json:
        print(json.dumps(summary(problems), indent=2))
    else:
        if not problems:
            print("Reconciliation passed: orders, payments and inventory agree.")
        for problem in problems:
            print(f"MISMATCH: {problem}")
        if problems:
            print(f"{len(problems)} mismatch(es) found.")
    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
