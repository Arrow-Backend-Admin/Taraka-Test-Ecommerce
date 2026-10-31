# Master-prompt schema gap report

**Phase 4 · 31 October 2026 · working data**

Phase 3 is approved as working data with its open items kept. This report compares the inferred Phase 3 schema (`brand/phase-3/product-schema.md`) with the master-prompt field list supplied by the founder. It does not resolve product facts; every construction, material, weight, fit, grip, test and care field remains `[TO CONFIRM]`.

## Summary

- **Covered:** product name; SKU pattern; category; materials; weight; fit notes; size table; price and MRP fields; tax category; care; SEO title and meta description fields; image filenames.
- **Partial:** category sub-category and audience; 5 feature bullets; price versus MRP; SEO meta length; image count.
- **Missing:** 15-word summary; 120-word description; 2–4 colourways per product; launch stock per variant; two of the six image filenames.
- **Critical for Phase 4:** launch stock per variant, a stable colourway model, and an explicit sub-category/audience taxonomy.

## Field-by-field comparison

| Master-prompt field | Inferred Phase 3 field(s) | Status | Gap / action |
|---|---|---|---|
| Product name | `name` | Covered | — |
| SKU pattern | `sku_pattern`, `sku_prefix`, variant `sku` | Covered | `MODEL-COLOUR-SIZE`; 330 unique SKUs. |
| Category | `category`, `category_code`, `category_slug` | Covered | Five categories. |
| Sub-category | — | **Missing** | `silhouette` is descriptive, not a taxonomy. Add `sub_category` (e.g. low-top, running, slide, strap, boot). |
| Audience | `gender`, `age_group` | **Partial** | Both are broad attributes, not a target audience. Add `audience` (e.g. urban India, 22–34, unisex). |
| 15-word summary | `short_description` | **Gap** | Current summaries are 8–24 words; no fixed 15-word field. Add `summary_15w` and a word-count check. |
| 120-word description | `long_description` | **Gap** | Current descriptions are 31–47 words; no 120-word field. Add `description_120w`; do not pad with unverified facts. |
| 5 feature bullets | `features` | **Partial** | Every product has 6 items: five positioning/policy bullets plus a construction flag. Add `feature_bullets` with exactly five publishable bullets; keep the construction flag separate. |
| Upper material | `upper_material` | Covered, unresolved | `[TO CONFIRM: manufacturer]`. |
| Midsole material | `midsole_material` | Covered, unresolved | `[TO CONFIRM: manufacturer]`. |
| Outsole material | `outsole_material` | Covered, unresolved | `[TO CONFIRM: manufacturer]`. |
| Lining material | `lining_material` | Covered, unresolved | `[TO CONFIRM: manufacturer]`. |
| Weight | `weight_g` | Covered, unresolved | `[TO CONFIRM: manufacturer]`; 268 g is not used. |
| Fit notes | `fit_note`, `fit_recommendation` | Covered, unresolved | `[TO CONFIRM: manufacturer]`; no true-to-size or wide-fit claim. |
| 2–4 colourways (name, HEX) | `colour`, `colour_code`, `colour_hex` | **Gap** | Each product is a single colourway. There is no model-level `colourways` array with 2–4 entries. Add it; do not invent extra colourways. |
| Sizes with UK/EU/US/cm table | `variants`, `size_system.rows`, `size-guide.csv` | Covered | UK 3–13, 11 whole sizes; every cm value is `[TO CONFIRM: last]`. |
| Price and MRP | `price_inr`, `mrp_inr`, `price_basis` | **Partial** | Both price fields are equal in the concept. There is no separate selling price or discount price. Add `sale_price_inr` only when a discount model exists. |
| Tax category | `gst_rate`, `gst_rate_pct`, `gst_bucket`, `hsn` | Covered, unresolved | 5%/18% modelled; HSN is `[TO CONFIRM: CA]`. |
| Launch stock per variant | `stock_status` | **Missing** | No quantity. Add `launch_stock_qty` per variant and seed inventory from it. |
| Care instructions | `care` | Covered, unresolved | `[TO CONFIRM: manufacturer]`. |
| SEO title (60 chars) | `seo_title` | Covered | Current titles are 22–31 characters, within 60. |
| Meta description (155 chars) | `seo_description` | **Gap** | Current descriptions are 161–256 characters, over 155. Add a length check and rewrite without new claims. |
| 6 image filenames | `images` | **Gap** | Four roles per product: `hero-45`, `side-profile`, `sole-macro`, `on-foot-34`. Add two roles, e.g. `detail-45` and `unboxing-45`, or revise the master list to four. |

## What Phase 4 Milestone 1 implements

- Adds nullable model columns for `sub_category`, `audience`, `summary_15w`, `description_120w`, `feature_bullets`, `colourways` and `sale_price_inr`; adds `launch_stock_qty` per variant.
- Seeds the Phase 3 data without inventing product facts. The seed maps the Phase 1 audience target, the single Phase 3 colourway and the five existing safe feature bullets where present. Missing content stays null or empty.
- Keeps the publish guard on every product and variant string that contains `[TO CONFIRM]`. A separate content-completeness check can flag missing master-prompt fields before launch.
- Stores images as a JSON list. The four-image Phase 2 set remains the current asset brief; no extra image filenames are invented.
- Adds `apps/api/scripts/seed.py`, the Alembic schema and the admin CRUD API. See `README.md` in this folder for verification.

## Decision needed

1. **Colourway model:** keep one colourway per product for v1, or group 2–4 colourways under one model? The current 30 products are 30 model-colour records.
2. **Image set:** confirm six roles, or approve four as the v1 set.
3. **Launch stock:** supply a quantity per variant, or keep inventory at zero until the first buy.
4. **Content length:** confirm the 15-word summary and 120-word description are hard requirements. They cannot be filled with unverified product facts.
