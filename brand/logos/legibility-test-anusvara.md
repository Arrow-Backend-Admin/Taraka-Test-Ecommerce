# Legibility test — सांत्वना (anusvara)

**Phase 2 · v2 · 30 October 2026**
Chosen lockup: **B — सांत्वना (anusvara)**. Latin display: **Sāntvana**.
Font under test: **Nirmala UI** (local stand-in) for §§1–3. **Final-face re-run: Noto Sans Devanagari 600** for §5.
The final-face numbers are the ones that apply to the Phase 2 concept suite. The 20 px floor and the 6 mm print floor stand; the 28 px 1× rule is now a conservative design rule pending the founder decision recorded in `../strategy.md` §9.

---

## Test conditions

- CSS sizes: **16, 20, 24 and 32 px** for the dot; **20 and 24 px** for the conjunct; **20, 24, 28 and 32 px** for the 1× size sweep.
- Device-pixel ratios: **1×, 1.5× and 2×**.
- Alpha thresholds: **40/255** (antialiased edge) and **128/255** (50% solid).
- The canvas is scaled by the DPR, so all measurements are in **device pixels**. The 20 px floor is **CSS px**; a high-DPR screen gives more device pixels but does not lower the CSS floor.
- **Anusvara dot:** the topmost separate component above the shirorekha in **सांत्वना**.
- **त्व conjunct:** measured in the **full word सांत्वना**, cropped to the त्व region. The isolated conjunct is a unit check only; the full word governs.
  - **Counter:** at least one enclosed hole must survive at the threshold.
  - **Waist:** the horizontal ink-density waist must be ≤ 50% of the lower adjacent peak.
  - Both must pass.
- A dot passes the solid-pixel check when it is at least **2 × 2 device px and 4 px area** at 128/255.

---

## 1. Anusvara dot

| CSS size | DPR | Canvas | Dot at 40/255 | Dot at 128/255 | Separate at 128? | Dot verdict | Overall screen verdict |
|---|---|---|---|---|---|---|---|
| 16 px | 1× | 620 × 240 | 3 × 2 (6 px) | 1 × 2 (2 px) | yes | below CSS floor | **fail — below floor** |
| 16 px | 1.5× | 930 × 360 | 4 × 3 (10 px) | 2 × 3 (6 px) | yes | below CSS floor | **fail — below floor** |
| 16 px | 2× | 1240 × 480 | 4 × 4 (16 px) | 4 × 4 (12 px) | yes | below CSS floor | **fail — below floor** |
| 20 px | 1× | 620 × 240 | 3 × 3 (8 px) | 2 × 3 (6 px) | yes | pass | **marginal — conjunct closes at 1×** |
| 20 px | 1.5× | 930 × 360 | 5 × 4 (16 px) | 3 × 4 (11 px) | yes | pass | **pass** |
| 20 px | 2× | 1240 × 480 | 6 × 5 (25 px) | 4 × 5 (17 px) | yes | pass | **pass** |
| 24 px | 1× | 620 × 240 | 4 × 3 (10 px) | 2 × 3 (6 px) | yes | pass | **marginal — conjunct closes at 1×** |
| 24 px | 1.5× | 930 × 360 | 5 × 5 (21 px) | 5 × 5 (19 px) | yes | pass | **pass** |
| 24 px | 2× | 1240 × 480 | 7 × 6 (34 px) | 5 × 6 (26 px) | yes | pass | **pass** |
| 32 px | 1× | 620 × 240 | 4 × 4 (16 px) | 4 × 4 (12 px) | yes | pass | **pass** |
| 32 px | 1.5× | 930 × 360 | 7 × 6 (34 px) | 5 × 6 (26 px) | yes | pass | **pass** |
| 32 px | 2× | 1240 × 480 | 8 × 8 (54 px) | 8 × 8 (52 px) | yes | pass | **pass** |

**Read this first:** at 16 px on 1×, the 50% solid dot is only **1 × 2 px**. That is below the solid-pixel check and below the CSS floor. At 20 px and 24 px on 1×, the dot passes its own check at 50% alpha, but the full-word **त्व counter closes** — see §2. At 28 px on 1×, the full-word त्व counter passes. 24 px does not rescue 20 px on 1× at the solid threshold.

---

## 2. त्व conjunct

| CSS size | DPR | Threshold | Counter | Waist ratio | Result |
|---|---|---|---|---|---|
| 20 px | 1× | 40/255 | 1 | 0.22 | **pass** |
| 20 px | 1× | 128/255 | **0** | 0.14 | **fail — counter closes** |
| 20 px | 1.5× | 40/255 | 1 | 0.18 | **pass** |
| 20 px | 1.5× | 128/255 | 1 | 0.20 | **pass** |
| 20 px | 2× | 40/255 | 1 | 0.12 | **pass** |
| 20 px | 2× | 128/255 | 1 | 0.14 | **pass** |
| 24 px | 1× | 40/255 | 1 | 0.11 | **pass** |
| 24 px | 1× | 128/255 | **0** | 0.13 | **fail — counter closes** |
| 24 px | 1.5× | 40/255 | 1 | 0.14 | **pass** |
| 24 px | 1.5× | 128/255 | 1 | 0.17 | **pass** |
| 24 px | 2× | 40/255 | 1 | 0.16 | **pass** |
| 24 px | 2× | 128/255 | 1 | 0.18 | **pass** |

### 1× size sweep at 50% alpha

| CSS size | DPR | Threshold | Counter | Waist ratio | Result |
|---|---|---|---|---|---|
| 20 px | 1× | 128/255 | 0 | 0.14 | **fail** |
| 24 px | 1× | 128/255 | 0 | 0.13 | **fail** |
| 28 px | 1× | 128/255 | 1 | 0.22 | **pass** |
| 32 px | 1× | 128/255 | 1 | 0.18 | **pass** |

**Finding:** at **1×/50% alpha**, the full-word त्व counter closes at both **20 px and 24 px**. The isolated conjunct passes at 24 px, but the full word does not; that is why the full word governs. **28 px is the first tested 1× size where the full-word त्व counter passes.** At **1.5× and 2×**, both 20 px and 24 px pass. At 1×/40% alpha they also pass, but 40/255 is the antialiased edge; 128/255 is the approval threshold. The dot is not the failure at 20 or 24 px; the conjunct is.

---

## 3. Decision

- **Screen floor: 20 px CSS.** **Print floor: 6 mm measured wordmark height**, not 6 mm font size. Measure the actual glyph height on the final artwork.
- **Below 20 px:** use the **Latin monogram or symbol**, never the Devanagari wordmark. This covers favicons, app icons, avatars, UI labels and any placement under the floor.
- **20 px is approved only at DPR ≥ 1.5.** On 1×, use **28 px** or the Latin monogram. 20 px on 1× is the absolute floor, not the safe production size.
- **28 px is the first tested 1× size where the full-word त्व counter passes**; **32 px is comfortable**. 24 px is not safe on 1× at the solid threshold.
- **Print is not proven by this test.** The 6 mm measured wordmark height needs a physical proof on the actual shoebox and care-card stock.
- **Final-face re-run completed:** Noto Sans Devanagari 600 passes the automated dot and full-word त्व checks at **20 px on 1×**. The conservative 28 px 1× rule is retained pending the founder decision in §5.4 and `../strategy.md` §9. The self-hosted TTF and the physical 6 mm proof are still required before print approval.

---

## 4. Method notes

- The dot's **solid-pixel size** is its bounding box at 128/255; the area is the number of ink pixels in that component. The 40/255 numbers are reported alongside for comparison.
- The conjunct region is found by measuring the advance width of **सां** and **सांत्व** in the full word, then cropping the त्व span with 1 device-pixel padding. The crop is analysed at the threshold, not scaled.
- The **counter** is the number of enclosed background regions in the cropped त्व cluster at the threshold. A counter closing is a visible loss of the half-त/व distinction, even when the waist ratio still looks acceptable.
- The **waist** is the minimum ink density between the left and right peaks of the lower two-thirds of the conjunct, divided by the lower peak. Lower is better; the pass ceiling is 0.50.
- The harness is `legibility-harness.html`. The font field is now set to **Noto Sans Devanagari**, weight **600**. Press **Run test** to reproduce the final-face numbers below.
- The test is an automated shape-survival check, not a substitute for a human proof. It answers the narrow question: at the floor, do the dot and the त्व counter survive?

---

## 5. Final-face re-run — Noto Sans Devanagari 600

Run on 30 October 2026 in `legibility-harness.html`, using the Google Fonts test build of **Noto Sans Devanagari** at weight **600**. The production `/brand` route self-hosts the same family; the self-hosted TTF must be re-run once before print approval.

### 5.1 Anusvara dot

| CSS size | DPR | Canvas | Dot at 40/255 | Dot at 128/255 | Separate at 128? | Dot verdict | Overall screen verdict |
|---|---|---|---|---|---|---|---|
| 16 px | 1× | 620 × 240 | 3 × 2 (6 px) | 2 × 2 (4 px) | yes | below CSS floor | **fail — below floor** |
| 16 px | 1.5× | 930 × 360 | 4 × 3 (12 px) | 4 × 3 (8 px) | yes | below CSS floor | **fail — below floor** |
| 16 px | 2× | 1240 × 480 | 5 × 4 (18 px) | 5 × 4 (16 px) | yes | below CSS floor | **fail — below floor** |
| 20 px | 1× | 620 × 240 | 4 × 3 (9 px) | 2 × 3 (6 px) | yes | pass | **pass** |
| 20 px | 1.5× | 930 × 360 | 5 × 4 (16 px) | 5 × 4 (15 px) | yes | pass | **pass** |
| 20 px | 2× | 1240 × 480 | 7 × 6 (34 px) | 5 × 6 (26 px) | yes | pass | **pass** |
| 24 px | 1× | 620 × 240 | 4 × 3 (12 px) | 4 × 3 (8 px) | yes | pass | **pass** |
| 24 px | 1.5× | 930 × 360 | 6 × 5 (24 px) | 5 × 5 (21 px) | yes | pass | **pass** |
| 24 px | 2× | 1240 × 480 | 8 × 7 (44 px) | 7 × 7 (38 px) | yes | pass | **pass** |
| 28 px | 1× | 620 × 240 | 5 × 4 (18 px) | 4 × 4 (12 px) | yes | pass | **pass** |
| 28 px | 1.5× | 930 × 360 | 6 × 6 (32 px) | 6 × 6 (32 px) | yes | pass | **pass** |
| 28 px | 2× | 1240 × 480 | 9 × 8 (59 px) | 7 × 8 (48 px) | yes | pass | **pass** |
| 32 px | 1× | 620 × 240 | 5 × 4 (18 px) | 5 × 4 (16 px) | yes | pass | **pass** |
| 32 px | 1.5× | 930 × 360 | 8 × 7 (44 px) | 7 × 7 (38 px) | yes | pass | **pass** |
| 32 px | 2× | 1240 × 480 | 10 × 9 (77 px) | 9 × 9 (61 px) | yes | pass | **pass** |

### 5.2 त्व conjunct in the full word

| CSS size | DPR | Threshold | Counter | Waist ratio | Result |
|---|---|---|---|---|---|
| 20 px | 1× | 40/255 | 1 | 0.40 | **pass** |
| 20 px | 1× | 128/255 | 1 | 0.22 | **pass** |
| 20 px | 1.5× | 40/255 | 1 | 0.29 | **pass** |
| 20 px | 1.5× | 128/255 | 1 | 0.17 | **pass** |
| 20 px | 2× | 40/255 | 1 | 0.22 | **pass** |
| 20 px | 2× | 128/255 | 1 | 0.24 | **pass** |
| 24 px | 1× | 40/255 | 1 | 0.36 | **pass** |
| 24 px | 1× | 128/255 | 1 | 0.30 | **pass** |
| 24 px | 1.5× | 40/255 | 1 | 0.25 | **pass** |
| 24 px | 1.5× | 128/255 | 1 | 0.25 | **pass** |
| 24 px | 2× | 40/255 | 1 | 0.18 | **pass** |
| 24 px | 2× | 128/255 | 1 | 0.20 | **pass** |

### 5.3 1× size sweep at 50% alpha

| CSS size | DPR | Threshold | Counter | Waist ratio | Result |
|---|---|---|---|---|---|
| 20 px | 1× | 128/255 | 1 | 0.22 | **pass** |
| 24 px | 1× | 128/255 | 1 | 0.30 | **pass** |
| 28 px | 1× | 128/255 | 1 | 0.30 | **pass** |
| 32 px | 1× | 128/255 | 1 | 0.29 | **pass** |

### 5.4 What changed

The final face is **more robust at 20 px on 1×** than the Nirmala UI stand-in. The dot is **2 × 3 device px** and the full-word त्व counter survives at 20 px/1×/50% alpha. That means the earlier **28 px practical 1× minimum** is no longer a measured necessity for this face; it is a conservative comfort rule. The **20 px absolute floor** and **6 mm measured print height** are unchanged.

This is one of the three inconsistencies parked in `../strategy.md` §9. Founder decision needed before Phase 3:

- **Keep 28 px on 1×** as the production rule (comfort and consistency with the earlier approved test), or
- **Adopt 20 px on 1×** for the final Noto Sans Devanagari 600 face, with 24 px as the comfortable recommendation.

Until that decision, the concept system uses **20 px absolute floor, 28 px practical 1× minimum, 32 px comfortable**. The 6 mm print proof is still pending.
