# Phase 2 — bilingual visual system

**Sāntvana · 30 October 2026; approved as a concept 31 October 2026**
No print, domain or ad spend until the attorney opinion in `../naming.md` §6 is back. No file here is a print release.

---

## What this phase delivers

| Deliverable | Where | Status |
|---|---|---|
| Bilingual logo suite: horizontal, stacked, Latin, Devanagari, symbol, monogram | `logos/` | Concept, outlined SVG |
| Logo usage, clear space, minimum size and misuse | `logo-usage.md` | Concept spec |
| Colour system with calculated WCAG 2.2 ratios | `colour.md`, `contrast.py` | Ratios verified |
| Typography: Archivo + Inter + Noto Sans Devanagari; Noto Serif tested and rejected | `typography.md`, `type-test.html` | Chosen; self-hosted TTF re-run pending |
| Imagery direction and shot list | `imagery.md` | Concept brief |
| Graphic language: Long Line, Tread Field, Ground Crop, Mile Marks, social formats | `graphic-language.md` | Concept spec |
| Packaging: box, mailer, tissue, care card, sticker, hangtag, size guide | `packaging.md` | Concept spec, no dieline |
| Collateral: card, letterhead, shipping label, thank-you card, email | `collateral.md` | Concept spec |
| Social templates | `social/` | Fixed-size HTML/CSS boards; copied to `apps/storefront/public/brand/social/` |
| Design tokens | `tokens.json`, `tokens.css` | Concept, v0.1.0 |
| `/brand` route | `../../apps/storefront/app/brand/page.tsx` | Next.js concept route; build verified |
| Legibility final-face re-run | `../logos/legibility-test-anusvara.md` §5 | Noto Sans Devanagari 600; 20 px/1× passes |

---

## Decisions made in this phase

1. **Logo form:** **सांत्वना** (anusvara), selected 30 October 2026. **सान्त्वना** remains valid for search/legal, not the logo.
2. **Latin display:** **Archivo 600**. **Body/UI:** **Inter 400–600**. **Devanagari:** **Noto Sans Devanagari 400–700**.
3. **Noto Serif Devanagari** was tested and rejected for text: smaller dot at 16 px and a narrower त्व aperture at 20–24 px. It is not in the production v1 system; it remains only as a test face.
4. **Palette:** warm paper/ink base, clay as the single action accent, moss and slate for quiet dark sections. No pastels, no gradients, no soft shadows.
5. **Graphic language:** the Long Line (a rule that stops), the Tread Field (the symbol's three bars as texture), the Ground Crop (ground always visible) and Mile Marks (section numbers). No arrows, chevrons or direction puns.
6. **Small-size rule:** below 20 px use the monogram (16–19 px) or symbol (20–31 px); never the Devanagari wordmark. The 20 px floor and 6 mm measured print height stand.
7. **1× rule parked:** the final Noto Sans Devanagari 600 re-run passes at 20 px on 1×. The conservative 28 px 1× rule remains until the founder decides. See `../strategy.md` §9.

---

## How to view

### `/brand` route

From the repository root:

```bash
npm install
npm run dev
```

Open `http://localhost:3000/brand`.

The route is a concept brand book, not the storefront. It uses the self-hosted fonts and the same tokens as the rest of the system. It links to static copies in `apps/storefront/public/brand/`: the type test, legibility harness, contrast report, three social boards, `tokens.json` and the font licence.

Build check:

```bash
npm run typecheck
npm run build
```

### Static concept pages

With any static server from the repository root:

```bash
python -m http.server 8000
```

- `http://localhost:8000/brand/phase-2/type-test.html` — the four type pairings.
- `http://localhost:8000/brand/logos/legibility-harness.html` — the device-pixel legibility harness.
- `http://localhost:8000/brand/logos/lockup-comparison.html` — the decision record for the two spellings.
- `http://localhost:8000/brand/phase-2/social/social-1x1.html` — the square social board.
- `http://localhost:8000/brand/phase-2/social/social-4x5.html` — the portrait board.
- `http://localhost:8000/brand/phase-2/social/social-9x16.html` — the story board.

---

## Reproduce the logo suite

```bash
python brand/phase-2/generate-logos.py
```

The generator shapes **Sāntvana** in Archivo 600 and **सांत्वना** in Noto Sans Devanagari 600 with HarfBuzz, then outlines the glyphs with fontTools. It writes the ten SVGs in `logos/`. Copy them to `apps/storefront/public/brand/logos/` for the `/brand` route after regenerating.

## Reproduce the contrast ratios

```bash
python brand/phase-2/contrast.py
```

The output is the source of truth for `colour.md` and the `/brand` route.

---

## What is still open

- **Attorney opinion and native-speaker connotation test.** Founder-run. No print, domain or ad spend until both are back.
- **6 mm measured print proof.** Pending final artwork and stock.
- **Self-hosted TTF legibility re-run.** The final-face re-run used the Google Fonts build; the /brand route self-hosts the TTF. Re-run before print approval.
- **1× rule decision.** 28 px conservative rule vs 20 px final-face result. Parked in `../strategy.md` §9.
- **Founder story facts.** The Phase 1 story structure is approved; the two founder-supplied passages are still required before public use.
- **Phase 2 status.** Approved as a concept visual system on 31 October 2026. The open items above are kept; production is still blocked by the attorney opinion, native-speaker test and print proof. Phase 3 data work may proceed against this concept.

---

## Guardrails

- No print, domain or ad spend until the attorney opinion.
- No material or sustainability claim without a supplier certificate.
- No "slip-proof", "tested on wet tile" or "fits Indian feet" claim without the evidence in `../strategy.md` §7.
- No lorem ipsum, no TODO placeholders, no invented product facts.
- No hard-coded secrets.
- The logo is one colour. The wordmark is not a pattern. The Devanagari is not a decoration.
