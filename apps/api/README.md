# Sāntvana API

FastAPI + SQLAlchemy + Alembic catalogue, inventory, orders and payments service
for the Phase 4 Milestone 3 concept storefront.

**Scope:** catalogue filters, full-text search, publish guard, inventory, guest
cart with time-boxed reservations, guest checkout, orders, Razorpay test-mode
payments, confirmation email and webhook verification. Shipping,
returns/exchanges, coupons and authentication are not implemented.

## Local setup

Use Python 3.11 or newer. PostgreSQL 16 is the target; SQLite is fine for tests
and local development.

```bash
cd apps/api
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"

cp .env.example .env
# Set DATABASE_URL and ADMIN_API_TOKEN in .env. Do not commit .env.

alembic upgrade head
python scripts/seed.py
uvicorn app.main:app --reload --port 8000
```

The seed reads `brand/phase-3/products.json` and loads 30 products, 330 variants,
5 categories and 330 inventory rows. It also attaches the six placeholder images
per product from `brand/phase-4/placeholder-images.json`. Every product stays
`draft` because the Phase 3 facts still contain `[TO CONFIRM]` fields.

Outside production the seed also loads a flagged development stock fixture so
the size selector and guest cart can be exercised. It never writes
`launch_stock_qty`, records `dev-fixture:<sku>` events and refuses to run when
`APP_ENV=production`. Use `--no-dev-inventory` to skip it, or
`--dev-inventory` to force it outside production.

For a throwaway SQLite database:

```bash
python scripts/seed.py \
  --database-url "sqlite:///./santvana-dev.db" \
  --create-tables
```

`--create-tables` is development-only. Production uses Alembic.

## Configuration

| Variable | Purpose |
|---|---|
| `APP_ENV` | `development` by default. Set `production` to enforce the placeholder publish guard and disable preview responses. `ENVIRONMENT` is accepted as an alias. |
| `DATABASE_URL` | SQLAlchemy URL. Defaults to `sqlite:///./santvana-dev.db`. |
| `ADMIN_API_TOKEN` | Bearer token for `/admin/*`. If unset, admin routes return `503`. |
| `CORS_ORIGINS` | Comma-separated storefront origins. Default `http://localhost:3000`. |
| `CART_IP_HASH_SECRET` | Salt for hashing guest IP addresses used by reservation caps. |
| `RAZORPAY_KEY_ID` | Razorpay key id. Test keys (`rzp_test_`) only in development. |
| `RAZORPAY_KEY_SECRET` | Razorpay key secret. |
| `RAZORPAY_WEBHOOK_SECRET` | HMAC secret for verifying `X-Razorpay-Signature` on webhooks. |
| `RAZORPAY_MOCK` | Set `true` for local review. Refuses to run in production. |
| `RAZORPAY_API_BASE` | Razorpay API base URL. Default `https://api.razorpay.com/v1`. |
| `ORDER_PAYMENT_WINDOW_MINUTES` | Minutes before an unpaid order expires. Default 10. |
| `STOREFRONT_URL` | Used in confirmation emails. Default `http://localhost:3000`. |
| `MAIL_ENABLED` | Set `true` to send confirmation emails via SMTP. |
| `SMTP_HOST` | SMTP host. Default `localhost` (Mailpit). |
| `SMTP_PORT` | SMTP port. Default `1025` (Mailpit). |
| `MAIL_FROM` | Sender address for transactional email. |
| `SELLER_STATE` | Seller state for GST. Placeholder: `[TO CONFIRM: founder]`. |
| `SELLER_GSTIN` | Seller GSTIN. Placeholder: `[TO CONFIRM: founder]`. |
| `OTEL_ENABLED` | Set `true` to instrument FastAPI and SQLAlchemy. Default `false`. |
| `OTEL_SERVICE_NAME` | Service name in traces. Default `santvana-api`. |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP/HTTP endpoint, e.g. `http://localhost:4318/v1/traces`. |
| `OTEL_EXPORTER_OTLP_HEADERS` | Optional `key=value,key2=value2` exporter headers. |

No credentials are committed. `.env.example` contains placeholders only. Optional
`UNSPLASH_ACCESS_KEY`, `PEXELS_API_KEY`, `PIXABAY_API_KEY`, `OPENVERSE_CLIENT_ID`
and `OPENVERSE_CLIENT_SECRET` entries are blank and are only for a future
placeholder refresh; the committed set uses Wikimedia Commons.

## Endpoints

### Public

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/health` | Liveness and telemetry state. |
| `GET` | `/health/live` | Liveness only; does not touch external services. |
| `GET` | `/health/ready` | Readiness; fails with `503` when the database is unreachable. |
| `GET` | `/catalogue` | Published, storefront-safe products only. |
| `GET` | `/catalogue?q=&category=&colour=&size=&min_price=&max_price=` | Filtered catalogue. `q` uses PostgreSQL full-text search; SQLite falls back to a case-insensitive substring match. |
| `GET` | `/catalogue/facets` | Category, colour, available-size and price facets for the same filters. |
| `GET` | `/catalogue/{slug}` | Published product detail, sizes, materials and images. |
| `GET` | `/catalogue/{slug}/stock` | Live per-size availability, with an `as_of` timestamp. |
| `GET` | `/catalogue?preview_drafts=true` | Development-only draft preview. Ignored when `APP_ENV=production`. |
| `GET` | `/catalogue/{slug}?preview_drafts=true` | Development-only draft detail. Ignored when `APP_ENV=production`. |

### Guest cart -- `santvana_cart` httpOnly cookie

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/cart` | Create a guest cart. Returns the opaque token. |
| `GET` | `/cart` | Read the cart and its reservation expiry. |
| `POST` | `/cart/items` | Add `{sku, quantity}` and reserve stock. |
| `PATCH` | `/cart/items/{id}` | Change quantity; `0` removes the line. |
| `DELETE` | `/cart/items/{id}` | Remove the line and release its reservation. |

Rules: 15-minute reservation, maximum 5 units per size, 10 units and 5 lines per
cart. Per-IP cap: max 10 units per IP; per-size cap = max(2, ceil(on_hand * 0.20)).
Reservations are released when a line is removed, the quantity changes or the
cart expires. The conditional inventory update prevents two guests reserving the
same last unit. The cart token is stored as a SHA-256 hash in `carts.token_hash`;
the raw token lives in an httpOnly `santvana_cart` cookie.

### Orders and payments

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/orders` | Create an order from the cart. Prices come from the database; GST is split per line. |
| `GET` | `/orders/{public_id}` | Read order status, items, GST split, address and seller details. |
| `POST` | `/orders/{public_id}/payment` | Retry payment (re-reserve if expired, create a new Razorpay order). |
| `POST` | `/orders/{public_id}/payment-verify` | Browser callback hint. Verifies the signature but never changes order status. |
| `POST` | `/orders/{public_id}/mock-pay` | Dev-only: sign a fake webhook and run the real confirmation path. Refused in production. |
| `POST` | `/orders/expire` | Sweep: expire all orders past their reservation window. |
| `POST` | `/webhooks/razorpay` | Razorpay webhook endpoint. Verifies raw-body HMAC signature. Idempotent and replay-safe. |

Payment is confirmed only by a signed `payment.captured` or `order.paid` webhook.
The browser callback is a UI hint. Webhooks are idempotent (`X-Razorpay-Event-Id`).
Late payments after reservation expiry attempt re-reservation; if stock is gone,
the payment is refunded. Failed/abandoned payments release stock.

Local mock payments use `POST /orders/{public_id}/mock-pay`, which signs a fake
webhook and runs the real confirmation path. Requires `RAZORPAY_MOCK=true` and
non-production `APP_ENV`.

### Admin -- `Authorization: Bearer <ADMIN_API_TOKEN>`

| Method | Path | Purpose |
|---|---|---|
| `GET/POST` | `/admin/categories` | List or create categories. |
| `GET/PATCH/DELETE` | `/admin/categories/{slug}` | Read, update or delete a category. |
| `GET/POST` | `/admin/products` | List or create products. New products are `draft`. |
| `GET/PATCH/DELETE` | `/admin/products/{id}` | Read, update or delete a draft product. |
| `POST` | `/admin/products/{id}/publish` | Publish only when every flag is resolved. |
| `POST` | `/admin/products/{id}/unpublish` | Return a product to `draft`. |
| `GET/POST` | `/admin/products/{id}/variants` | List or create variants. Creation loads launch stock into inventory. |
| `PATCH/DELETE` | `/admin/variants/{sku}` | Update or delete a variant. |
| `GET` | `/admin/inventory/{sku}` | On hand, reserved, available and version. |
| `POST` | `/admin/inventory/{sku}/adjust` | Apply a signed stock adjustment. |
| `GET` | `/admin/inventory/{sku}/events` | Inventory event ledger. |

Interactive docs are at `/docs`.

## Publish guard

`app/services/publish.py` walks every product and variant column, including JSON
lists and dictionaries, looking for `[TO CONFIRM` (case-insensitive).

- Publishing with a flag returns `409` and lists the offending paths.
- Editing a published product or variant so it gains a flag returns `409`; the
  admin must unpublish first.
- Adding a variant with a flag to a published product also returns `409`.
- The public catalogue skips any published row that still has a flag. This is
  defence in depth: bad data is hidden, not rendered.
- Public serialisation also filters individual strings, so a flag cannot leak
  through a nested feature, material, image name or SEO field.
- When `APP_ENV=production`, publishing a product with any
  `images[].is_placeholder=true` returns `409` with
  `reason: "placeholder_images"`. A published product also cannot be edited to
  add a placeholder image in production.
- In production, the public catalogue skips a forced-published product that
  still has a placeholder image.
- `GET /catalogue?preview_drafts=true` is ignored in production. In development
  it returns all products, replaces unresolved values with "To be confirmed"
  and marks each payload with `preview: true`. It never returns a raw
  `[TO CONFIRM]` value.

## Launch check

Run this against the production database before launch:

```bash
cd apps/api
python scripts/launch_check.py
```

It exits non-zero if any published product still has a placeholder image or an
unresolved `[TO CONFIRM]` field. It is a separate check from the API guard so a
forced database edit cannot slip through unnoticed.

## Operations

Run these from the repository root (or see the `Makefile`):

| Command | Purpose |
|---|---|
| `make preflight` | One launch gate: mock payments, wrong-environment keys, dev fixture, placeholder images, unresolved fields, seller GSTIN/state, static admin token, migrations at head. Exits non-zero on any failure. |
| `make reconcile` | Nightly read-only reconciliation of orders, payments, inventory and inventory events. Exits non-zero on mismatch. |
| `make outbox` | Send pending confirmation emails from the durable outbox. Run on a schedule. |
| `make expire` | Release stock held by orders past their payment window. Run on a schedule (cron or the platform scheduler). |
| `make backup` | PostgreSQL custom-format dump (or SQLite copy). |
| `make restore DUMP=...` | Destructive restore. Read the runbook first. |

Runbooks: `../../docs/runbooks/` covers stuck payments, failing webhooks,
stock mismatch and backup/restore. Known gaps are in
`../../docs/known-limitations.md`. The real Razorpay test-mode drill is
`../../brand/phase-4/razorpay-test-runbook.md`.

Health endpoints: `/health/live` is process liveness; `/health/ready` returns
`503` when the database cannot answer a trivial query. The API disposes its
connection pool on shutdown.

## Inventory concurrency

Reservations use a single conditional `UPDATE`:

```sql
UPDATE inventory
SET reserved = reserved + :qty, version = version + 1
WHERE variant_id = :id AND on_hand - reserved >= :qty;
```

The database decides the winner. There is no read-then-write race. The test
`tests/test_inventory_concurrency.py` starts two threads against the last unit
and asserts exactly one reservation succeeds. `inventory_events` records the
reservation, release, sale, adjustment or seed event.

`reserve_stock`, `release_stock`, `commit_sale` and `adjust_stock` are in
`app/services/inventory.py`. `commit_sale` is called by the webhook handler
when a payment is confirmed.

## Tests

```bash
cd apps/api
python -m pytest -q
```

Coverage includes:

- public catalogue and detail serialisation;
- publish guard on product fields and variant fields;
- forced-published unresolved data hidden from the storefront;
- production placeholder publish guard and public filtering;
- development draft preview with "To be confirmed" and placeholder notices;
- catalogue filters, facets, search and live stock;
- guest cart add/update/remove, line and unit limits, oversell guard and expiry;
- customer-copy sanitising and the flagged dev inventory fixture;
- parallel last-unit reservation;
- seed counts and idempotency;
- telemetry disabled by default;
- order creation from database prices with per-line GST split;
- Indian address and pincode validation;
- Razorpay signature verification failures;
- replayed webhook events (idempotent);
- failed payment release and retry;
- expired reservation retry and late payment re-reserve/refund;
- payment amount mismatch refund;
- browser verify hint (never changes order state);
- double-submit guard;
- mock-pay dev-only shortcut;
- live-key guard, mock guard, webhook-secret guard;
- concurrent duplicate-capture on PostgreSQL (skipped on SQLite).

The suite currently reports **141 passed, 4 skipped** locally (PostgreSQL-only,
Mailpit-only and PostgreSQL restore tests skip without those services; CI runs
them).

## Database model

- `categories`
- `products`
- `product_variants`
- `inventory` -- one row per variant, `on_hand`, `reserved`, optimistic `version`
- `inventory_events` -- append-only ledger with a unique optional `reference`
- `carts` -- opaque guest token, status and reservation expiry
- `cart_items` -- reserved line with unit price and reservation reference
- `orders` -- guest order with address, seller details, GST split, status state machine
- `order_items` -- price and name snapshots, per-line GST, stock_state (reserved/sold/released)
- `payments` -- Razorpay order id, payment id, status, refund tracking
- `webhook_events` -- idempotent event intake keyed by `X-Razorpay-Event-Id`
- `email_outbox` -- durable confirmation-email queue with attempt count and last error

Migrations:

- `alembic/versions/b137d92f11bf_initial_catalogue_and_inventory.py`
- `alembic/versions/c4a1f2d3e5b6_guest_carts_and_search.py` -- carts, cart items and
  the PostgreSQL-only GIN index `ix_products_search_tsv`. SQLite gets no index
  and uses the fallback search.
- `alembic/versions/e6c3f9a2b8d1_orders_payments_webhooks.py` -- orders, order items,
  payments and webhook events.
- `alembic/versions/f7d4a1c9e2b3_hardening_outbox_and_checks.py` -- payment review
  fields, the email outbox, extra CHECK constraints and outbox indexes. Webhook
  idempotency is the unique `webhook_events.event_id` added in the previous
  migration.

## Open items

Product facts, landed cost, HSN, launch stock, GST threshold interpretation,
reverse logistics, policy windows and legal review are still open. The API
stores these as flags or nullable fields; it does not invent values. See
`../../brand/phase-4/schema-gap-report.md` and `../../brand/phase-3/README.md`.

## Next milestone

Stop here. Shipments, returns/exchanges, coupons and authentication start only
after explicit founder approval. Cash on delivery is deferred; see
`../../brand/phase-4/cod-decision-note.md`.
