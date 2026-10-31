# Policies and reverse-logistics cost model — Sāntvana Phase 3

**Phase 3 · 31 October 2026 · concept only**
Policy copy is a draft for founder and legal review. The name is not cleared; no print, domain or ad spend. Hindi copy is not included because it needs native-speaker and legal review.

---

## 1. Confirmed terms

| Term | Status | Note |
|---|---|---|
| Free size exchange **twice** | Confirmed by founder, 30 October 2026 | Applies to size, not a change of mind on style. |
| **30-day returns** | Confirmed by founder, 30 October 2026 | The clock starts at **delivery**, not dispatch. |
| **No warranty in v1** | Confirmed by founder, 30 October 2026 | Publish confirmed sole and outsole specifications instead. |
| Two drops a year | Confirmed by founder, 30 October 2026 | Not a policy term; it constrains the merchandising plan. |

**Not confirmed:** the exchange window, who pays return shipping, the fair-use conditions, the post-30-day defect route, and whether a second exchange can be refused. These are flagged in `fields-to-confirm.csv`.

---

## 2. Customer-facing copy

### 2.1 Size exchange

**Short version**

> Wrong size? We will exchange it free, twice.

**Full version**

> If the fit is wrong, we will exchange the size free, twice. Start the exchange from your order page and we will arrange the pickup. We will send the replacement once the returned pair is checked. If your size is out of stock, we will offer a refund or another colour instead of a third exchange.

**Do not say**

- “30-day exchange” until the founder confirms the exchange window. The 30-day window is confirmed for returns, not exchanges.
- “No questions asked” unless the founder accepts the fair-use conditions.
- “Free returns” — return shipping is **[TO CONFIRM: founder]**.

### 2.2 Returns

**Short version**

> 30-day returns from delivery.

**Full version**

> You have 30 days from delivery to return your pair. Start the return from your order page. We will arrange the pickup and refund to the original payment method after the pair is checked. Return shipping is **[TO CONFIRM: founder]**.

### 2.3 Warranty

**Short version**

> No warranty in v1.

**Full version**

> There is no warranty in v1. We publish confirmed sole and outsole specifications instead. If the pair is faulty on arrival, use the 30-day return policy. After 30 days, the defect route is **[TO CONFIRM: legal]**.

### 2.4 Footer line

> Free size exchange twice · 30-day returns from delivery · No durability warranty in v1.

---

## 3. Internal operating rules

1. **Return clock.** Start at the delivery scan, not dispatch. Store the delivery timestamp and show the last eligible date in the account.
2. **Exchange limit.** Track two exchanges against the order. If the second replacement still does not fit, offer a refund or another style; do not offer a third exchange. This is the working interpretation of “twice”; the founder should confirm it.
3. **Exchange window.** **[TO CONFIRM: founder]** Do not publish 30 days for exchanges until confirmed.
4. **Condition.** The pair must be in a resalable condition, unworn beyond trying on, with the box and tags. Fair-use conditions are **[TO CONFIRM: legal]**.
5. **Inspection.** Inspect at the warehouse. Resell only if resalable. The cost model assumes **no resale recovery** for returned pairs; that is conservative.
6. **No warranty.** Do not promise repair, resole or a durability guarantee in v1. The Phase 1 repair-and-resole idea is not a v1 policy.
7. **Reason codes.** Use `SIZE_SMALL`, `SIZE_LARGE`, `WIDTH`, `STYLE`, `DAMAGED`, `OTHER`. Report the first three separately; they drive size-guide and last changes.
8. **Hindi copy.** Not included. Native-speaker and legal review required before publishing.

---

## 4. Reverse-logistics cost model

### 4.1 Assumptions

| Item | Value | Status |
|---|---:|---|
| Reverse-logistics cost per exchange | **₹300** | **[TO CONFIRM: 3PL]** |
| Pickup leg | ₹120 | Planning assumption |
| Return leg | ₹80 | Planning assumption |
| QC and repack | ₹50 | Planning assumption |
| Outbound replacement | ₹50 | Planning assumption |
| Exchange rate | % of orders with at least one exchange | Planning definition |
| Second exchange | Doubles the reverse-logistics cost for that order | Policy allows it |
| Resale recovery | ₹0 | **[TO CONFIRM: ops]** |
| Average net revenue | ₹2,907.49 | Simple average across 30 products |
| Average gross margin | ₹1,495.83 | 51.45% before reverse logistics |
| Costs excluded | Payment gateway, forward shipping, packaging, marketing, fixed costs | Not in this model |

The ₹300 is a planning assumption, not a quote. Get a written 3PL rate before the promise goes live. A ₹50 increase per exchange is enough to push the 30% two-exchange case below the 45% margin floor.

### 4.2 Base case: one exchange per exchanging order

| Exchange rate | Cost per order | Gross margin after | Margin % | Impact |
|---:|---:|---:|---:|---:|
| 10% | ₹30.00 | ₹1,465.83 | 50.42% | −1.03 pp |
| 20% | ₹60.00 | ₹1,435.83 | 49.38% | −2.06 pp |
| 30% | ₹90.00 | ₹1,405.83 | 48.35% | −3.10 pp |

### 4.3 Stress case: two exchanges per exchanging order

The policy allows two exchanges. If every exchanging customer uses both, the cost doubles.

| Exchange rate | Cost per order | Gross margin after | Margin % | Impact |
|---:|---:|---:|---:|---:|
| 10% | ₹60.00 | ₹1,435.83 | 49.38% | −2.06 pp |
| 20% | ₹120.00 | ₹1,375.83 | 47.32% | −4.13 pp |
| 30% | ₹180.00 | ₹1,315.83 | 45.26% | −6.19 pp |

**Planning ceiling:** 30% exchange rate with two exchanges leaves 45.26%, only 0.26 pp above a 45% gross-margin floor. At ₹350 per exchange, the same case falls to 44.22%. If the actual rate is above 30% or the 3PL cost is above ₹300, the promise needs a price change, a fit fix, or a policy change.

### 4.4 Two product examples

**Meridian Low — ₹2,299, 5% GST, net ₹2,189.52, gross margin ₹1,089.52 (49.76%)**

| Exchange rate | Cost per order | Gross margin after | Margin % | Impact |
|---:|---:|---:|---:|---:|
| 10% | ₹30.00 | ₹1,059.52 | 48.39% | −1.37 pp |
| 20% | ₹60.00 | ₹1,029.52 | 47.02% | −2.74 pp |
| 30% | ₹90.00 | ₹999.52 | 45.65% | −4.11 pp |

**Halt — ₹4,999, 18% GST, net ₹4,236.44, gross margin ₹2,136.44 (50.43%)**

| Exchange rate | Cost per order | Gross margin after | Margin % | Impact |
|---:|---:|---:|---:|---:|
| 10% | ₹30.00 | ₹2,106.44 | 49.72% | −0.71 pp |
| 20% | ₹60.00 | ₹2,076.44 | 49.01% | −1.42 pp |
| 30% | ₹90.00 | ₹2,046.44 | 48.31% | −2.12 pp |

The lower-priced pair carries a larger percentage-point impact. That is why the good tier needs a fit-first PDP, a correct size guide and a real exchange process, not just a promise.

---

## 5. What the policy costs, in plain terms

- At a 10% exchange rate, one free exchange costs about **1% of net revenue** across the catalogue.
- At 20%, it costs about **2%**.
- At 30%, it costs about **3%**.
- If every exchanging customer uses both exchanges, double those figures: **2%, 4.1% and 6.2%**.
- The promise is affordable only if the exchange rate stays near or below 20% and the 3PL cost stays near ₹300. Both are unconfirmed.

---

## 6. Open items

| Item | Owner | Status |
|---|---|---|
| Exchange window | Founder | **[TO CONFIRM: founder]** |
| Who pays return shipping | Founder | **[TO CONFIRM: founder]** |
| Fair-use conditions | Legal | **[TO CONFIRM: legal]** |
| Post-30-day defect route | Legal | **[TO CONFIRM: legal]** |
| 3PL cost per exchange | 3PL | **[TO CONFIRM: 3PL]** |
| Resale recovery | Ops | **[TO CONFIRM: ops]** |
| Hindi policy copy | Native speaker + legal | Not started |
| Whether “twice” is per order or per customer | Founder | **[TO CONFIRM: founder]** Working assumption: per order |

---

## Guardrails

- No “free returns” claim. Only the size exchange is confirmed free.
- No “30-day exchange” claim until the founder confirms the exchange window.
- No warranty, repair or durability promise in v1.
- No policy copy goes live without legal review and a written 3PL rate.
