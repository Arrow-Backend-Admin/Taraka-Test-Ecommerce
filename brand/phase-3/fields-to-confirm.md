# Fields to confirm - Sāntvana Phase 3

**Phase 3 · 31 October 2026 · concept only**
Every `[TO CONFIRM]` in the catalogue data is listed here. The per-product, per-SKU list is `fields-to-confirm.csv`; this page is the summary.

## How to use

1. Send the manufacturer rows to the factory with the sample request. Do not publish a PDP until the construction, material, weight, sole, fit, care and origin rows are answered.
2. Send the CA rows to the chartered accountant before setting the final price ladder or running a discount.
3. Send the legal rows to the policy/label reviewer. The name-clearance row is already a Phase 1 blocker.
4. Send the 3PL rows to the reverse-logistics partner before signing the exchange promise into the checkout.

## Summary by field

| Field | Rows | Owner | Blocking | Notes |
|---|---:|---|---|---|
| `variants.foot_length_cm_status` | 330 | last | size guide | BT-FLD-SND-UK3: cm values are nominal; confirm against the last. |
| `launch_date` | 31 | founder | launch / policy | Drop 01 date is not set. |
| `care` | 30 | manufacturer | PDP / launch | Care instructions for the label and PDP. |
| `closure` | 30 | manufacturer | PDP / launch | Lace, strap or zip type and hardware. |
| `country_of_origin` | 30 | manufacturer | PDP / launch | Legal label requirement. |
| `drop_mm` | 30 | manufacturer | PDP / launch | Heel-to-toe drop; confirm the measurement method. |
| `fit_note` | 30 | manufacturer | PDP / launch | Do not publish 'true to size' or 'wide fit' until measured. |
| `fit_recommendation` | 30 | manufacturer | PDP / launch | Do not publish a fit recommendation until the last is checked. |
| `grip_claim` | 30 | manufacturer | PDP / launch | No grip claim without a test protocol and a result. |
| `heel_height_mm` | 30 | manufacturer | PDP / launch | Measured heel height. |
| `hsn` | 30 | CA | tax / pricing | Candidate headings 6401-6405; confirm material and classification. |
| `insole_material` | 30 | manufacturer | PDP / launch | Exact material and composition. |
| `last_width` | 30 | manufacturer | PDP / launch | Width and last; do not claim wide fit until measured. |
| `legal_metrology` | 30 | legal | policy / label | MRP, country of origin, manufacturer, net quantity and consumer care. |
| `lining_material` | 30 | manufacturer | PDP / launch | Exact material and composition. |
| `lug_depth_mm` | 30 | manufacturer | PDP / launch | The sample copy's 4 mm lugs are a placeholder and are not used. |
| `manufacturer` | 30 | manufacturer | PDP / launch | Legal manufacturer name and address for the label. |
| `midsole_material` | 30 | manufacturer | PDP / launch | Exact material and composition. |
| `outsole_material` | 30 | manufacturer | PDP / launch | Exact material and composition. |
| `sole_compound` | 30 | manufacturer | PDP / launch | Exact compound; no grip or durability claim without test data. |
| `test_claim` | 30 | manufacturer | PDP / launch | No test claim without a test protocol and a result. |
| `toe_shape` | 30 | manufacturer | PDP / launch | Last and toe shape; confirm before any fit copy. |
| `upper_material` | 30 | manufacturer | PDP / launch | Exact material and composition; no vegan/recycled claim without a certificate. |
| `water_resistance` | 30 | manufacturer | PDP / launch | No waterproof claim without test data. |
| `weight_g` | 30 | manufacturer | PDP / launch | The sample copy's 268 g is a placeholder and is not used. |
| `discount_flip_note` | 15 | CA | tax / pricing | A discount can flip the GST rate; confirm the treatment with the CA. |
| `exchange_limit_basis` | 1 | founder | launch / policy | Confirm whether 'twice' is per order or per customer. |
| `exchange_window` | 1 | founder | launch / policy | The 30-day window is confirmed for returns, not exchanges. |
| `fair_use_conditions` | 1 | legal | policy / label | Conditions for worn or damaged pairs need legal review. |
| `founder_story_facts` | 1 | founder | launch / policy | Founder-supplied story facts are still required before public use. |
| `gst_rule.discount_flip` | 1 | CA | tax / pricing | Confirm the GST rate when a discount moves the invoice across ₹2,500. |
| `gst_rule.headings` | 1 | CA | tax / pricing | Confirm the HSN heading for each product after materials are known. |
| `gst_rule.threshold_basis` | 1 | CA | tax / pricing | Confirm whether the ₹2,500 threshold is measured before or after tax. |
| `image_convention.credit` | 1 | photography | assets | Photographer credit is not set. |
| `image_convention.release` | 1 | legal | policy / label | Model and location releases are not recorded. |
| `name_clearance` | 1 | attorney | name clearance | Sāntvana is not cleared; no print, domain or ad spend. |
| `post_30_day_defects` | 1 | legal | policy / label | No warranty in v1; confirm the post-30-day defect route. |
| `resale_recovery` | 1 | ops | cost model | No resale recovery is assumed for returned pairs. |
| `return_shipping` | 1 | founder | launch / policy | The founder has not said who pays return shipping. |
| `reverse_logistics_per_exchange` | 1 | 3PL | cost model | ₹300 per exchange is a planning assumption; get a 3PL quote. |
| `size_curve` | 1 | founder | launch / policy | Do not set a size curve before fit-trial or pre-order data. |
| `size_system.cm_status` | 1 | last | size guide | Every cm value must be checked against the last. |
| `size_system.half_sizes` | 1 | manufacturer | PDP / launch | Half sizes are not in v1; confirm whether they are available. |
| `size_system.width` | 1 | manufacturer | PDP / launch | Do not claim wide fit until the last is measured. |
| `target_landed_cost_inr` | 1 | manufacturer | PDP / launch | All 30 target landed costs are planning assumptions; get supplier quotes. |

## What must clear before launch

- **Manufacturer:** every material, weight, lug depth, sole compound, fit statement, care instruction and country of origin. The 268 g and 4 mm lugs in the Phase 1 sample copy are placeholders and are not in this catalogue.
- **CA:** HSN classification, whether the ₹2,500 threshold is measured before or after tax, and the rate after a discount. The price ladder avoids the ambiguous zone, but discounts can enter it.
- **Legal:** legal metrology, fair-use conditions, post-30-day defect route, image releases and the name-clearance opinion.
- **3PL:** the ₹300 per-exchange reverse-logistics assumption and whether returned pairs can be resold.
- **Founder:** exchange window, whether “twice” is per order or per customer, return shipping, Drop 01 date, size curve and founder story facts.

## Full list

`fields-to-confirm.csv` has one row per product field and one row per SKU cm value, plus the catalogue, size-guide, policy, cost-model, merchandising and legal rows.
