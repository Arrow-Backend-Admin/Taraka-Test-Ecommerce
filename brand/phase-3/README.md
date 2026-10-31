# Phase 3 — catalogue and commercial model

**Sāntvana · 31 October 2026 · concept only**
Phase 1 is approved as v1.1. Phase 2 is approved as a concept visual system, with its open items kept. **Phase 3 is approved as working data on 31 October 2026, with its open items kept.** No print, domain or ad spend until the attorney opinion and native-speaker connotation test are back. The name is not cleared.

---

## What this phase delivers

| Deliverable | Where | Status |
|---|---|---|
| 30 products, 5 categories × 6, with a good/better/best ladder | `products.json`, `products.csv` | Concept data |
| 330 SKUs in `MODEL-COLOUR-SIZE`, UK 3–13 | `skus.csv` | Concept data |
| GST and price model, net revenue and margin per product | `gst-and-pricing.md`, `pricing-table.md` | Planning model; CA confirmation needed |
| Free exchange twice, 30-day returns, no warranty in v1 | `policies.md` | Copy draft; legal/founder review needed |
| Reverse-logistics cost per exchange and margin impact | `policies.md` §4 | Planning model; 3PL quote needed |
| Size guide with UK/EU/US/cm and last flags | `size-guide.md`, `size-guide.csv` | Conversion table; last must confirm |
| Hero products, margin targets, 90-day launch plan, two drops a year | `merchandising-plan.md` | Concept plan |
| SQLAlchemy 2.0 seed script | `seed.py` | Tested against SQLite; PostgreSQL needs `psycopg` |
| Fields to confirm | `fields-to-confirm.md`, `fields-to-confirm.csv` | 1,085 rows |
| Data contract and field meanings | `product-schema.md` | Concept schema |
| Reproducible generator and validator | `build_catalogue.py`, `validate_catalogue.py` | Passing |

---

## The range in one screen

- **30 products:** 5 categories × 6 products.
- **Tiers:** 15 good, 10 better, 5 best.
- **GST line:** 15 products at or below ₹2,500 (5%), 15 above (18%).
- **Ladder:** ₹2,299 / ₹2,399 / ₹2,499 → ₹3,499 / ₹3,999 → ₹4,999.
- **No product between ₹2,500 and ₹3,499.** This avoids the GST dead zone at full price and keeps the rate the same under either threshold interpretation. The Phase 1 price band is reconciled to **₹2,299–₹4,999**.
- **330 SKUs:** 30 products × 11 whole sizes, UK 3–13.
- **5 heroes:** Meridian Low, Tempo, Daily, Courtyard, Halt — one per category.
- **Images:** 4 per product, all 4:5, following the Phase 2 convention: `drop-01_<slug>_<role>_4x5_v01.jpg`.
- **Average planning net revenue:** ₹2,907.49. **Average planning gross margin:** ₹1,495.83 (51.45%), before reverse logistics and other costs.

---

## Read this first

1. **Every product fact is unconfirmed.** Weight, materials, lug depth, sole compound, fit, grip, test claims, care and country of origin are `[TO CONFIRM: manufacturer]`. The Phase 1 sample copy's **268 g** and **4 mm lugs** are placeholders and are **not** carried into this catalogue.
2. **The GST model is not tax advice.** A chartered accountant must confirm whether the ₹2,500 threshold is measured before or after tax, and how a discount that crosses the line is treated. See `gst-and-pricing.md` §1 and §7.
3. **Costs and margins are planning assumptions.** The landed costs, ₹300 per-exchange reverse-logistics cost and 45% margin floor are not supplier or 3PL quotes.
4. **Policy copy is a draft.** The exchange window, return shipping, fair-use conditions and post-30-day defect route are unconfirmed. See `policies.md` §6.
5. **The model names are concept labels.** They are not trademark cleared. The name Sāntvana is not cleared either.
6. **The master-prompt field list is not in this repository.** `product-schema.md` documents the inferred schema. If the original list has extra fields, add them to `build_catalogue.py` and regenerate.

---

## Run it

```bash
# Rebuild the JSON, CSVs and generated Markdown
python brand/phase-3/build_catalogue.py

# Validate counts, GST/margin math, SKU patterns, image names and flags
python brand/phase-3/validate_catalogue.py

# Validate the seed payload without a database
python brand/phase-3/seed.py --dry-run

# Install the seed dependencies (not needed for --dry-run)
pip install "SQLAlchemy>=2.0" "psycopg[binary]>=3.2"

# Development only: create tables and seed PostgreSQL 16
$env:DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DBNAME"
python brand/phase-3/seed.py --create-tables

# Production: run Alembic first, then seed without --create-tables
python brand/phase-3/seed.py
```

The seed script is idempotent (`session.merge`) and has no hard-coded credentials. Do not commit `DATABASE_URL`. Use `--create-tables` only in development. The local smoke test used SQLite; PostgreSQL 16 with `psycopg` is the target.

---

## Key files

| File | What it is |
|---|---|
| `products.json` | Canonical catalogue: 30 products, 330 variants, images, tax, margins, flags. |
| `products.csv` | One row per product; flattened for merchandising review. |
| `skus.csv` | One row per SKU; size-level price, tax, cost and margin. |
| `size-guide.md` | Customer-facing conversion table and fit caveats. |
| `size-guide.csv` | Machine-readable conversion table. |
| `gst-and-pricing.md` | GST rule, ₹2,500 cliff, two interpretations, ladder, per-product table, discount bands. |
| `pricing-table.md` | Generated per-product net revenue and margin table. |
| `policies.md` | Customer copy, internal rules and reverse-logistics cost model. |
| `merchandising-plan.md` | Range architecture, heroes, margin targets, 90-day launch plan, Drop 02. |
| `fields-to-confirm.md` | Summary of every `[TO CONFIRM]` by field and owner. |
| `fields-to-confirm.csv` | Per-product, per-SKU follow-up list. |
| `product-schema.md` | Data contract and field meanings. |
| `build_catalogue.py` | Single source of truth; writes the data and generated docs. |
| `validate_catalogue.py` | Independent checks; exits non-zero on failure. |
| `seed.py` | SQLAlchemy 2.0 models and idempotent seed. |
| `../phase-4/schema-gap-report.md` | Master-prompt comparison and Phase 4 handoff. |

---

## Open items and blockers

| Item | Owner | Blocks |
|---|---|---|
| All construction, material, weight, lug, sole, fit, care and origin facts | Manufacturer | PDP, label, launch |
| Supplier landed cost and target costs | Manufacturer | Pricing, margin |
| HSN heading per product | Manufacturer + CA | Tax, invoice, label |
| Whether the ₹2,500 threshold is before or after tax | CA | Price display, discount rule |
| GST treatment when a discount crosses ₹2,500 | CA | Discounts |
| Exchange window | Founder | Policy copy |
| Whether “twice” is per order or per customer | Founder | Policy copy |
| Who pays return shipping | Founder | Policy copy |
| Fair-use conditions and post-30-day defect route | Legal | Policy copy |
| Reverse-logistics cost per exchange | 3PL | Cost model, promise |
| Resale recovery for returned pairs | Ops | Cost model |
| Drop 01 launch date and size curve | Founder | Buying, launch |
| Photography, credit and model/location releases | Photography / legal | PDP, ads |
| Name clearance and native-speaker connotation test | Attorney / native speaker | Domain, print, ads |
| Founder-supplied story facts | Founder | Public story |
| Master-prompt field list | Founder | Schema completeness |

The full list is in `fields-to-confirm.csv`; the summary is in `fields-to-confirm.md`.

---

## What is not in Phase 3

- No storefront route, cart, checkout, payment or logistics integration.
- No product photography or final image assets.
- No inventory purchase, supplier contract or 3PL contract.
- No final GST, legal or name-clearance opinion.
- No Hindi policy copy. It needs native-speaker and legal review.

---

## Guardrails

- No performance, material or fit claim without the evidence in `../strategy.md` §7.
- No numeric weight or lug depth until the manufacturer supplies it. 268 g and 4 mm lugs are not used.
- No discount into the ₹2,501–₹2,809.52 GST dead zone.
- No “free returns” claim. Only the size exchange is confirmed free.
- No “30-day exchange” claim until the founder confirms the exchange window.
- No warranty, repair or durability promise in v1.
- No inventory buy before the fit trial, supplier quote, 3PL rate and name clearance.
- No hard-coded secrets. `DATABASE_URL` is required.
