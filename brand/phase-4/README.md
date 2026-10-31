# Phase 4 — Milestone 1

**Status: delivered 31 October 2026, awaiting founder approval.**
Phase 3 is approved as working data with its open items kept. Phase 4 Milestone 1
is the catalogue and inventory foundation only. Cart, checkout and payments are
not started.

## What is in this milestone

- Monorepo layout: `apps/storefront` (Next.js) and `apps/api` (FastAPI).
- Alembic models and initial migration for `categories`, `products`,
  `product_variants`, `inventory` and `inventory_events`.
- Seed that loads `brand/phase-3/products.json`: 30 products, 330 variants,
  5 categories and 330 inventory rows.
- Admin CRUD API for categories, products, variants and inventory.
- Public storefront catalogue page at `/catalogue`.
- Publish guard: any product or variant containing `[TO CONFIRM]` cannot be
  published. The public API also hides a published row if a flag appears, so the
  storefront never renders one.
- Parallel-checkout inventory test: two concurrent reservations for the last
  unit; exactly one wins.
- OpenTelemetry instrumentation for FastAPI and SQLAlchemy, wired from the first
  Phase 4 commit and disabled by default for local tests.

## What is deliberately not in this milestone

- Cart, checkout, payments, orders, shipping and returns.
- Admin UI. CRUD is exposed as a bearer-token API; a UI comes later.
- Real product facts, launch stock, HSN, care, fit, weight, materials or images.
- Any claim that is not already confirmed in Phase 3.

## Data and guard rules

- Every seeded product is `draft`, even though the Phase 3 JSON says `concept`.
- A product publishes only when every product and variant string is free of
  `[TO CONFIRM]`.
- Editing a published product or variant to add a flag returns `409`; adding a
  flagged variant to a published product also returns `409`. Unpublish first.
- Public catalogue queries return only `published` products. As defence in
  depth, a forced-published product with a flag is skipped and never serialised.
- Inventory reservations use one conditional SQL `UPDATE`:
  `reserved + qty` only when `on_hand - reserved >= qty`. The database picks the
  winner; the application does not read-then-write.
- `inventory_events` records `reservation`, `release`, `sale`, `adjustment` and
  `seed` events. `quantity_delta` is the signed change to available stock.

## Verification

```text
python brand/phase-3/build_catalogue.py
python brand/phase-3/validate_catalogue.py
# PASS: 30 products, 330 SKUs, 15/15 GST split

cd apps/api
alembic upgrade head
python scripts/seed.py
# Seeded 30 products, 330 variants, 5 categories, 330 inventory rows.
# Products with unresolved [TO CONFIRM] fields: 30/30

python -m pytest -q
# 10 passed
```

The storefront build passes with Next.js 16.4.3. A runtime smoke test rendered
the empty catalogue and a resolved test product, with no `[TO CONFIRM]` value in
either response.

## Open items carried forward

- Product facts, landed cost, HSN and launch stock: manufacturer / founder / CA.
- GST threshold basis and discount treatment: CA.
- Reverse-logistics cost per exchange: 3PL.
- Exchange window, return shipping and “twice” basis: founder.
- Fair-use conditions and post-30-day defect route: legal.
- Name clearance, native-speaker test, 6 mm print proof and self-hosted TTF
  legibility re-run.
- Master-prompt schema gaps in `schema-gap-report.md`: sub-category, audience,
  15-word summary, 120-word description, exactly five feature bullets, 2–4
  colourways, launch stock per variant, six image roles, SEO meta length.

## Next move

Stop here. Wait for founder approval before cart, checkout or payments.
