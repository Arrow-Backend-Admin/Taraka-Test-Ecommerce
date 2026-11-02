# Sāntvana

Concept D2C footwear brand for India. Phase 1 strategy is approved as v1.1; the
naming memo is a risk memo, not a clearance opinion. Phase 2 is the bilingual
visual system: logo suite, colour, typography, imagery, graphic language,
packaging, collateral and design tokens. Phase 3 is the 30-product catalogue,
GST/pricing model, policies, size guide and merchandising plan.

**Status: concept only.** Phase 2 is approved as a concept visual system. Phase 3
is approved as working data, with its open items kept. Phase 4 Milestone 1 is
delivered; Milestone 2 adds catalogue filters, PostgreSQL full-text search, live
stock size selection and a guest cart with 15-minute reservations. Checkout and
payments are not started. No print, domain or ad spend until the attorney opinion
and native-speaker connotation test are back. The name is not cleared.

## Monorepo

| Path | Contents |
|---|---|
| `apps/storefront/` | Next.js 16 app: `/brand` concept route, `/catalogue` list and detail routes, `/credits` image credits |
| `apps/api/` | FastAPI + SQLAlchemy + Alembic catalogue and inventory API |
| `brand/strategy.md` | Phase 1 strategy, v1.1 approvals and open items |
| `brand/naming.md` | Naming risk memo, spelling policy and clearance status |
| `brand/logos/` | Legibility test, harness and decision record |
| `brand/phase-2/` | Phase 2 specs, tokens, static tests and social boards |
| `brand/phase-3/` | Phase 3 catalogue, GST/pricing, policies, size guide and merchandising |
| `brand/phase-4/` | Phase 4 schema gap report and Milestone 1 notes |

## Storefront

Node 22 or newer is recommended.

```bash
npm install
npm run dev
```

Open `http://localhost:3000` for the concept landing page,
`http://localhost:3000/catalogue` for the publish-gated catalogue,
`http://localhost:3000/credits` for placeholder sources and visual QA, and
`http://localhost:3000/brand` for the concept brand book.

The catalogue reads `API_URL` (default `http://localhost:8000`) on the server.
Browser calls for live stock and the guest cart read `NEXT_PUBLIC_API_URL`. Copy
`apps/storefront/.env.example` to `apps/storefront/.env` if the API runs
elsewhere.

The storefront shows published products only by default. For local draft review,
set `PREVIEW_DRAFTS=true` and keep `APP_ENV=development`; unresolved fields read
“To be confirmed” and every placeholder is labelled. `PREVIEW_DRAFTS` is ignored
when `APP_ENV=production`.

Build checks:

```bash
npm run typecheck
npm run build
```

## API

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

The seed loads the Phase 3 catalogue: 30 products, 330 variants, 5 categories and
330 inventory rows. Every product stays `draft` because the product facts still
contain `[TO CONFIRM]` fields. The publish guard blocks those products, and the
public catalogue never renders a flagged value.

Outside production the seed also loads a clearly flagged development stock
fixture so size selectors and the guest cart can be exercised. The fixture never
writes `launch_stock_qty`, records `dev-fixture:<sku>` inventory events and
refuses to run when `APP_ENV=production`. Pass `--no-dev-inventory` to skip it.

API docs: `http://localhost:8000/docs`. See `apps/api/README.md` for endpoints,
configuration, inventory semantics and the OpenTelemetry setup.

## Verify

```bash
# Phase 3 data
python brand/phase-3/build_catalogue.py
python brand/phase-3/validate_catalogue.py

# API
cd apps/api
python -m pytest -q
python scripts/launch_check.py

# Storefront
cd ../..
npm run typecheck
npm run build
```

The API test suite includes the parallel last-unit reservation test: two threads
reserve the same final unit, and exactly one succeeds. The launch check fails if
any published product still has a placeholder image or an unresolved field.

## Guardrails

- No material, sustainability, grip or fit claim without evidence.
- No lorem ipsum, TODO placeholders or invented product facts.
- No hard-coded secrets. `.env` files, keys and local databases are ignored.
- A product with any unresolved `[TO CONFIRM]` field cannot be published.
- The storefront must never render a `[TO CONFIRM]` value, including after a
  forced-published row.
- A product with any placeholder image cannot be published in production.
- Placeholder images are temporary, local, CC0/CC BY derivatives. They must never
  be used in ads, social posts or packaging.
- `python apps/api/scripts/launch_check.py` must fail if a published product
  still uses a placeholder image.
- Checkout and payments are not implemented. The guest cart only holds a
  time-boxed reservation; it never takes payment.
- The Devanagari wordmark has a 20 px absolute screen floor and a 6 mm measured
  print floor. Below 20 px, use the monogram or symbol.
