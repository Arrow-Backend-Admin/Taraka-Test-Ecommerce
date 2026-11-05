# Runbook: stock mismatch

Use this when `make reconcile` reports inventory problems, when a customer sees
stock that cannot be bought, or after a crash during checkout.

## What reconciliation checks

`apps/api/app/services/reconciliation.py` compares:

- `order.total_paise` against the sum of line totals plus shipping;
- `order.subtotal_paise` / `order.gst_paise` against the line sums;
- each line: `unit_price × quantity = line_total` and
  `taxable + GST = line_total`;
- paid orders against captured payments and `paid_at`;
- captured amounts against order totals;
- `refunded_paise` against `amount_paise`;
- inventory: `on_hand >= 0`, `reserved >= 0`, `reserved <= on_hand`;
- `inventory.reserved` against the event-derived reserved count;
- sold lines against their `:sale` inventory event and reserved lines against
  their reservation event.

## 1. Run it

```bash
cd apps/api
make reconcile          # from the repo root: make reconcile
```

Exit code is non-zero when any mismatch is found. The output is the report.

## 2. Read the mismatch classes

### `reserved` exceeds `on_hand`, or negative values

This should be impossible while the database CHECK constraints are active. If it
appears:

- stop writes to the affected variants;
- check whether someone disabled constraints (`PRAGMA
  ignore_check_constraints` on SQLite, or a manual `ALTER TABLE` on PostgreSQL);
- inspect the reservation/release/sale events for the variant:

```bash
cd apps/api
python - <<'PY'
from sqlalchemy import select
from app.db import SessionLocal
from app.models import InventoryEvent

variant_id = 0  # replace
with SessionLocal() as db:
    for e in db.scalars(
        select(InventoryEvent)
        .where(InventoryEvent.variant_id == variant_id)
        .order_by(InventoryEvent.created_at)
    ):
        print(e.created_at, e.event_type, e.quantity_delta, e.reference)
PY
```

Do not "fix" stock by editing `inventory` directly. Write an `adjustment` event
through the inventory service so the audit trail stays complete, and record who
approved it.

### `reserved` differs from event-derived reserved

The counter and the event log disagree. Find the first divergence, then decide:

- if a release or sale event is missing, determine whether the order actually
  expired/paid;
- if the counter is wrong, post a correcting `adjustment` event with a note;
- never delete events.

### Sold line without a sale event

A paid order line has `stock_state = 'sold'` but no `<reservation>:sale` event.
This means the sale commit was interrupted. Re-run the sale commit for the order
through the service (not by hand) so the event is written, then reconcile again.
If the inventory already reflects the sale, investigate before writing anything.

### Reserved line without a reservation event

The order line says `reserved` but the event log has no reservation. Check the
order status and `reservation_expires_at`. If the order is active and stock is
held, the event is missing; if the order is expired, the line should be
`released`. Resolve through the expiry/release service, not by editing rows.

### Total or GST arithmetic mismatch

These indicate a write path bypassed the money service. Do not adjust the order
to match a guess. Determine the correct values from the order snapshot and the
GST rule in `apps/api/app/services/money.py`, then repair through a reviewed
migration or service call with the reason recorded.

## 3. Prevent recurrence

- Keep the database CHECK constraints; do not run with them disabled.
- Keep the reservation expiry sweeper scheduled (`make expire` under cron or the
  platform scheduler; see the API README).
- Keep the deadlock/serialization retry enabled.
- Run `make reconcile` nightly and treat a non-zero exit as a page.
