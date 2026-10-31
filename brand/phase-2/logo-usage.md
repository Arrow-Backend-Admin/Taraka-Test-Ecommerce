# Logo usage — Sāntvana concept suite

**Phase 2 · 30 October 2026 · concept only**
No print, domain or ad spend until the attorney opinion in `../naming.md` §6 is back. The 6 mm print proof is pending.

---

## 1. What the suite contains

All files are in `logos/`. They are **outlined SVG** — the wordmarks are paths, not live text — so they do not depend on a viewer having Archivo or Noto Sans Devanagari installed. The source generator is `generate-logos.py`.

| File | Use | Notes |
|---|---|---|
| `santvana-horizontal.svg` | Primary horizontal lockup: symbol + Latin + Devanagari | Website header, email header, letterhead, wide packaging panels |
| `santvana-horizontal-reverse.svg` | Primary horizontal lockup, paper on ink | Dark surfaces only |
| `santvana-stacked.svg` | Stacked lockup: symbol above Latin, Devanagari below | Shoebox front, care card, hangtag, social avatar |
| `santvana-stacked-reverse.svg` | Stacked lockup, paper on ink | Dark packaging and social |
| `santvana-wordmark-latin.svg` | Latin wordmark only | Where the Devanagari is supplied separately or the context is Latin-only |
| `santvana-wordmark-devanagari.svg` | Devanagari wordmark only | Hindi-first surfaces, packaging back, editorial |
| `santvana-symbol.svg` | Ground mark: rounded square with three staggered tread bars | 20–31 px, app icon, avatar, pattern seed |
| `santvana-symbol-reverse.svg` | Ground mark, paper on ink | Dark surfaces |
| `santvana-monogram.svg` | S monogram in a rounded square | 16–19 px and favicon; below the Devanagari floor |
| `santvana-monogram-reverse.svg` | S monogram, paper on ink | Dark favicon and app icon |

**The selected Devanagari form is सांत्वना (anusvara).** सान्त्वना remains valid for search and legal text but is not the logo. Do not re-cut the mark to the conjunct form without a new decision.

---

## 2. Which lockup to use

| Context | Lockup | Why |
|---|---|---|
| Website header, desktop | Horizontal | Reads as one bilingual signature; Latin first for scan, Devanagari directly beneath |
| Website header, mobile | Horizontal if the Devanagari line is ≥ 28 px at 1×; otherwise symbol or monogram | Do not shrink the Devanagari below the floor |
| Email header | Horizontal | Fixed width, alt text in both scripts |
| Shoebox front | Stacked | Centred, symmetrical, survives a square panel |
| Shoebox side | Horizontal or Latin wordmark | Horizontal if the panel is wide enough |
| Care card, hangtag | Stacked | Small square format |
| Social avatar | Symbol or monogram | The wordmark is illegible in a circle crop |
| Favicon | Monogram | 16 px; never the Devanagari wordmark |
| App icon | Monogram or symbol | Monogram at 16–19 px; symbol at 20–31 px |
| Hindi-first campaign | Devanagari wordmark or stacked | The Devanagari is not a decoration beneath a Latin headline |

**Do not** put the Latin and Devanagari at the same point size and call it matched. The Devanagari wordmark in the horizontal lockup is set at **0.64×** the Latin size, then adjusted optically. The Devanagari is not a caption; it is the second half of the signature.

---

## 3. Clear space

**Lockups:** clear space = **1× the Latin cap height**, measured from the tallest ascender to the nearest edge, on all four sides. Never less than **24 px on screen** or **4 mm in print**. The space must be empty paper, not a busy image.

**Symbol:** clear space = **0.5× the symbol width** on all sides. At 64 px, that is 32 px.

**Monogram:** clear space = **0.25× the monogram width** on all sides. At 64 px, that is 16 px.

Do not place type, rules, crop marks, stickers or other logos inside the clear-space zone. If a layout cannot give the lockup its clear space, use the symbol or monogram instead.

---

## 4. Minimum size

The floor is set by the **Devanagari wordmark**, not by the whole lockup and not by the Latin.

| Asset | Absolute floor | Practical 1× | Comfortable | Print |
|---|---:|---:|---:|---:|
| Devanagari wordmark | **20 px** | **28 px** (parked decision) | 32 px | **6 mm measured wordmark height** |
| Horizontal lockup | Deva line 20 px (≈208 px wide) | Deva line 28 px (≈291 px wide) | Deva line 32 px (≈333 px wide) | 6 mm measured Deva height |
| Stacked lockup | Deva line 20 px (≈207 px wide) | Deva line 28 px (≈290 px wide) | Deva line 32 px (≈331 px wide) | 6 mm measured Deva height |
| Symbol | 20 px | 24 px | 32 px | 5 mm |
| Monogram | 16 px | 20 px | 24 px | 4 mm |

- **Below 20 px:** use the **monogram** at 16–19 px, or the **symbol** at 20–31 px. Never the Devanagari wordmark.
- **20 px is the absolute floor.** At DPR ≥ 1.5 it passes the automated final-face check. At 1× the conservative rule is 28 px; the final Noto Sans Devanagari 600 re-run passes at 20 px, but the 28 px rule is parked for founder decision (`../strategy.md` §9).
- **The print number is a measured wordmark height, not a point size.** A 6 mm font size is not a 6 mm wordmark. Measure the actual glyph height on the final artwork and stock.
- The 6 mm proof is **pending**. Do not send anything to print before it exists.

---

## 5. Colour

| Surface | Mark | Notes |
|---|---|---|
| Paper `#F5F1E8`, Bone `#EAE3D6`, Sand `#D9CBB4` | Ink `#171614` | Default |
| Ink `#171614`, Ground `#2B2722`, Moss `#3E4A3A`, Slate `#35424C` | Paper `#F5F1E8` | Use the reverse SVG |
| Clay `#A8452B` | Paper `#F5F1E8` | Only for a single accent panel; not for long text |
| Photography | Paper or Ink, with a flat scrim | Never place the mark on a busy image without a scrim |
| Any other colour | Do not | No gradients, no metallic, no outline-only versions |

The logo is **one colour**. The symbol's bars are the surface colour, not a second brand colour. Do not recolour the bars clay or moss.

---

## 6. Misuse

Do not:

- stretch, squash, rotate or skew the lockup;
- set the Devanagari in Archivo, Inter or any Latin face;
- add a macron to the Devanagari, or remove the macron from the Latin;
- add a drop shadow, glow, bevel, outline or gradient;
- place the mark inside a circle, blob or badge that crops the clear space;
- use the Devanagari as a repeating pattern or texture;
- set the wordmark in all caps, small caps or with extra tracking;
- use the mark below the minimum size;
- use the mark as a bullet, a list icon or a replacement for the letter S in body copy;
- combine it with another brand's mark without a written co-branding agreement;
- use the old conjunct SVG as a production asset. It is a decision record only.

The **symbol** may be repeated as a pattern at low contrast, but the **wordmark** may not. The pattern is always the three-bar geometry, never the letters.

---

## 7. Co-branding and partner use

- Equal optical height, not equal width. The partner mark gets its own clear space.
- A co-branded lockup needs a new file; do not assemble one from the two SVGs in a layout tool without approval.
- Do not put the Sāntvana mark on a partner's product, press release or event without a written agreement.
- The name is not cleared. No co-branding, sponsorship or retail partner announcement until the attorney opinion is back.

---

## 8. Production notes

- The SVGs are outlined and self-contained. Keep the source generator so the wordmarks can be re-cut if the type or spelling changes.
- The final Devanagari face is **Noto Sans Devanagari 600**. The /brand route self-hosts the TTF. Re-run `../logos/legibility-harness.html` with the self-hosted file before print approval.
- The 6 mm measured proof is on the actual shoebox and care-card stock, not on office paper.
- No print, domain or ad spend until the attorney opinion. This document is a concept specification, not a print release.
