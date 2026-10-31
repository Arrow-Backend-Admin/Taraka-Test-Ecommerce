# Merchandising plan — Sāntvana Phase 3

**Phase 3 · 31 October 2026 · concept only**
The range is a 30-product launch, not a twelve-drop calendar. Two drops a year. No product fact is confirmed; no inventory is committed.

---

## 1. Range architecture

**30 products = 5 categories × 6.** Each category has 3 good, 2 better and 1 best product. That gives 15 products at or below ₹2,500 (5% GST) and 15 above (18% GST).

| Category | Role | Good (3) | Better (2) | Best (1) |
|---|---|---|---|---|
| **Sneakers** | Traffic driver; the most legible silhouette | Meridian Low ₹2,299 · Baseline ₹2,399 · Quarter ₹2,499 | Court ₹3,499 · Drift ₹3,999 | Atlas ₹4,999 |
| **Running** | Credibility; the fit-and-climate story once evidenced | Tempo ₹2,299 · Stride ₹2,399 · Loop ₹2,499 | Relay ₹3,499 · Pace ₹3,999 | Mile ₹4,999 |
| **Everyday** | Volume; the commute, errand and weekend pair | Daily ₹2,299 · Errand ₹2,399 · Commute ₹2,499 | Market ₹3,499 · Sunday ₹3,999 | Neighbour ₹4,999 |
| **Sandals** | Summer; the highest-margin category | Step ₹2,299 · Slide ₹2,399 · Strap ₹2,499 | Shore ₹3,499 · Dust ₹3,999 | Courtyard ₹4,999 |
| **Boots** | Halo and outdoor; lower volume, higher price | Site ₹2,299 · Field ₹2,399 · Forge ₹2,499 | Ridge ₹3,499 · Quarry ₹3,999 | Halt ₹4,999 |

**Price ladder:** ₹2,299 / ₹2,399 / ₹2,499 → ₹3,499 / ₹3,999 → ₹4,999. There is no product between ₹2,500 and ₹3,499; the ladder deliberately avoids the GST dead zone at full price. See `gst-and-pricing.md` §3–§4.

---

## 2. Hero products

Five heroes, one per category. Two are good-tier volume drivers; three are best-tier halos.

| Hero | Category | Tier | Price | Planning GM | Why it is a hero | Restock |
|---|---|---|---:|---:|---|---|
| **Meridian Low** (Chalk) | Sneakers | Good | ₹2,299 | 49.76% | Entry price at the top of the 5% band; the white low-top is the most legible launch silhouette. | A |
| **Tempo** (Ink) | Running | Good | ₹2,299 | 47.48% | Lowest entry price in running; the first step into the fit system. | A |
| **Daily** (Chalk) | Everyday | Good | ₹2,299 | 54.33% | Lowest entry price in everyday; highest planning GM in the good tier. The volume driver. | A |
| **Courtyard** (Slate) | Sandals | Best | ₹4,999 | 55.15% | Best-tier sandal at ₹4,999; summer halo and planned highest AOV in the category. | B |
| **Halt** (Clay) | Boots | Best | ₹4,999 | 50.43% | Best-tier boot at ₹4,999; the outdoor-and-site halo. | B |

**Hero rule:** a hero gets the first restock, the first photography, the first size-curve review and the first PDP test. Do not spread the same attention across 30 products.

---

## 3. Margin targets

Planning gross margin before reverse logistics, payment fees, forward shipping, marketing, fulfilment and fixed costs. Costs are assumptions, not supplier quotes.

| Category | Good target | Better target | Best target | Actual planning range |
|---|---:|---:|---:|---|
| Sneakers | 48–51% | 50–53% | 52–55% | Good 49.58–49.76%; better 51.10–51.31%; best 52.79% |
| Running | 46–49% | 48–51% | 51–54% | Good 47.48%; better 49.41–49.84%; best 52.79% |
| Everyday | 52–55% | 51–54% | 54–57% | Good 53.78–54.33%; better 52.79%; best 55.15% |
| Sandals | 56–60% | 53–56% | 54–57% | Good 57.98–58.90%; better 54.26–54.47%; best 55.15% |
| Boots | 42–45% | 46–49% | 49–52% | Good 42.91–43.28%; better 47.73–48.36%; best 50.43% |

All 30 products sit inside their planning bands. The bands are not promises; a supplier quote can move a product out. Re-cut the ladder if the landed cost moves more than 10%.

**Margin floor:** after reverse logistics, the range should stay at or above **45%** gross margin. At a 30% exchange rate with two exchanges, the average is 45.26% at ₹300 per exchange; at ₹350, it is 44.22%. See `policies.md` §4.

---

## 4. 90-day launch plan

**Two drops a year.** Drop 01 is the 30-product launch. Drop 02 is at **Day 180**, not inside the first 90 days. The 90-day plan is a launch window, not a third drop.

| Window | Merchandising action | Content / ops | Gate |
|---|---|---|---|
| **Day −30 to 0** | Lock the range, hero list, size run and planning costs. Seed the database. | Manufacturer facts, CA opinion, legal metrology, 3PL rate, photography releases, size guide. | No launch until the name is cleared and the `fields-to-confirm` blockers are closed. |
| **Day 0–30** | Launch all 30. Protect hero stock. No new SKU. | Publish the fit and care pages only where evidenced. Measure exchange rate, return rate, sell-through and hero sell-through. | No discount into the GST dead zone. No performance claim without evidence. |
| **Day 31–60** | Restock A heroes. Review the size curve. No new SKU, no new colour. | Review `SIZE_SMALL`, `SIZE_LARGE` and `WIDTH` reason codes. Fix the size guide only with fit data. | If one size is more than 20% of exchanges, stop and fix the guide/last before adding stock. |
| **Day 61–90** | Margin review after reverse logistics. Decide the Drop 02 range. | Compare actual exchange rate and 3PL cost with the model. Lock Drop 02 at 12–18 SKUs if the data supports it. | If exchange rate >20% or margin after reverse logistics <45%, fix fit, size or policy before adding SKUs. |

### 90-day planning targets

These are targets, not forecasts.

| Metric | Target | Why |
|---|---:|---|
| Sell-through by Day 90 | 55–65% | Proves the range before Drop 02. |
| Size exchange rate | ≤20% | Keeps the promise near the cost-model base case. |
| Return rate | ≤8% | Protects margin and stock. |
| Gross margin after reverse logistics | ≥45% | The planning floor. |
| Hero stock cover | 45 days | Prevents a hero stock-out in the first quarter. |
| Size-guide accuracy | <5% of orders exchange for size | The fit promise has to show up in the data. |

---

## 5. Discount rule

The full-price ladder avoids the ₹2,501–₹2,809.52 dead zone. A discount can still land in it. The simple rule:

> **Do not discount a product into ₹2,501–₹2,809.52.** Either stay at or above ₹2,809.52, or go to ₹2,500 or below with the CA’s written treatment.

Discount bands are in `gst-and-pricing.md` §7. A 20% discount on Court (₹3,499) lands at ₹2,799.20 — inside the dead zone. The customer pays less, the brand nets less, and the GST rate is 18%. Do not run it.

---

## 6. Assortment and buy notes

- **Colour core:** chalk, ink and clay. **Accents:** bone, moss, slate, sand and ground. No pastels, no gradients, no seasonal colour drop in the first 90 days.
- **Size curve:** **[TO CONFIRM: founder]**. Do not set a buy curve before the fit trial or pre-order data. The size run is UK 3-13, whole sizes only.
- **Buy depth:** A heroes first, B better/best second, C good third. The first buy should be shallow enough to learn from exchanges; the cost model assumes a 10–30% exchange rate.
- **No new categories in v1.** No collaborations, no celebrity, no “limited drop” language. Two drops a year is the model.
- **No inventory commitment** until the manufacturer facts, CA opinion, 3PL rate and name clearance are in.

---

## 7. Drop 02 (Day 180)

- **Size:** 12–18 SKUs, planning range. Not a commitment.
- **What changes:** use the first 90 days of exchange reasons, return reasons and hero sell-through. Add a colour or a construction upgrade only if the data supports it.
- **What does not change:** five categories, the good/better/best ladder, the ₹2,500 line discipline, the two-drop cadence.
- **What must be true:** name cleared, product facts confirmed, 3PL rate written, margin after reverse logistics ≥45%, and the size guide validated against the last.

---

## 8. Open items

| Item | Owner | Status |
|---|---|---|
| Launch date | Founder | **[TO CONFIRM: founder]** |
| Size curve and first buy depth | Founder / ops | **[TO CONFIRM: founder]** |
| Manufacturer facts and landed cost | Manufacturer | **[TO CONFIRM: manufacturer]** |
| CA opinion on the GST threshold and discounts | CA | **[TO CONFIRM: CA]** |
| 3PL reverse-logistics rate | 3PL | **[TO CONFIRM: 3PL]** |
| Photography and releases | Photography / legal | **[TO CONFIRM: photography]** |
| Name clearance | Attorney | **[TO CONFIRM: attorney]** |
| Founder story facts | Founder | **[TO CONFIRM: founder]** Still required before public use |

---

## Guardrails

- No product fact is confirmed by a price, a margin or a hero badge.
- No performance, material or fit claim without the evidence in `../strategy.md` §7.
- No discount into the GST dead zone.
- No new drop inside the first 90 days. Two drops a year.
- No inventory buy before the fit trial, supplier quote and name clearance.
