# Phase 4 — Milestone 1

**Status: delivered 1 November 2026, awaiting founder approval.**
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
- Public storefront catalogue page at `/catalogue`, plus a product detail page at
  `/catalogue/[slug]`.
- Publish guard: any product or variant containing `[TO CONFIRM]` cannot be
  published. The public API also hides a published row if a flag appears, so the
  storefront never renders one.
- Temporary placeholder photography: six roles per product, local 4:5
  derivatives, per-image metadata and `image-credits.md`.
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
- OpenTelemetry instrumentation for FastAPI and SQLAlchemy, wired from the first
  Phase 4 commit and disabled by default for local tests.

## What is deliberately not in this milestone

- Cart, checkout, payments, orders, shipping and returns.
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
- `inventory_events` records `reservation`, `release`, `sale`, `adjustment` and
  `seed` events. `quantity_delta` is the signed change to available stock.

## Placeholder photography

The canonical source list is `brand/phase-4/placeholder-sources.json`; the
generated per-image metadata is `placeholder-images.json`; the generated credits
are `image-credits.md`. The build script is `build_placeholders.py`.

Phase 3's `products.json` keeps its four-role photography brief as approved
working data. Phase 4 does not overwrite that file: the seed replaces the
`images` column with the six-role placeholder set at load time. This keeps the
approved Phase 3 catalogue auditable while the storefront gets the required
six-role placeholder set.

- Sources: six Wikimedia Commons photographs, CC0 1.0 or CC BY 4.0 only. No NC,
  ND or SA licences. No Unsplash, Pexels or Pixabay API keys were available, so
  the committed set uses Wikimedia Commons. The Unsplash-derived on-foot image
  is the CC0 review copy hosted on Wikimedia Commons.
- Roles: `hero-45`, `lateral`, `heel`, `top-down`, `sole-macro`, `on-foot`.
- Every product gets six local files named
  `placeholder_<model>_<role>_4x5_v00.jpg` under
  `apps/storefront/public/placeholders/`. The same six source photographs are
  reused across the 30 concept products so no placeholder implies a unique
  product shot.
- Derivatives are centre-cropped to 4:5, resized to 800 × 1000 and saved as
  progressive JPEG. Nothing is hotlinked.
- Per-image metadata includes source URL, photographer, licence name and URL,
  licence version, retrieval date and `is_placeholder=true`.
- Every placeholder is rendered with “Placeholder image, not the actual
  product”. Alt text describes the photograph, never our product.
- Placeholders must never be used in ads, social posts or packaging.

Rebuild the set with Pillow installed:

```bash
python -m pip install -r brand/phase-4/requirements.txt
python brand/phase-4/build_placeholders.py
```

The script caches downloads in `brand/phase-4/source-images/`, which is ignored
by git. Delete the cache to force a fresh download.

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
# 14 passed

python scripts/launch_check.py
# LAUNCH CHECK PASSED (0 published products)

cd ../..
npm run typecheck
npm run build
```

The storefront build passes with Next.js 16.4.3. A runtime smoke test rendered
the empty catalogue, a resolved test product, and the development draft preview
with placeholders and “To be confirmed”, with no `[TO CONFIRM]` value in any
response.

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
- Human visual QA of the six source photographs for third-party marks,
  identifiable faces, ground-in-frame and overcast-light compliance. The
  placeholder guard blocks production use regardless, but the source set must
  not be used externally before this review.

## Next move

Stop here. Wait for founder approval before cart, checkout or payments.
