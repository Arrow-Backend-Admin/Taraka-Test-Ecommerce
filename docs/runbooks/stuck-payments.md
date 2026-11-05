# Runbook: stuck payments

Use this when an order stays `awaiting_payment`, `created`, `refund_pending` or
`payment_failed` longer than expected, or when a customer says money left their
account but the order is not `paid`.

## Ground rules

- **Only a signed webhook marks an order paid.** Never hand-edit an order to
  `paid` because the browser callback said so. The browser callback is a hint.
- Do not delete payment or webhook rows. They are the audit trail.
- All timestamps are UTC.

## 1. Identify the order and payment

```bash
cd apps/api
python - <<'PY'
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.db import SessionLocal
from app.models import Order, Payment, WebhookEvent

public_id = "ord_REPLACE_ME"
with SessionLocal() as db:
    order = db.scalar(
        select(Order)
        .options(joinedload(Order.items), joinedload(Order.payments))
        .where(Order.public_id == public_id)
    )
    print("status:", order.status, "total_paise:", order.total_paise)
    print("paid_at:", order.paid_at, "expires:", order.reservation_expires_at)
    print("notes:", order.notes)
    for p in order.payments:
        print(
            "payment", p.provider_order_id, p.provider_payment_id,
            p.status, p.amount_paise, p.currency,
            "needs_review=", p.needs_review, "reason=", p.review_reason,
        )
    for e in db.scalars(
        select(WebhookEvent).order_by(WebhookEvent.created_at.desc()).limit(20)
    ):
        print("event", e.event_id, e.event_type, e.status, e.error)
PY
```

## 2. Check whether the webhook arrived

- `WebhookEvent.status == "processed"`: the event was handled. If the order is
  still not paid, the event was not a capture for this order (wrong order id,
  wrong amount/currency, or a non-capture event). Continue to step 3.
- `WebhookEvent.status == "failed"`: read `error`. Fix the cause, then have
  Razorpay replay the event (dashboard → Webhooks → event → Resend). The intake
  accepts a replay for a `failed` row and reprocesses it.
- `WebhookEvent.status == "received"` and older than the 5-minute lease: the
  process likely crashed between durable storage and processing. Resend the
  event from the dashboard; the intake reclaims a stale `received` row. If no
  replay is possible, inspect the payload and follow step 4.
- `WebhookEvent.status == "received"` and fresh: another worker is probably
  still handling it. Wait for the lease before treating it as stuck.
- No event at all: the webhook is not registered, the URL/tunnel is wrong, the
  signature secret is wrong, or Razorpay never delivered. Check the dashboard
  delivery log and `docs/runbooks/failing-webhooks.md`.

## 3. Payment captured but order not paid

The capture handler refuses to confirm when:

- the captured amount differs from the order total,
- the captured currency is not `INR` / the order currency,
- required fields (`id`, `order_id`, `amount`, `currency`) are missing.

In those cases the payment is marked `needs_review` with a `review_reason` and
the order is never marked paid. An amount mismatch in the expected currency is
refunded automatically using the captured amount. A currency mismatch is left in
`refund_pending` for a human because the refund must be issued in the captured
currency. **Do not override this by editing the order.**

```bash
# List everything a human must review
cd apps/api
python - <<'PY'
from sqlalchemy import select
from app.db import SessionLocal
from app.models import Payment
with SessionLocal() as db:
    for p in db.scalars(select(Payment).where(Payment.needs_review.is_(True))):
        print(p.order_id, p.provider_order_id, p.provider_payment_id,
              p.amount_paise, p.review_reason)
PY
```

Decide with the founder/finance owner:

1. If the amount/currency is wrong, refund in the Razorpay dashboard and record
   the refund reference.
2. If the capture is legitimate and the order data is wrong, treat it as a
   reconciliation incident; do not silently confirm.
3. Update the payment review fields only through a reviewed change, and write
   down why in the incident log.

## 4. Late payment after expiry

`mark_paid` handles an order that expired before the capture arrived:

- it tries to re-reserve every line in one transaction;
- if stock is available, the order becomes `paid`;
- if stock is gone, it calls the refund path and the order becomes
  `refund_pending` (or `refunded` if the gateway call succeeded).

If the order is `refund_pending`, check `order.notes` for the refund failure
reason. Retry the refund in the Razorpay dashboard if the API call failed, then
record the refund reference. There is no automatic refund retry worker.

## 5. Refund stuck in `refund_pending`

- Confirm the payment id is present. If it is missing, `order.notes` says so and
  the refund must be done manually from the Razorpay dashboard.
- If the API refund call failed, the note contains the error. Retry from the
  dashboard, then update the payment/order to `refunded` only after the gateway
  confirms it.

## 6. Close out

- Add an incident note with order id, payment id, event ids, decision and who
  decided.
- Run `make reconcile` and confirm the order no longer appears as a mismatch.
- If the cause was a code or configuration defect, fix it before the next
  release; do not just repair the row.
