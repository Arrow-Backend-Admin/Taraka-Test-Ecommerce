# Runbook: failing webhooks

Use this when Razorpay reports failed deliveries, when orders stop reaching
`paid`, or when `WebhookEvent` rows accumulate as `failed` or stale `received`.

## How intake works

1. The raw body is verified with `RAZORPAY_WEBHOOK_SECRET` before parsing.
2. The event id (header, then payload `id`, then a body hash) is inserted into
   `webhook_events`. The insert is committed **before** any business work.
3. Only after that durable write does the API return 2xx to Razorpay.
4. Business processing runs with a bounded PostgreSQL retry for serialization
   failures and deadlocks.
5. Duplicate `processed` events are acknowledged without touching state. A
   `failed` event may be reprocessed on replay.

If the event cannot be stored, the API returns an error and Razorpay retries.

## 1. Find the failing events

```bash
cd apps/api
python - <<'PY'
from sqlalchemy import select
from app.db import SessionLocal
from app.models import WebhookEvent

with SessionLocal() as db:
    rows = db.scalars(
        select(WebhookEvent)
        .where(WebhookEvent.status.in_(["failed", "received"]))
        .order_by(WebhookEvent.created_at)
    ).all()
    for e in rows:
        print(e.created_at, e.event_id, e.event_type, e.status, e.error)
PY
```

## 2. Diagnose by status

### `failed`

`error` holds the exception text. Common causes:

- a payment references an order that does not exist (wrong environment: test
  webhook pointed at a production database or vice versa);
- captured amount/currency mismatch (this should become `needs_review`, not a
  crash — if it crashed, treat it as a bug);
- a database constraint or deadlock that outlived the retries;
- a bug in the handler.

Fix the cause first. Then ask Razorpay to resend the event. The intake flips the
row back to `received`, reprocesses it, and marks it `processed` on success.

### stale `received`

The process crashed after the durable insert but before processing finished, or
another worker is still handling it. A replay within the 5-minute lease is
treated as an in-flight duplicate. After the lease, a provider replay is
reclaimed automatically and processed, so normally you only need to resend the
event from the Razorpay dashboard.

If a row is older than the lease and no replay arrives, options in order of
preference:

1. If the event is a capture and the customer is waiting, verify the payment in
   the Razorpay dashboard and follow `docs/runbooks/stuck-payments.md`.
2. Resend the event from the Razorpay dashboard so the intake reclaims it.
3. Only if the dashboard cannot resend it, re-drive the handler deliberately
   with a reviewed script that loads the stored payload and calls
   `process_event`, then sets the row to `processed` or `failed`. Record the
   event id and outcome.

### Signature failures (no row at all)

A bad signature is rejected before any row is written, so there is nothing to
query. Check:

- the tunnel/URL points at the intended environment;
- the webhook secret in the Razorpay dashboard matches
  `RAZORPAY_WEBHOOK_SECRET`;
- a proxy is not rewriting the raw body (signature covers the exact bytes).

## 3. Confirm the endpoint is healthy

```bash
curl -fsS http://127.0.0.1:8000/health/live
curl -fsS http://127.0.0.1:8000/health/ready
```

`/health/ready` checks the database. If it fails, fix the database before
chasing webhooks.

## 4. After a fix

- Resend the affected events from the Razorpay dashboard.
- Confirm the rows become `processed`.
- Run `make reconcile` and check the affected orders.
- Write down the root cause and the events replayed.
