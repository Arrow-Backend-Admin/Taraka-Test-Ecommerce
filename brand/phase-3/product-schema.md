# Product schema — Sāntvana Phase 3

**Phase 3 · 31 October 2026 · concept only**
This is the data contract for the 30-product catalogue. The generator `build_catalogue.py` is the single source of truth; `products.json`, the CSVs, the size guide and the seed script are derived from it.

The referenced “master prompt” field list is not in this repository. This schema covers the fields needed to build a product page, cart line, tax line, size guide, seed and merchandising plan. If the master prompt has extra fields, add them to `build_catalogue.py` and regenerate; do not hand-edit the generated files.

---

## 1. Files

| File | Grain | Rows | Use |
|---|---|---:|---|
| `products.json` | One product with nested variants and images | 30 products / 330 variants | Application import, seed, content. |
| `products.csv` | One product | 30 | Merchandising, buying, review. |
| `skus.csv` | One SKU | 330 | Inventory, cart, size-level price/tax. |
| `size-guide.csv` | One UK size | 11 | Storefront size table. |
| `seed.py` | SQLAlchemy 2.0 models | 30 / 330 | PostgreSQL seed. |
| `fields-to-confirm.csv` | One product field or SKU cm value | 1,085 | Manufacturer, CA, legal, 3PL follow-up. |

---

## 2. Top-level fields

| Field | Type | Notes |
|---|---|---|
| `schema_version` | string | `1.0.0`. |
| `generated_at` | date | `2026-10-31`. |
| `brand` | string | `Sāntvana`; concept, not cleared. |
| `status` | string | `concept - product facts unconfirmed; not for production`. |
| `currency` | string | `INR`. |
| `market` | string | `India only`. |
| `price_band_inr` | array[int] | `[2299, 4999]`. |
| `core_price_band_inr` | array[int] | `[2299, 4999]`; reconciled with the Phase 1 band on 31 October 2026. |
| `catalogue` | object | Counts: 30 products, 5 categories, 6 per category, 15/10/5 tiers, 15/15 GST buckets, 330 SKUs, 11 sizes. |
| `gst_rule` | object | Notification reference, headings, threshold, rates, basis, CA flag and discount note. |
| `size_system` | object | UK 3–13, whole sizes, half-size/width flags, cm status and the 11-row table. |
| `image_convention` | object | Pattern, 4:5 aspect, four roles, storage and release flags. |
| `claims_register` | object | Confirmed policy claims, banned v1 claims, source. |
| `placeholders_not_used` | array[string] | 268 g and 4 mm lugs are explicitly not carried into the catalogue. |
| `notes` | string | Concept, name and cost caveats. |
| `products` | array[object] | The 30 product records. |

---

## 3. Product identity and merchandising fields

| Field | Type | Notes |
|---|---|---|
| `product_id` | string | `MODEL-COLOUR`, e.g. `SN-MER-CHK`. Primary key in `products`. |
| `sku_prefix` | string | Same as `product_id`; used to build SKUs. |
| `sku_pattern` | string | `MODEL-COLOUR-SIZE`. |
| `name` | string | Concept model name, e.g. `Meridian Low`. Not trademark cleared. |
| `slug` | string | `meridian-low-chalk`. |
| `category` | string | Sneakers, Running, Everyday, Sandals, Boots. |
| `category_code` | string | `SN`, `RN`, `EV`, `SD`, `BT`. |
| `category_slug` | string | Lowercase category. |
| `tier` | string | `good`, `better`, `best`. |
| `tier_label` | string | `Good`, `Better`, `Best`. |
| `model_code` | string | `SN-MER`. |
| `colour` | string | Chalk, Ink, Clay, Bone, Moss, Slate, Sand, Ground. |
| `colour_code` | string | `CHK`, `INK`, `CLY`, `BON`, `MOS`, `SLT`, `SND`, `GRD`. |
| `colour_hex` | string | Concept palette hex. |
| `silhouette` | string | Design descriptor, not a material or performance fact. |
| `gender` | string | `Unisex`. |
| `age_group` | string | `Adult`. |
| `season` | string | `All year`, except Sandals `Summer`. |
| `drop` | string | `Drop 01`. |
| `launch_date` | string | `[TO CONFIRM: founder]`. |
| `status` | string | `concept`. |
| `name_status` | string | `concept label; not trademark cleared`. |
| `hero` | boolean | 5 heroes, one per category. |
| `hero_reason` | string/null | Merchandising rationale; null for non-heroes. |
| `restock_priority` | string | `A` hero, `B` better/best, `C` good. |
| `size_run` | string | `UK 3-13`. |
| `size_system` | string | `UK whole sizes only in v1`. |
| `sku_count` | integer | 11. |

---

## 4. Commercial and tax fields

| Field | Type | Notes |
|---|---|---|
| `price_inr` | integer | GST-inclusive MRP. |
| `mrp_inr` | integer | Same as `price_inr` in the concept. |
| `price_basis` | string | `GST-inclusive MRP`. |
| `gst_rate` | number | `0.05` at or below ₹2,500; `0.18` above. |
| `gst_rate_pct` | integer | `5` or `18`. |
| `gst_bucket` | string | `at_or_below_2500` or `above_2500`. |
| `gst_amount_inr` | number | Price minus net revenue. |
| `net_revenue_inr` | number | `price ÷ (1 + rate)`. |
| `target_landed_cost_inr` | number | **Planning assumption, not a supplier quote.** |
| `cost_basis` | string | `planning assumption; not a supplier quote`. |
| `gross_margin_inr` | number | Net revenue minus target landed cost. |
| `gross_margin_pct` | number | Gross margin ÷ net revenue × 100. |
| `margin_target_low_pct` | integer | Lower bound for the category/tier. |
| `margin_target_high_pct` | integer | Upper bound. |
| `margin_target_pct` | string | Display label, e.g. `48–51%`. |
| `discount_flip_threshold_pct` | number/null | Rounded planning discount that takes the price to ₹2,500; null for good-tier products. |
| `discount_flip_note` | string | Plain-language note and `[TO CONFIRM: CA]` flag. |
| `hsn` | string | `[TO CONFIRM: CA]`. |
| `hsn_candidates` | array[string] | Candidate headings 6401–6405 for the category. |
| `legal_metrology` | string | `[TO CONFIRM: legal]` — MRP, origin, manufacturer, net quantity, care. |

The full per-product table is in `gst-and-pricing.md` §6 and `pricing-table.md`. The tax rule is modelled on GST-inclusive invoice value; the CA must confirm the threshold basis.

---

## 5. Product-fact fields

Every field in this group is **`[TO CONFIRM: manufacturer]`** in the current data. Do not replace a flag with a number, material or claim until the factory has supplied it in writing.

| Field | Notes |
|---|---|
| `manufacturer` | Legal name and address for the label. |
| `country_of_origin` | Legal label requirement. |
| `upper_material` | Exact material and composition. |
| `lining_material` | Exact material and composition. |
| `insole_material` | Exact material and composition. |
| `midsole_material` | Exact material and composition. |
| `outsole_material` | Exact material and composition. |
| `sole_compound` | Exact compound; no grip/durability claim without test data. |
| `weight_g` | Sample copy's 268 g is a placeholder and is not used. |
| `lug_depth_mm` | Sample copy's 4 mm lugs are a placeholder and are not used. |
| `drop_mm` | Heel-to-toe drop and measurement method. |
| `closure` | Lace, strap or zip type and hardware. |
| `heel_height_mm` | Measured heel height. |
| `toe_shape` | Last and toe shape. |
| `last_width` | Width/last; do not claim wide fit. |
| `water_resistance` | No waterproof claim without test data. |
| `fit_note` | No “true to size” or “wide fit” claim until measured. |
| `fit_recommendation` | No recommendation until the last is checked. |
| `grip_claim` | No grip claim without protocol and result. |
| `test_claim` | No test claim without protocol and result. |
| `care` | Care instructions for label and PDP. |

`performance_claims` is an empty array. `claims` contains only the two confirmed policy claims: free size exchange twice and 30-day returns from delivery.

---

## 6. Content fields

| Field | Notes |
|---|---|
| `short_description` | Positioning copy; no material, fit or performance fact. |
| `long_description` | Adds the “pending manufacturer confirmation” caveat. |
| `features` | Silhouette, colour, size run, policy claims and a construction flag. |
| `tags` | Category, tier, colour, season, drop. |
| `seo_title` | Model, colour, brand. |
| `seo_description` | Description plus policy and confirmation caveat. |
| `claims` | Array of `{claim, status, evidence}`. Only confirmed policy claims. |

---

## 7. Image fields

Each product has four images, all 4:5, following the Phase 2 convention:

| Role | Filename pattern | Alt text |
|---|---|---|
| `hero-45` | `drop-01_<slug>_hero-45_4x5_v01.jpg` | Product, colour, silhouette, low three-quarter on concrete. |
| `side-profile` | `drop-01_<slug>_side-profile_4x5_v01.jpg` | Side profile. |
| `sole-macro` | `drop-01_<slug>_sole-macro_4x5_v01.jpg` | Sole detail. |
| `on-foot-34` | `drop-01_<slug>_on-foot-34_4x5_v01.jpg` | Worn on a city pavement, three-quarter. |

Each image object has `role`, `filename`, `storage_key`, `aspect`, `alt` and `status`. `status` is `brief only; no asset`. Photographer credit and model/location releases are flagged at the top level.

---

## 8. Variant fields

Each product has 11 variants, UK 3–13, whole sizes only.

| Field | Notes |
|---|---|
| `sku` | `MODEL-COLOUR-SIZE`, e.g. `SN-MER-CHK-UK7`. |
| `size_uk` | `UK 3` … `UK 13`. |
| `size_eu` | Nominal EU conversion. |
| `size_us_men` | Nominal US men's conversion. |
| `size_us_women` | Nominal US women's conversion. |
| `foot_length_cm` | Nominal foot length, not insole length. |
| `foot_length_cm_status` | `[TO CONFIRM: last]` on every variant. |
| `price_inr` | Inherited from product. |
| `gst_rate` | Inherited. |
| `net_revenue_inr` | Inherited. |
| `target_landed_cost_inr` | Inherited. |
| `gross_margin_inr` | Inherited. |
| `gross_margin_pct` | Inherited. |
| `stock_status` | `not_allocated`. |

The cm values are a conversion table, not a fit guarantee. The last must confirm them before publishing. Half sizes and width are `[TO CONFIRM: manufacturer]`.

---

## 9. `[TO CONFIRM]` convention

| Owner | Meaning |
|---|---|
| `manufacturer` | Factory must supply the fact in writing. |
| `CA` | Chartered accountant must confirm the tax treatment. |
| `last` | The actual last must confirm the cm conversion. |
| `founder` | Founder must set the commercial or policy term. |
| `legal` | Policy, label or release review. |
| `3PL` | Reverse-logistics partner must quote. |
| `photography` | Credit and asset status. |
| `ops` | Resale recovery or operational assumption. |
| `attorney` | Name clearance. |

`fields-to-confirm.csv` lists every occurrence. `fields-to-confirm.md` summarises by field. Do not remove a flag without a source and a date.

---

## 10. Seed mapping

`seed.py` maps:

- `products.json` → `products` table, with `product_id` → `products.id`.
- `variants` → `product_variants`, with `product_id` foreign key and `sku` primary key.
- Nested `features`, `tags`, `hsn_candidates`, `performance_claims`, `claims` and `images` → JSON columns.
- Money and percentages → `Numeric`; `price_inr` → `Integer`.

The script is idempotent (`session.merge`) and requires `DATABASE_URL`; it has no hard-coded credentials. `--create-tables` is for development only. Use Alembic in production.

---

## 11. Change rule

1. Change the data or copy in `build_catalogue.py`.
2. Run `python brand/phase-3/build_catalogue.py`.
3. Run `python brand/phase-3/validate_catalogue.py`.
4. Run `python brand/phase-3/seed.py --dry-run`.
5. Do not hand-edit `products.json`, the CSVs or the generated Markdown; the next build will overwrite them.
