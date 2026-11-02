# Sāntvana API

FastAPI + SQLAlchemy + Alembic catalogue and inventory service for the Phase 4
Milestone 2 concept storefront.

**Scope:** catalogue filters, full-text search, publish guard, inventory and a
guest cart with time-boxed reservations. Checkout, payments, orders and shipping
are not implemented.

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
| `GET` | `/catalogue` | Published, storefront-safe products only. |
| `GET` | `/catalogue?q=&category=&colour=&size=&min_price=&max_price=` | Filtered catalogue. `q` uses PostgreSQL full-text search; SQLite falls back to a case-insensitive substring match. |
| `GET` | `/catalogue/facets` | Category, colour, available-size and price facets for the same filters. |
| `GET` | `/catalogue/{slug}` | Published product detail, sizes, materials and images. |
| `GET` | `/catalogue/{slug}/stock` | Live per-size availability, with an `as_of` timestamp. |
| `GET` | `/catalogue?preview_drafts=true` | Development-only draft preview. Ignored when `APP_ENV=production`. |
| `GET` | `/catalogue/{slug}?preview_drafts=true` | Development-only draft detail. Ignored when `APP_ENV=production`. |

### Guest cart — `X-Cart-Token: <token>`

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/cart` | Create a guest cart. Returns the opaque token. |
| `GET` | `/cart` | Read the cart and its reservation expiry. |
| `POST` | `/cart/items` | Add `{sku, quantity}` and reserve stock. |
| `PATCH` | `/cart/items/{id}` | Change quantity; `0` removes the line. |
| `DELETE` | `/cart/items/{id}` | Remove the line and release its reservation. |

Rules: 15-minute reservation, maximum 5 units per size, 10 units and 5 lines per
cart. Checkout is deliberately unavailable in this milestone. Reservations are
released when a line is removed, the quantity changes or the cart expires. The
conditional inventory update prevents two guests reserving the same last unit.

### Admin — `Authorization: Bearer <ADMIN_API_TOKEN>`

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
  it returns all products, replaces unresolved values with “To be confirmed”
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
`app/services/inventory.py`. `commit_sale` exists for the later checkout
milestone but is not called by any route yet.

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
- development draft preview with “To be confirmed” and placeholder notices;
- catalogue filters, facets, search and live stock;
- guest cart add/update/remove, line and unit limits, oversell guard and expiry;
- customer-copy sanitising and the flagged dev inventory fixture;
- parallel last-unit reservation;
- seed counts and idempotency;
- telemetry disabled by default.

The suite currently reports **29 passed**.

## Database model

- `categories`
- `products`
- `product_variants`
- `inventory` — one row per variant, `on_hand`, `reserved`, optimistic `version`
- `inventory_events` — append-only ledger with a unique optional `reference`
- `carts` — opaque guest token, status and reservation expiry
- `cart_items` — reserved line with unit price and reservation reference

Migrations:

- `alembic/versions/b137d92f11bf_initial_catalogue_and_inventory.py`
- `alembic/versions/c4a1f2d3e5b6_guest_carts_and_search.py` — carts, cart items and
  the PostgreSQL-only GIN index `ix_products_search_tsv`. SQLite gets no index
  and uses the fallback search.

## Open items

Product facts, landed cost, HSN, launch stock, GST threshold interpretation,
reverse logistics, policy windows and legal review are still open. The API
stores these as flags or nullable fields; it does not invent values. See
`../../brand/phase-4/schema-gap-report.md` and `../../brand/phase-3/README.md`.

## Next milestone

Stop here. Checkout and payments start only after explicit founder approval.
