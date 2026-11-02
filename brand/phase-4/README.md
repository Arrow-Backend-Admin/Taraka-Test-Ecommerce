# Phase 4 — Milestone 2

**Status: delivered 2 November 2026, awaiting founder approval.**
Phase 3 is approved as working data with its open items kept. Milestone 1 delivered
the catalogue and inventory foundation. Milestone 2 adds catalogue filters,
PostgreSQL full-text search, a live stock size selector and a guest cart with
time-boxed reservations. Checkout and payments are not started.

## What Milestone 2 adds

- Catalogue filters for category, colour, available size, minimum and maximum
  price, plus a text query.
- PostgreSQL full-text search over name, sub-category, colour and descriptions,
  backed by the GIN index `ix_products_search_tsv`. SQLite uses a
  case-insensitive substring fallback for tests and local development.
- Facet counts for categories, colours, available sizes and the price range.
- `/catalogue/{slug}/stock` returns live per-size availability with an `as_of`
  timestamp; the product page refreshes it every 30 seconds.
- Live size selector with unavailable sizes disabled and a quantity cap.
- Guest cart with a 15-minute reservation, maximum 5 units per size, 10 units and
  5 lines per cart. Removing a line, changing quantity or expiry releases the
  hold. The conditional inventory update prevents overselling the last unit.
- Checkout is explicitly unavailable. No payment, order or shipping flow exists.
- Customer-copy sanitising removes internal ladder language and unconfirmed
  return or exchange promises at seed time and again at serialisation.
- `/credits` page with every placeholder source, licence, change and visual QA
  result; linked from the storefront footer.

## Milestone 1 foundation

- Monorepo layout: `apps/storefront` (Next.js) and `apps/api` (FastAPI).
- Alembic models and initial migration for `categories`, `products`,
  `product_variants`, `inventory` and `inventory_events`.
- Seed that loads `brand/phase-3/products.json`: 30 products, 330 variants,
  5 categories and 330 inventory rows.
- Admin CRUD API for categories, products, variants and inventory.
- Public storefront catalogue page at `/catalogue`, plus a product detail page at
  `/catalogue/[slug]`.
- Publish guard: any product or variant containing `[TO CONFIRM]` cannot be
  published. The public API also hides a published row if a flag appears, so the
  storefront never renders one.
- Production publish guard: a product with any `is_placeholder` image cannot be
  published when `APP_ENV=production`, and a published product cannot be edited
  to add one.
- Development-only draft preview: `PREVIEW_DRAFTS=true` renders draft products
  with unresolved values shown as “To be confirmed”. It is ignored when
  `APP_ENV=production`.
- Launch check: `python scripts/launch_check.py` fails if a published product
  still uses a placeholder image (and also checks for unresolved fields).
- Parallel-checkout inventory test: two concurrent reservations for the last
  unit; exactly one wins.
- OpenTelemetry instrumentation for FastAPI and SQLAlchemy, disabled by default
  for local tests.

## What is deliberately not in this milestone

- Checkout, payments, orders, shipping and returns.
- Admin UI. CRUD is exposed as a bearer-token API; a UI comes later.
- Real product photography. Only temporary CC0/CC BY placeholders exist.
- Real product facts, launch stock, HSN, care, fit, weight or materials.
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
- `inventory_events` records `reservation`, `release`, `sale`, `adjustment`,
  `seed` and `dev_fixture` events. `quantity_delta` is the signed change to
  available stock.
- The development stock fixture is clearly flagged, never writes
  `launch_stock_qty` and refuses to run when `APP_ENV=production`. Launch stock
  remains `[TO CONFIRM]`.

## Placeholder photography

The canonical source list is `brand/phase-4/placeholder-sources.json`; the
generated per-image metadata is `placeholder-images.json`; the generated credits
are `image-credits.md`. The build script is `build_placeholders.py`.

Phase 3's `products.json` keeps its four-role photography brief as approved
working data. Phase 4 does not overwrite that file: the seed replaces the
`images` column with the six-role placeholder set at load time. This keeps the
approved Phase 3 catalogue auditable while the storefront gets the required
six-role placeholder set.

- Sources: Wikimedia Commons only, CC0 1.0 or CC BY 4.0. No NC, ND or SA
  licences. No Unsplash, Pexels or Pixabay API keys were available, so the
  committed set uses Wikimedia Commons.
- Roles: `hero-45`, `lateral`, `heel`, `top-down`, `sole-macro`, `on-foot`.
- Twelve category/role slots use a reviewed photograph; the other eighteen use a
  neutral grey 4:5 “Image coming” block because every candidate was branded,
  wrong-view, an illustration, a museum fragment or carried an identifiable mark
  or face.
- Every product gets six local files named
  `placeholder_<model>_<role>_4x5_v00.jpg` under
  `apps/storefront/public/placeholders/`. Sources are reused by category so no
  placeholder implies a unique product shot.
- Derivatives are centre-cropped to 4:5, resized to 800 × 1000 and saved as
  progressive JPEG. Nothing is hotlinked.
- Per-image metadata includes source URL, photographer, licence name and URL,
  licence version, retrieval date, the change (“cropped and resized”), the QA
  result and `is_placeholder=true`.
- Every placeholder is rendered with “Placeholder image, not the actual
  product”. Alt text describes the photograph, never our product.
- Placeholders must never be used in ads, social posts or packaging.

Rebuild the set with Pillow installed:

```bash
python -m pip install -r brand/phase-4/requirements.txt
python brand/phase-4/merge_sources.py
python brand/phase-4/build_placeholders.py
```

The script caches downloads in `brand/phase-4/source-images/`, and candidate
review material in `brand/phase-4/qa/`; both are ignored by git. Delete the cache
to force a fresh download.

## Verification

```text
python brand/phase-3/validate_catalogue.py
# PASS: 30 products, 330 SKUs, 15/15 GST split

cd apps/api
alembic upgrade head
python scripts/seed.py
# Seeded 30 products, 330 variants, 5 categories, 0 inventory rows.
# DEV ONLY: seeded 330 preview stock rows.
# Products with unresolved [TO CONFIRM] fields: 30/30

python -m pytest -q
# 29 passed

python scripts/launch_check.py
# LAUNCH CHECK PASSED (0 published products)

cd ../..
npm run typecheck
npm run build
```

The storefront build passes with Next.js 16.4.3. A runtime smoke test covered
catalogue filters and facets, live stock, cart add/update/remove with reservation
release, the product detail page and `/credits`.

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
- Human visual QA of the twelve retained source photographs. The model QA record
  is in `image-credits.md`; the placeholder guard blocks production use
  regardless.

## Next move

Stop here. Checkout and payments start only after explicit founder approval.
