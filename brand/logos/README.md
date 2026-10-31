# Sāntvana — bilingual lockup concepts

**Phase 2, step 1 · 30 October 2026**
Status: concept work only. No print, domain or ad spend until the attorney opinion in `../naming.md` §6 is back.

---

## What is here

| File | What it is |
|---|---|
| `santvana-conjunct-horizontal.svg` | Horizontal lockup with **सान्त्वना** (conjunct न्त्व) |
| `santvana-anusvara-horizontal.svg` | Horizontal lockup with **सांत्वना** (anusvara) |
| `santvana-conjunct-stacked.svg` | Stacked lockup with **सान्त्वना** |
| `santvana-anusvara-stacked.svg` | Stacked lockup with **सांत्वना** |
| `lockup-comparison.html` | Side-by-side comparison and selected lockup |
| `legibility-harness.html` | Device-pixel-aware test harness; change the font field and re-run |

All four SVGs are hand-editable: the wordmarks are live `<text>` elements, not outlines. The tread mark is a simple stroke geometry that can become the brand's pattern later.

## Decision (recorded)

**B — सांत्वना (anusvara)** was selected on 30 October 2026. The Latin wordmark, tread mark, spacing and weight are identical in both concepts, so the choice was purely the Devanagari spelling.

- **A — सान्त्वना** is the more literal Sanskrit form and the spelling in the name you supplied. The न्त्व conjunct is the harder shape at small sizes.
- **B — सांत्वना** uses the anusvara dot. Dictionaries use both. It is simpler at small sizes, but the dot can read as decoration if the type is too light.

The formal legibility test on B is in `legibility-test-anusvara.md`. It covers **1×, 1.5× and 2×** at **40/255 and 128/255** alpha. At 16 px on 1×, the Nirmala UI stand-in's solid dot is only 1 × 2 px, so 16 px is below the floor. At 20 and 24 px the dot passes, but the **full-word त्व counter closes at 1×/50% alpha**; both pass at DPR ≥ 1.5. On 1×, the conservative rule is **28 px**. The final Noto Sans Devanagari 600 re-run passes at 20 px/1×; the 28 px rule is parked for founder decision. The **6 mm measured wordmark height print proof is still pending**. Below 20 px, use the Latin monogram or symbol, never the Devanagari wordmark.

## Latin display form — fixed

The Latin brand form is **Sāntvana**, with the macron on the first ā only. The final long ā is not marked in Latin; the Devanagari carries it and the pronunciation guide says -naa. This is stated once in `../naming.md` §4 and applies everywhere.

## Type note

These early comparison SVGs use **Segoe UI** for Latin and **Nirmala UI** for Devanagari as local stand-ins. They are decision records, not production artwork. The Phase 2 concept suite in `../phase-2/logos/` is outlined from **Archivo 600** and **Noto Sans Devanagari 600**.

**Final-face re-run (30 October 2026):** Noto Sans Devanagari 600 passes the automated anusvara-dot and full-word **त्व** checks at **20 px on 1×**. The conservative **28 px** 1× rule is retained pending the founder decision in `../strategy.md` §9. Noto Serif Devanagari was tested and rejected for text: its dot is 2 × 1 px at 16 px and its त्व aperture is narrower at 20–24 px. The self-hosted TTF and the physical 6 mm proof are still required before print approval. Full numbers: `legibility-test-anusvara.md` §5.

## How to view

Open `lockup-comparison.html` in a browser, or open any SVG directly. The comparison page also shows both spellings at 16, 20, 24, 28 and 32 px. Open `legibility-harness.html` to reproduce the device-pixel test and re-run it with the final typeface.
