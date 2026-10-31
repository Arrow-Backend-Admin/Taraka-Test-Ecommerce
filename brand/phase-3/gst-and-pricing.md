# GST and pricing — Sāntvana Phase 3

**Phase 3 · 31 October 2026 · concept only**
No tax opinion is given here. A chartered accountant must confirm the treatment before the prices go live. The name is not cleared; no print, domain or ad spend.

---

## 1. The rule as supplied

The founder supplied this rule on 31 October 2026:

> Footwear is **5% GST up to ₹2,500 per pair** and **18% above ₹2,500**, on **invoice sale value**, for the **whole pair**. It applies to headings **6401–6405** under **Notification 9/2025-Central Tax (Rate), effective 22 September 2025**.

**CA confirmation required:** a chartered accountant must confirm whether the ₹2,500 threshold is measured **before or after tax**, and how a discount that moves a pair across the line is treated. This document models the threshold as the GST-inclusive invoice value because the storefront shows GST-inclusive MRP. That is a working assumption, not a legal conclusion.

---

## 2. Model assumptions

| Item | Assumption |
|---|---|
| Listed price | GST-inclusive MRP. This matches the Phase 1 sample copy: “Inclusive of all taxes.” |
| Net revenue | `price ÷ (1 + GST rate)` |
| GST amount | `price − net revenue` |
| Gross margin | `net revenue − target landed cost` |
| Target landed cost | **Planning assumption, not a supplier quote.** Replace with the factory FOB plus freight, duty, packaging and landed cost. |
| Margin shown | Product gross margin only. It excludes reverse logistics, payment gateway fees, forward shipping, packaging, marketing, marketplace fees and fixed costs. |
| Rounding | Two decimal places, normal commercial rounding. |
| Price ladder | ₹2,299 / ₹2,399 / ₹2,499 (good) · ₹3,499 / ₹3,999 (better) · ₹4,999 (best). |

The price ladder deliberately leaves **no product between ₹2,500 and ₹3,499**. That keeps every full-price product on the same side of the line under either threshold interpretation. Discounts can still enter the ambiguous zone; see §7.

---

## 3. The ₹2,500 cliff

The rate change is not a gentle slope. At ₹2,501, net revenue falls by ₹261.46 compared with ₹2,500.

| Invoice price | GST rate | GST amount | Net revenue | Note |
|---:|---:|---:|---:|---|
| ₹2,499 | 5% | ₹119.00 | ₹2,380.00 | Good tier. |
| ₹2,500 | 5% | ₹119.05 | ₹2,380.95 | Top of the 5% band. |
| ₹2,501 | 18% | ₹381.51 | ₹2,119.49 | **₹261.46 less net revenue than ₹2,500.** |
| ₹2,809.52 | 18% | ₹428.57 | ₹2,380.95 | Break-even with ₹2,500 at 5%. |
| ₹3,499 | 18% | ₹533.75 | ₹2,965.25 | First better-tier price. |
| ₹4,999 | 18% | ₹762.56 | ₹4,236.44 | Top of the range. |

**Dead zone: ₹2,501–₹2,809.52.** A full-price product should not sit here. It pays 18% but nets less than a ₹2,500 pair at 5%.

---

## 4. Two interpretations of the threshold

The CA must decide which line applies. The full-price ladder is designed so the answer does not change any product’s rate.

| Interpretation | Top of 5% band (GST-inclusive price) | 18% break-even to match ₹2,500 at 5% | Products in the divergence zone? |
|---|---:|---:|---|
| Threshold on GST-inclusive invoice value | ₹2,500.00 | ₹2,809.52 | None. Good ends at ₹2,499; better starts at ₹3,499. |
| Threshold on taxable value | ₹2,625.00 | ₹2,950.00 | None. Good ends at ₹2,499; better starts at ₹3,499. |

If the CA says the threshold is on taxable value, the 5% band extends to a ₹2,625 GST-inclusive price. The ladder still has no product in that zone at full price. Discounts between ₹2,500 and ₹2,625 are the only place where the two interpretations diverge.

---

## 5. Price ladder and GST buckets

### At or below ₹2,500 — 5% GST (15 products)

| Category | Good products | Price |
|---|---|---:|
| Sneakers | Meridian Low, Baseline, Quarter | ₹2,299 / ₹2,399 / ₹2,499 |
| Running | Tempo, Stride, Loop | ₹2,299 / ₹2,399 / ₹2,499 |
| Everyday | Daily, Errand, Commute | ₹2,299 / ₹2,399 / ₹2,499 |
| Sandals | Step, Slide, Strap | ₹2,299 / ₹2,399 / ₹2,499 |
| Boots | Site, Field, Forge | ₹2,299 / ₹2,399 / ₹2,499 |

### Above ₹2,500 — 18% GST (15 products)

| Category | Better products | Best product |
|---|---|---|
| Sneakers | Court ₹3,499; Drift ₹3,999 | Atlas ₹4,999 |
| Running | Relay ₹3,499; Pace ₹3,999 | Mile ₹4,999 |
| Everyday | Market ₹3,499; Sunday ₹3,999 | Neighbour ₹4,999 |
| Sandals | Shore ₹3,499; Dust ₹3,999 | Courtyard ₹4,999 |
| Boots | Ridge ₹3,499; Quarry ₹3,999 | Halt ₹4,999 |

### Tier summary

| Tier | Price points | Products | GST bucket | Role |
|---|---|---:|---|---|
| Good | ₹2,299 / ₹2,399 / ₹2,499 | 15 | 5% | Entry, volume, fit trial. |
| Better | ₹3,499 / ₹3,999 | 10 | 18% | Higher-price tier; material and construction claims unconfirmed. |
| Best | ₹4,999 | 5 | 18% | Halo, one per category. |

---

## 6. Net revenue and margin for each product

Prices are GST-inclusive. Costs are planning assumptions. The full generated table is also in `pricing-table.md`.

| # | Product | Category | Tier | Price ₹ | GST | GST ₹ | Net ₹ | Landed cost ₹ | GM ₹ | GM % | Target |
|---:|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Meridian Low (Chalk) | Sneakers | Good | 2,299 | 5% | 109.48 | 2,189.52 | 1,100 | 1,089.52 | 49.76% | 48–51% |
| 2 | Baseline (Ink) | Sneakers | Good | 2,399 | 5% | 114.24 | 2,284.76 | 1,150 | 1,134.76 | 49.67% | 48–51% |
| 3 | Quarter (Clay) | Sneakers | Good | 2,499 | 5% | 119.00 | 2,380.00 | 1,200 | 1,180.00 | 49.58% | 48–51% |
| 4 | Court (Bone) | Sneakers | Better | 3,499 | 18% | 533.75 | 2,965.25 | 1,450 | 1,515.25 | 51.10% | 50–53% |
| 5 | Drift (Moss) | Sneakers | Better | 3,999 | 18% | 610.02 | 3,388.98 | 1,650 | 1,738.98 | 51.31% | 50–53% |
| 6 | Atlas (Slate) | Sneakers | Best | 4,999 | 18% | 762.56 | 4,236.44 | 2,000 | 2,236.44 | 52.79% | 52–55% |
| 7 | Tempo (Ink) | Running | Good | 2,299 | 5% | 109.48 | 2,189.52 | 1,150 | 1,039.52 | 47.48% | 46–49% |
| 8 | Stride (Chalk) | Running | Good | 2,399 | 5% | 114.24 | 2,284.76 | 1,200 | 1,084.76 | 47.48% | 46–49% |
| 9 | Loop (Clay) | Running | Good | 2,499 | 5% | 119.00 | 2,380.00 | 1,250 | 1,130.00 | 47.48% | 46–49% |
| 10 | Relay (Moss) | Running | Better | 3,499 | 18% | 533.75 | 2,965.25 | 1,500 | 1,465.25 | 49.41% | 48–51% |
| 11 | Pace (Slate) | Running | Better | 3,999 | 18% | 610.02 | 3,388.98 | 1,700 | 1,688.98 | 49.84% | 48–51% |
| 12 | Mile (Ground) | Running | Best | 4,999 | 18% | 762.56 | 4,236.44 | 2,000 | 2,236.44 | 52.79% | 51–54% |
| 13 | Daily (Chalk) | Everyday | Good | 2,299 | 5% | 109.48 | 2,189.52 | 1,000 | 1,189.52 | 54.33% | 52–55% |
| 14 | Errand (Sand) | Everyday | Good | 2,399 | 5% | 114.24 | 2,284.76 | 1,050 | 1,234.76 | 54.04% | 52–55% |
| 15 | Commute (Ink) | Everyday | Good | 2,499 | 5% | 119.00 | 2,380.00 | 1,100 | 1,280.00 | 53.78% | 52–55% |
| 16 | Market (Bone) | Everyday | Better | 3,499 | 18% | 533.75 | 2,965.25 | 1,400 | 1,565.25 | 52.79% | 51–54% |
| 17 | Sunday (Clay) | Everyday | Better | 3,999 | 18% | 610.02 | 3,388.98 | 1,600 | 1,788.98 | 52.79% | 51–54% |
| 18 | Neighbour (Moss) | Everyday | Best | 4,999 | 18% | 762.56 | 4,236.44 | 1,900 | 2,336.44 | 55.15% | 54–57% |
| 19 | Step (Sand) | Sandals | Good | 2,299 | 5% | 109.48 | 2,189.52 | 900 | 1,289.52 | 58.90% | 56–60% |
| 20 | Slide (Ink) | Sandals | Good | 2,399 | 5% | 114.24 | 2,284.76 | 950 | 1,334.76 | 58.42% | 56–60% |
| 21 | Strap (Clay) | Sandals | Good | 2,499 | 5% | 119.00 | 2,380.00 | 1,000 | 1,380.00 | 57.98% | 56–60% |
| 22 | Shore (Bone) | Sandals | Better | 3,499 | 18% | 533.75 | 2,965.25 | 1,350 | 1,615.25 | 54.47% | 53–56% |
| 23 | Dust (Moss) | Sandals | Better | 3,999 | 18% | 610.02 | 3,388.98 | 1,550 | 1,838.98 | 54.26% | 53–56% |
| 24 | Courtyard (Slate) | Sandals | Best | 4,999 | 18% | 762.56 | 4,236.44 | 1,900 | 2,336.44 | 55.15% | 54–57% |
| 25 | Site (Ground) | Boots | Good | 2,299 | 5% | 109.48 | 2,189.52 | 1,250 | 939.52 | 42.91% | 42–45% |
| 26 | Field (Sand) | Boots | Good | 2,399 | 5% | 114.24 | 2,284.76 | 1,300 | 984.76 | 43.10% | 42–45% |
| 27 | Forge (Ink) | Boots | Good | 2,499 | 5% | 119.00 | 2,380.00 | 1,350 | 1,030.00 | 43.28% | 42–45% |
| 28 | Ridge (Moss) | Boots | Better | 3,499 | 18% | 533.75 | 2,965.25 | 1,550 | 1,415.25 | 47.73% | 46–49% |
| 29 | Quarry (Slate) | Boots | Better | 3,999 | 18% | 610.02 | 3,388.98 | 1,750 | 1,638.98 | 48.36% | 46–49% |
| 30 | Halt (Clay) | Boots | Best | 4,999 | 18% | 762.56 | 4,236.44 | 2,100 | 2,136.44 | 50.43% | 49–52% |

**Summary:** 15 products at or below ₹2,500 (5%), 15 above (18%). Average net revenue ₹2,907.49; average gross margin ₹1,495.83, or 51.45% (simple average, not sales-weighted).

---

## 7. Discounts: two cliffs

A discount can do two things:

1. **Flip the rate.** If it takes the invoice to ₹2,500 or below, the 5% rate may apply.
2. **Land in the dead zone.** If it leaves the invoice between ₹2,501 and ₹2,809.52, the pair pays 18% but nets less than a ₹2,500 pair at 5%.

| Full price | 18% band with net ≥ ₹2,380.95 | Avoid: 18% dead zone | 5% rate band (price ≤ ₹2,500) |
|---:|---:|---:|---:|
| ₹3,499 | 0–19.70% | 19.71–28.55% | 28.56%+ |
| ₹3,999 | 0–29.74% | 29.75–37.48% | 37.49%+ |
| ₹4,999 | 0–43.80% | 43.81–49.98% | 49.99%+ |

A product at ₹2,499 stays in the 5% band under discount. A price increase above ₹2,500 flips it to 18%.

**Do not run a discount that lands in the dead zone.** The customer pays less, the brand nets less, and the GST rate is higher. The exact treatment of a discount that crosses the line is **[TO CONFIRM: CA]**.

---

## 8. Decisions needed

1. **CA opinion:** is the ₹2,500 threshold measured on GST-inclusive invoice value or taxable value? The full-price ladder avoids the difference; discounts do not.
2. **CA opinion:** when a discount takes the invoice below ₹2,500, does the 5% rate apply to the whole pair, and from what date?
3. **Founder:** approve the ₹2,299 / ₹2,399 / ₹2,499 / ₹3,499 / ₹3,999 / ₹4,999 ladder.
4. **Founder:** approve the discount rule. The simplest rule is “no discount into ₹2,501–₹2,809.52.” A deeper discount to ₹2,500 or below is allowed only with the CA’s written treatment.
5. **Manufacturer:** confirm the HSN heading for each product after the materials are known. Candidate headings are 6401–6405.

---

## 9. Open items

| Item | Owner | Status |
|---|---|---|
| Whether the threshold is before or after tax | CA | **[TO CONFIRM: CA]** |
| GST treatment when a discount crosses ₹2,500 | CA | **[TO CONFIRM: CA]** |
| HSN heading per product | Manufacturer + CA | **[TO CONFIRM: CA]** |
| Supplier landed cost | Manufacturer / founder | **[TO CONFIRM: manufacturer]** |
| Payment gateway and forward-shipping costs | Founder / ops | Not in this model |
| Reverse-logistics impact | 3PL / ops | See `policies.md` |

---

## Guardrails

- No tax opinion is given here. The CA’s written advice replaces this model.
- No product fact is confirmed by a price or a margin.
- No discount into the dead zone without the CA’s treatment.
- No “GST included” claim until the price display, invoice and CA advice agree.
