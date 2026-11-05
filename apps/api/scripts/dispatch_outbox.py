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
            "Send pending confirmation emails from the durable outbox. Run this "
            "on a schedule; the API only makes one best-effort attempt per payment."
        )
    )
    parser.add_argument(
        "--database-url",
        default=None,
        help="Override DATABASE_URL. Prefer the environment variable for real credentials.",
    )
    parser.add_argument("--limit", type=int, default=100)
    args = parser.parse_args()

    if args.database_url:
        os.environ["DATABASE_URL"] = args.database_url

    from sqlalchemy import func, select

    from app.config import get_settings
    from app.db import SessionLocal
    from app.models import EmailOutbox
    from app.services.outbox import dispatch_pending

    settings = get_settings()
    with SessionLocal() as session:
        sent = dispatch_pending(session, settings, limit=args.limit)
        pending = session.scalar(
            select(func.count())
            .select_from(EmailOutbox)
            .where(EmailOutbox.status == "pending")
        )
        failed = session.scalar(
            select(func.count())
            .select_from(EmailOutbox)
            .where(EmailOutbox.status == "failed")
        )

    print(f"Sent {sent} confirmation email(s).")
    print(f"Pending: {pending}; permanently failed: {failed}.")
    if not settings.mail_enabled:
        print("MAIL_ENABLED is false, so rows stay pending by design.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
