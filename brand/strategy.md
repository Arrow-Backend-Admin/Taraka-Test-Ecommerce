# Sāntvana — Brand Strategy

**Phase 1 deliverable · v1.1 · 30 October 2026**
Owner: brand strategy · Status: Phase 2 approved as a concept; Phase 3 awaiting approval; no print, domain or ad spend until the attorney opinion

**v1.1 changes:** The previous name is dropped. Sāntvana (सांत्वना; also spelled सान्त्वना) replaces it throughout. Name-dependent wordplay is removed, the origin story is rebuilt around founder-supplied facts rather than an invented anecdote, and Phase 2 now carries a bilingual Devanagari requirement.

---

## 0. Assumptions

Your Inputs section was blank except for the brand name. These are the defaults I have used. Correct any of them and I will re-cut this document — every downstream phase depends on them.

| Input | Value used | Why |
|---|---|---|
| Brand name | **Sāntvana** (सांत्वना; also सान्त्वना), supplied by you | See `naming.md` — a risk memo, not a clearance opinion; print, domain and ad spend are blocked until an attorney opinion |
| Market | India only at launch | Matches INR pricing, GST/HSN, Razorpay, ap-south-1 |
| Currency | INR | — |
| Price tier | Mid-range, ₹2,299–₹4,999 core | Highest-volume D2C band in Indian footwear; leaves room for a good/better/best ladder |
| Hero categories | Sneakers, running, everyday, sandals, boots | 5 categories × 6 products = the 30-product launch catalogue |
| Target customer | Urban, 22–34, style-conscious, value-driven, tier-1 and tier-2 metros | Derived from the price tier and categories |
| Personality | Calm · grounded · quietly bold · dependable | Re-derived from the name's meaning (solace, comfort); three of the four v1.0 words kept — see §1.9 |
| Shipping | India only (all serviceable pincodes) | International is Tier 2 |
| References | Admire: On (engineering clarity), Veja (material honesty), Clarks (comfort heritage). Avoid resembling: Nike, Adidas, Puma (visual and verbal similarity risk) | Empty in your inputs; stated so you can veto |
| Cloud | AWS `ap-south-1`, Cloudflare R2 for images, ~USD 150/month MVP budget | — |
| Payments | Razorpay, test mode first | — |
| Domain | Not owned | Ideas in `naming.md` |
| Tech overrides | None | Stack frozen as specified |

---

## 1. Strategy

### 1.1 Mission

Make footwear that fits Indian feet and Indian days — the commute, the monsoon, and the ten thousand steps nobody planned for.

### 1.2 Vision

To be the pair urban India reaches for without thinking about it: the default everyday shoe by 2032, bought on fit and durability rather than on logo.

### 1.3 Values

Three values, each with the behaviour that proves it. A value that cannot be observed in a decision is a poster, not a value.

**1. Fit before flash.**
Every style starts with the last, not the trend board.
*Proof:* every product page publishes a fit note ("runs narrow / true to size / wide-friendly") and a half-size recommendation. If we cannot say how it fits, we do not ship it.

**2. Say what it is.**
Materials, weights and care instructions on the page, in plain words. No claim we cannot evidence.
*Proof:* a materials table on every PDP and a public claims register (see §7). "Vegan", "recycled" and "sustainable" stay off the site until a supplier certificate exists.

**3. Built to be worn out.**
We design for kilometres, not seasons. Fewer styles, kept longer.
*Proof:* two drops a year instead of twelve; sole and outsole specs published; a repair-and-resole path before a replacement path.

### 1.4 Positioning statement

> For urban Indians aged 22–34 who spend more of the day on their feet than they intended, **Sāntvana** is the everyday footwear brand that fits Indian feet and Indian weather at a mid-market price, **because** every style is built on lasts shaped for Indian foot widths and tested on wet, uneven city surfaces before it ships.

Two clauses in that statement are currently **claims, not facts** — the lasts and the testing. They are commitments the product team must make true before launch. See §7.

### 1.5 Brand promise

**The Sāntvana promise: right fit, first pair — or we exchange it free, twice.**

Short enough to print on a box. Backed by a policy that costs real money, which is what makes it a promise rather than a slogan. The exchange policy itself is written in Phase 3; the "twice" is confirmed (§6).

### 1.6 Customer personas

Three personas, each tied to a category cluster so the catalogue in Phase 3 has someone to sell to.

---

**Persona 1 — Karthik, the commuter**
*27 · Bengaluru (Indiranagar) · product analyst · household income ₹12–18L · buys 2–3 pairs a year at ₹2,500–₹4,000*

- **Day:** 45 minutes on the Purple Line, then 1.2 km of walking, then eight hours at a desk, then back. Weekends are cafés and a 5 km walk.
- **What he buys:** one clean white sneaker he can wear to work, one darker everyday pair for the monsoon.
- **Trigger:** his current white pair has gone grey at the toe and the sole has flattened.
- **Objection:** "Will it look cheap in person?" He has been burned by ₹1,800 shoes that photographed well.
- **What wins him:** real photography at 45°, a materials list, and a return policy he believes.
- **Where he shops:** phone, 10pm, Instagram ad → site → UPI.

> "I don't need a shoe that says something. I need one that survives the walk from Indiranagar metro."

---

**Persona 2 — Nisha, the reluctant runner**
*31 · Pune (Kothrud) · school teacher · household income ₹8–14L · buys 2 pairs a year at ₹2,000–₹4,500*

- **Day:** on her feet in a classroom, then a 5K three mornings a week. Runs because it is cheap and it is hers.
- **What she buys:** one running pair, one sandal for the summer.
- **Trigger:** a half-marathon entry, or a heel blister that will not heal.
- **Objection:** "It'll rub at the heel by week two." She has returned three pairs this year.
- **What wins her:** a fit note that admits when a shoe runs narrow, reviews that mention blisters, and an exchange that does not require an argument.
- **Where she shops:** site on laptop, reads every review, pays by card.

> "I've returned three pairs this year because of the heel. I just want to know before I buy."

---

**Persona 3 — Imran, the nine-hour day**
*34 · Surat · site supervisor · household income ₹6–10L · buys 2 pairs a year at ₹2,500–₹3,500*

- **Day:** nine hours on concrete and gravel, some of it wet. Replaces his work pair every nine months whether or not it has failed.
- **What he buys:** a boot for site, an everyday pair for evenings and family occasions.
- **Trigger:** the sole goes slick, or the toe cap splits.
- **Objection:** "Sole wears out in one season." He judges a shoe entirely by how long the bottom lasts.
- **What wins him:** a published outsole spec, a grip claim with evidence behind it, UPI and COD, and a link he can forward on WhatsApp to his wife.
- **Where he shops:** mostly phone, often someone else's phone.

> "Tell me how long the sole lasts. That's the only number I care about."

---

### 1.7 Competitive map

Positions are qualitative judgements for strategy, not measured data. Price bands are approximate and should be re-checked at build time.

| Brand | Price band (INR) | Where it wins | Where it is exposed | How Sāntvana differs |
|---|---|---|---|---|
| **Nike India** | 4,000–15,000 | Performance credibility, status, retail theatre | Price for everyday use; narrow lasts; little fit guidance | Same engineering language, roughly half the price, published fit notes |
| **Bata** | 800–3,500 | Distribution, family trust, price | Design credibility, digital experience | Design-led and online-first, without abandoning price honesty |
| **Campus** | 1,200–2,500 | Price, youth sneaker volume | Durability perception, fit range, sole life | ~₹1,000 more for a materially better sole and a real fit system |
| **Neemans** | 2,500–4,500 | Comfort story, D2C execution, eco positioning | Narrow silhouette range, little beyond sneakers | Full range: sneakers, running, everyday, sandals, boots |
| **Comet** | 3,500–6,000 | Design credibility, drop model, cultural relevance | Climate and fit engineering; price | Engineering-first, not drop-first; two drops a year |

**Map — price against fit-and-climate engineering for India**

```
                    HIGH fit & climate engineering
                              │
                              │            ● Sāntvana (target position)
                              │
              Neemans ●       │
                              │        ● Comet
                              │
  ────────────────────────────┼────────────────────────────  PRICE →
   LOW                        │                         HIGH
                     ● Bata   │      ● Campus
                              │
                     ● Nike India
                              │
                    LOW fit & climate engineering
```

**The gap Sāntvana is claiming:** nobody in this set leads with *fit and climate engineering at a mid-market price*. Nike owns performance status, Comet owns design, Neemans owns comfort language, Bata owns reach, Campus owns price. Fit-for-India is the one defensible position that is also cheap to prove — it lives in the last, the sole compound and the product page, not in media spend.

### 1.8 What we are deliberately not

Stated so the next seven phases do not drift:

- **Not a performance brand.** No carbon plates, no marathon records, no elite athlete endorsements.
- **Not a drop brand.** Two drops a year. Scarcity is not the business model.
- **Not a marketplace brand in v1.** Own site only; marketplaces are Tier 2.
- **Not a sustainability brand yet.** We will not use "eco", "vegan" or "recycled" until a supplier certificate exists for that specific material.

### 1.9 Personality

Four words, re-derived from the name. Sāntvana means solace — not softness, not spa. Each word has to be visible in a decision, a page or a product, or it is decoration.

| Word | What it means here | Evidence it has to show up in |
|---|---|---|
| **Calm** | The name's first meaning: relief, not excitement. | Restrained palette, one idea per screen, no exclamation marks, error copy that lowers the temperature. |
| **Grounded** | Comfort for real Indian ground, not a concept. | Fit notes, real photography, material and weight specs, wet-surface testing. |
| **Quietly bold** | Confidence without volume. | A distinctive sole tread, strong silhouettes, no oversized logo. |
| **Dependable** | Comfort that survives the second monsoon. | Published outsole specs, 30-day returns, the exchange promise, stock accuracy. |

**Kept from v1.0:** grounded, quietly bold, dependable. **Retired:** precise. Precision is still a value behaviour — it lives in "Fit before flash" and in the copy discipline — but it described the method, not the character. **Added:** calm, which is the one word the name actually gives us.

---

## 2. Taglines

Eight options. The primary carries the brand; the two secondaries do specific jobs. No name-dependent wordplay survives from v1.0.

| # | Tagline | Job |
|---|---|---|
| **1** | **Made for the long way home.** | **Primary.** Emotional, category-agnostic, owns the commute rather than the gym |
| **2** | **Fit first.** | **Secondary.** Functional proof line for PDPs, packaging and ads |
| **3** | **Comfort, earned.** | **Secondary.** Ties to the name's meaning without claiming a softness we cannot evidence |
| 4 | Made to be forgotten. | The best compliment for an everyday shoe; launch campaign, not the masthead |
| 5 | Built for the 10,000. | Step-count framing; strong for running, weak for sandals |
| 6 | Right fit, first pair. | Restates the promise; use on the returns/exchange page |
| 7 | Your day, on foot. | Calm, broad, low-risk; a safe alternative primary |
| 8 | Fewer shoes. Better ones. | Anti-fast-fashion stance; use in the About page and press kit |

**Hindi adaptation of the primary:** *लंबे रास्ते के लिए बने।* ("Made for the long road.") An alternative that leans into the name's meaning is *घर लौटने तक साथ।* ("With you until you get home.") Both are flagged for review by a native Hindi copywriter before use — "long way home" does not translate literally without sounding odd.

---

## 3. Brand story

Sāntvana began with a problem that would not go away: [FOUNDER'S REAL STORY — the moment, person or pair of shoes that started this].

What stayed with us was simpler than a business plan. Much of the footwear sold in India is designed on lasts shaped somewhere else, then sold to feet that live here — feet that walk to a station, stand through a shift, and come home on wet, uneven ground.

So we start with the last. [FOUNDER'S REAL STORY — the first sample, fit trial or customer who told you it finally fit.] That became the method: wider toe boxes where they are needed, heel counters that do not rub, soles built for wet tile, and materials published in plain words.

Sāntvana means solace — the quiet comfort of being looked after. We are not claiming to have invented comfort. We are trying to earn it, one pair at a time, for the long way home.

**About us (50 words)**

Sāntvana makes everyday footwear for urban India — sneakers, runners, sandals and boots built on lasts shaped for Indian feet. Mid-market prices, honest materials, fewer styles kept for longer. Free size exchanges twice, 30-day returns, and a size guide that tells you the truth. Designed in Bengaluru, shipped from Bhiwandi.

> **Two placeholders, deliberately.** The founding anecdote is the one asset I cannot invent for you. Replace both bracketed passages with the real account, or cut them and let the problem statement carry the story. The About paragraph keeps the v1.0 location line; confirm Bengaluru and Bhiwandi in the claims register before publishing.

---

## 4. Voice and tone

Four attributes. Voice stays constant; tone shifts by context (a payment failure is calmer than a launch post). Say the name **SAAN-tvuh-naa**; write it **Sāntvana** in display copy and **Santvana** in URLs, handles and legal text (see `naming.md` §4).

### 4.1 Plain-spoken

Say the thing. Short sentences. No "innovation", "elevate", "curated", "seamless".

- **Do:** "Fits true to size. Between sizes? Go up."
- **Don't:** "Experience unparalleled comfort engineered for the modern urban lifestyle."

### 4.2 Quietly confident

State the spec and stop. Confidence is a number, not an adjective.

- **Do:** "268 g in a UK 8. Rubber outsole, 4 mm lugs."
- **Don't:** "The most advanced comfort technology ever created."

### 4.3 Warm, not chummy

We are helpful, not performing friendliness. No "Hey bestie", no exclamation marks in transactional email.

- **Do:** "Something's gone wrong on our side. We'll sort it."
- **Don't:** "Oopsie! 🙈 Something went wrong!!!"

### 4.4 Specific to the number

Vague is where trust dies. Dates, weights, timelines, order numbers.

- **Do:** "Refunds land in 5–7 working days. Reference PAY-8F2C19."
- **Don't:** "Refunds will be processed shortly."

### 4.5 Sample copy

**Homepage hero**

> **Sāntvana. Shoes that fit Indian feet.**
> Every last is shaped for our foot widths. Every sole is tested on wet, uneven city ground. Mid-market prices, published materials, free size exchange twice.
> `[ Shop the launch 30 ]`  `[ Find your size ]`

**Product page — Urban Runner, White/Ash**

> **Urban Runner**
> White / Ash · ₹3,499 <s>₹4,299</s> · Inclusive of all taxes
>
> True to size. Wide feet: take a half size up.
> Knit upper, 268 g in a UK 8, rubber outsole with 4 mm lugs. Built for eight-hour days on concrete.
>
> `[ Select size ]`  `[ Add to bag ]`
>
> Free delivery over ₹1,499 · 30-day returns · Free size exchange twice

**Order confirmation email**

> **Subject:** Order A-10428 is confirmed — what happens next
> **Preview:** Packing today. Out the door tomorrow.
>
> Hi Priya,
>
> Your Urban Runner (White/Ash, UK 7) is confirmed. We're packing it at our Bhiwandi warehouse today and it should leave tomorrow.
>
> **Order A-10428 · ₹3,499 · paid by UPI**
> Track it: santvana.example/track/A-10428
>
> You have 30 days to return it and two free size exchanges, no questions asked. If it doesn't fit, reply to this email and we'll send a pickup.
>
> — Team Sāntvana

**Error message — payment failed**

> **We couldn't confirm your payment.**
> Nothing has been charged and your bag is saved. Try again, or pay by UPI — it usually goes through first time.
> If money did leave your account, it comes back within 5–7 working days.
> Reference: `PAY-8F2C19`

**Instagram caption**

> A white sneaker that survives a Bengaluru monsoon is a small miracle. Ours is called Urban Runner. 268 g, knit upper, and a sole that actually grips wet tile.
> Link in bio. #SantvanaFootwear #MadeForTheLongWayHome

> The Urban Runner example is unchanged from v1.0. Only the signature, tracking domain and hashtag move to the new name; the product facts still have to be confirmed in Phase 3. `santvana.example` is a reserved documentation domain, not a live URL.

---

## 5. Phase 2 requirement — bilingual identity

Phase 2 must deliver a bilingual identity, not a Latin wordmark with a Devanagari decoration added at the end.

1. **Lockups.** Three lockups: Latin wordmark (Sāntvana), Devanagari wordmark (सांत्वना — the anusvara form selected on 30 October 2026), and a combination. The combination needs a horizontal lockup for the website header and a stacked lockup for packaging. The two scripts must be optically matched in weight and cap height, not scaled to the same point size.
2. **Devanagari typeface.** Pair one Devanagari family with the Latin display and body faces. Test Noto Serif Devanagari and Noto Sans Devanagari first (both open-licence and self-hostable through `next/font`); choose on the selected anusvara form, the त्व counter and the व/न distinction, not on the headline. The Devanagari face must hold its weight at text sizes and must not look like a fallback.
3. **Minimum size for the chosen mark.** Floor: **20 px on screen** and **6 mm measured wordmark height in print**. The selected anusvara form is tested on the dot and the त्व counter at 1×, 1.5× and 2×, against 40/255 and 128/255. At 16 px on 1×, the dot is 1 × 2 solid px at 50% alpha and is below the floor. At 20 and 24 px the dot passes, but on 1×/50% alpha the full-word त्व counter closes; both pass at DPR ≥ 1.5. On 1×, use 28 px or the Latin monogram. Results are in `logos/legibility-test-anusvara.md`. Re-run after the final Devanagari typeface is chosen; Nirmala UI is a stand-in.
4. **Clear space and misuse.** The Devanagari lockup gets the same clear-space rule as the Latin one, measured from the tallest ascender. Do not set the Devanagari in a Latin typeface, do not add a macron to the Devanagari, and do not use the Devanagari as a pattern or texture.
5. **Deliverables.** Both scripts in the `/brand` route, the token set, the packaging spec and the social templates. A lockup that only works in Latin is not approved.
6. **Small-size rule.** Below **20 px**, use the Latin monogram or symbol, never the Devanagari wordmark. This applies to favicons, app icons, avatars, UI labels and any placement under the floor.

**Sequencing:** concept work may proceed now. No print, domain or ad spend until the attorney opinion in `naming.md` §6 is back. The bilingual requirement is specified now so Phase 2 does not have to be rebuilt later.

**Final-face note (30 October 2026):** Noto Sans Devanagari 600 is the chosen Devanagari face. The final-face re-run passes the automated dot and full-word **त्व** checks at **20 px on 1×**. The **28 px** rule is retained as a conservative design rule, not a measured necessity, until the founder decides between 20 px and 28 px on 1× (see §9). The 20 px absolute floor and 6 mm measured print height are unchanged.

---

## 6. Decisions

Confirmed by the founder on 30 October 2026. Decision 1 remains open only for the attorney opinion and native-speaker test; it no longer blocks concept work.

| # | Decision | Status |
|---|---|---|
| 1 | **Brand name** — Sāntvana is not cleared. Approve it only after the attorney opinion and native-speaker test in `naming.md`? | **Open** — concept work may proceed; no print, domain or ad spend until the opinion is back |
| 2 | Free size exchange **twice** | **Confirmed** — yes |
| 3 | 30-day returns | **Confirmed** — from delivery |
| 4 | Sole/outsole durability warranty | **Confirmed** — no warranty in v1; publish specs instead |
| 5 | Two drops a year | **Confirmed** — yes |

**Price band reconciliation, 31 October 2026:** the Phase 1 band is updated from ₹2,499–₹4,999 to **₹2,299–₹4,999** to match the approved Phase 3 working ladder: good ₹2,299 / ₹2,399 / ₹2,499; better ₹3,499 / ₹3,999; best ₹4,999.

---

## 7. Claims register

Every outward claim that is not yet evidenced. This table is the guardrail for Phases 2, 3 and 8 — no claim ships without the evidence column filled.

| Claim | Where it appears | Status | Evidence needed before publishing |
|---|---|---|---|
| "Lasts shaped for Indian feet" | Positioning, hero, About | **Unverified** | Documented last-development process: foot scans or fit trials, sample size, width data. Otherwise soften to "wider toe box, roomier forefoot" |
| "Tested on wet, uneven city surfaces" | Positioning | **Unverified** | Written test protocol and results (surface types, slip test method, sample size) |
| "Grip that grips wet tile" / "soles built for wet tile" | Instagram, PDP, story | **Unverified** | Coefficient-of-friction test on wet tile, or remove the tile reference |
| "Free size exchange twice" | Promise, email | **Confirmed policy** | Ops cost model; confirmed by founder 30 Oct 2026 |
| "Sāntvana means solace" | Name, About, campaigns | Dictionary meaning; connotation **unverified** | Native-speaker test (`naming.md` §3). If the grief/consolation-prize association dominates, the name changes, not the definition |
| "30-day returns" | About, email | **Confirmed policy — from delivery** | Phase 3 writes the policy; the clock starts at delivery, not dispatch |
| "Designed in Bengaluru, shipped from Bhiwandi" | About | **Unverified** | Confirm actual design location and fulfilment warehouse |
| Any material descriptor (vegan, recycled, sustainable) | — | **Banned in v1** | Supplier certificate per material, per batch |

---

## 8. Approvals

**Phase 1 v1.1 approved by the founder on 30 October 2026.** Approval covers the strategy document, not the unresolved name clearance or the founder-supplied story facts.

- [ ] **Sāntvana approved after attorney opinion** — blocks print, domain and ad spend; concept work may proceed
- [x] Strategy, personas and positioning accepted — Phase 1 v1.1, 30 October 2026
- [x] Primary and secondary taglines accepted — Phase 1 v1.1, 30 October 2026
- [x] Origin story structure accepted — founder-supplied facts still required before public use
- [x] Voice and tone accepted — Phase 1 v1.1, 30 October 2026
- [x] Commercial decisions in §6 confirmed (2–5)
- [ ] Native-speaker connotation test completed (`naming.md` §3)
- [x] Bilingual Devanagari requirement accepted (§5) — Phase 2 proceeds on it
- [x] Devanagari logo form selected: **सांत्वना** (anusvara), 30 October 2026
- [x] Legibility test v2 run on the selected form: dot and full-word त्व counter at 1×/1.5×/2×, 40/255 and 128/255; 20 px approved at DPR ≥ 1.5, 28 px on 1×; 6 mm measured wordmark height print proof pending (`logos/legibility-test-anusvara.md`)
- [ ] Small-size rule accepted: below 20 px use the Latin monogram or symbol, never the Devanagari wordmark
- [x] Legibility test re-run after the final Devanagari typeface is chosen — Noto Sans Devanagari 600, 30 October 2026; 20 px/1× passes the automated check, 28 px retained pending founder decision (`logos/legibility-test-anusvara.md` §5)
- [x] **Phase 2 approved as a concept visual system** — 31 October 2026; the open items in `phase-2/README.md` are kept
- [ ] **Phase 3 catalogue approved** — pending founder review, 31 October 2026

---

## 9. Known open items

Parked deliberately so they are not lost. None of these blocks concept work; all of them block print, domain, ad spend or final approval.

| # | Open item | Why it is open | Owner / next step |
|---|---|---|---|
| 1 | **The 1× rule** | The approved floor is 20 px. The Nirmala UI stand-in failed the full-word त्व counter at 20 and 24 px on 1×, which produced the 28 px practical minimum. The final Noto Sans Devanagari 600 re-run passes at 20 px on 1×. 28 px is now a conservative design rule, not a measured necessity. | Founder decision: keep 28 px on 1× for comfort, or adopt 20 px with 24 px recommended. Record in §5 and `logos/legibility-test-anusvara.md` §5.4. |
| 2 | **The isolated-conjunct label** | The isolated **त्व** is a unit check only. It can pass while the full word fails because the surrounding शिरोरेखा and spacing change the counter. The label "isolated conjunct passes at 24 px" must never be quoted as approval. | Keep the label "unit check only" in every report. The full word governs. Re-check any future deck or summary that cites the isolated result. |
| 3 | **The Noto Sans/Serif test** | Noto Sans Devanagari 600 is selected. Noto Serif Devanagari was tested and rejected for text because its dot and त्व aperture are less robust at 16–24 px. The test used the Google Fonts build, not the self-hosted TTF. | Re-run `logos/legibility-harness.html` with the self-hosted TTF before print approval. The /brand route already self-hosts the family. |
| 4 | **6 mm print proof** | The screen test cannot prove the print floor. | Produce a physical 6 mm measured wordmark-height proof on the actual shoebox and care-card stock once the attorney opinion allows print spend. |
| 5 | **Name clearance and connotation** | The attorney opinion and native-speaker test are founder-run. Sāntvana is not cleared. | No print, domain or ad spend until both are back. If either fails, stop production and re-cut the name before further spend. |
