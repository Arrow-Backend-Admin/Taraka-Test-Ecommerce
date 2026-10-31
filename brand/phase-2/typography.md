# Typography — Sāntvana

**Phase 2 · 30 October 2026 · concept only**
No print, domain or ad spend until the attorney opinion in `../naming.md` §6 is back.

---

## 1. The pairing

| Role | Family | Weights | Why |
|---|---|---|---|
| Display, wordmark, headings | **Archivo** | 600 display; 500 subhead | A sturdy grotesk with a slightly wide, grounded stance. It is quietly bold without becoming a sports brand. |
| Body, UI, captions | **Inter** | 400, 500, 600 | Neutral, legible at 14–18 px, tabular numerals for prices and sizes. |
| Devanagari, all roles | **Noto Sans Devanagari** | 400, 500, 600, 700 | The most robust of the two candidates at 16–24 px. Holds the anusvara dot and the त्व counter better than Noto Serif. |
| Devanagari test only | **Noto Serif Devanagari** | 400, 500, 600, 700 | Tested and **not selected** for the v1 system. Its dot is smaller at 16 px and its त्व aperture is narrower at 20–24 px. |

All three production families are open-licence Google Fonts and are self-hosted through `next/font/local`. Do not hotlink Google Fonts in production. Keep the OFL licence files with the font files.

**The Latin display is Archivo, not a serif.** The earlier Newsreader direction was tested in `type-test.html` and rejected: a serif Latin and a sans Devanagari fight for the same lockup, and the serif's fine joins do not survive a shoebox. The brand is calm, not editorial-luxury.

---

## 2. The Devanagari test

Test page: `type-test.html`. It sets four pairings side by side at 16, 20, 24, 28, 32 and 48 px:

- A — Archivo + Inter + **Noto Sans Devanagari**
- B — Archivo + Inter + **Noto Serif Devanagari**
- C — Newsreader + Inter + Noto Sans Devanagari
- D — Newsreader + Inter + Noto Serif Devanagari

The decision was made on the full word **सांत्वना**, the **त्व** counter and the **व / न** distinction — not on the 48 px headline.

### 2.1 Anusvara dot at 1×, 128/255, weight 600

| CSS size | Noto Sans Devanagari | Noto Serif Devanagari | Reading |
|---:|---|---|---|
| 16 px | **2 × 2 px** (4 px area) | **2 × 1 px** (2 px area) | Both are below the floor. The serif dot is a single row; it disappears first. |
| 20 px | **2 × 3 px** (6 px area) | **2 × 3 px** (6 px area) | Both pass the dot check. The sans dot is more solid. |
| 24 px | **3 × 3 px** (9 px area) | **3 × 3 px** (7 px area) | Both pass; the sans has more ink. |
| 28 px | **4 × 3 px** (12 px area) | **3 × 3 px** (9 px area) | The sans dot is visibly stronger. |
| 32 px | **4 × 5 px** (16 px area) | **4 × 4 px** (13 px area) | Both are comfortable; the sans still has more presence. |

### 2.2 त्व and व / न

- **Noto Sans Devanagari 600** keeps the full-word **त्व** counter open at **20 px on 1×** in the automated final-face re-run (`../logos/legibility-test-anusvara.md` §5). The waist ratio is 0.22 at 20 px/1×/128, well inside the 0.50 ceiling.
- **Noto Serif Devanagari 600** has a narrower aperture at 20–24 px and a lighter dot. It is not the text face. It may be used for a one-off editorial headline only after a separate test and approval; it is not part of the v1 system.
- The **व / न** distinction is clear in Noto Sans at 20 px. The serif's thin joins make the distinction less immediate at the same size.
- The isolated **त्व** is a unit check only. The full word governs. Do not quote the isolated result as approval.

**Decision: A — Archivo + Inter + Noto Sans Devanagari.** It is the only pairing that holds the personality and the 20 px floor without borrowing wellness cues.

---

## 3. Optical matching

Do not set both scripts at the same point size.

| Context | Latin | Devanagari | Rule |
|---|---|---|---|
| Horizontal lockup | Archivo 600 at 104 units | Noto Sans Devanagari 600 at 66 units | **0.64×** the Latin size, then adjust optically. The Devanagari sits on its own baseline below the Latin, not on the same line. |
| Stacked lockup | Archivo 600 at 92 units | Noto Sans Devanagari 600 at 58 units | **0.63×** the Latin size, centred. |
| Display headline | Archivo 600 | Noto Sans Devanagari 600 at **1.0–1.05×** the Latin size | Devanagari has a smaller x-height; start at 1.05× and check the शिरोरेखा, not the cap height. |
| Body | Inter 400 at 16 px | Noto Sans Devanagari 400 at **17 px** (1.05×) | Same line height; check व/न at 16–17 px. |
| Micro / label | Inter 600 at 12 px | Noto Sans Devanagari 600 at **13 px** | Only for short labels; never the logo. |

**Line height:** Devanagari needs more vertical room than Latin. Use **1.65–1.8** for Devanagari body copy, not 1.5. The शिरोरेखा and matras need air. For display, use 1.15–1.25.

**Tracking:** never add letter-spacing to Devanagari. It breaks the शिरोरेखा and the conjuncts. Latin display uses **-0.035em**; Latin body uses **0**; micro labels use **+0.14em**.

---

## 4. Type scale

| Token | Size | Line height | Family / weight | Use |
|---|---|---|---|---|
| `display-large` | `clamp(4.5rem, 10vw, 8rem)` | 0.92 | Archivo 600 | Campaign statement, one per page |
| `display` | `clamp(3.5rem, 7vw, 5.5rem)` | 0.98 | Archivo 600 | Page title |
| `display-small` | `clamp(2.5rem, 5vw, 3.5rem)` | 1.02 | Archivo 600 | Section title |
| `heading` | 2rem | 1.15 | Archivo 600 | Subsection |
| `heading-small` | 1.5rem | 1.25 | Archivo 500 | Card title |
| `body-large` | 1.125rem | 1.65 | Inter 400 | Lede, product description |
| `body` | 1rem | 1.6 | Inter 400 | Default |
| `small` | 0.875rem | 1.5 | Inter 400/500 | Caption, metadata |
| `micro` | 0.75rem | 1.4 | Inter 600, +0.14em | Eyebrow, label, legal |

**Devanagari body:** use the same scale with a **1.05× size** and **1.65–1.8 line height**. Do not use the Latin line height unchanged.

**Numerals:** Inter with `font-variant-numeric: tabular-nums` for prices, sizes, order numbers and tables. Use Latin digits for prices and sizes even in Hindi copy, so the number is unambiguous. Devanagari digits are allowed in Hindi editorial copy, never in a price.

---

## 5. Spelling and macron rules

- Latin display: **Sāntvana** — macron on the **first ā only**. The final long ā is not marked.
- ASCII / URL / handle / legal: **Santvana**.
- Devanagari: **सांत्वना** (anusvara) is the logo. **सान्त्वना** is valid for search and legal text but is not the logo.
- Do not add a macron to the Devanagari. Do not remove the macron from the Latin display.
- Pronunciation guide: **SAAN-tvuh-naa**. Put it in the About page and the press kit, not in the logo.
- Do not set the name in all caps, small caps or with extra tracking. The macron needs room.

---

## 6. Voice in type

- **Calm:** one display idea per screen. No all-caps shouting, no more than two weights in a section.
- **Grounded:** body copy at 16 px minimum on the web; 14 px only for metadata. Devanagari body at 17 px minimum.
- **Quietly bold:** display type can be large, but the logo stays small. Do not use the wordmark as a headline.
- **Dependable:** prices, sizes and dates use tabular numerals. Do not use decorative numerals.

**Do not:**

- use Noto Serif Devanagari as the body face;
- use a Latin face for Devanagari;
- use faux italic or faux bold;
- underline anything except links;
- use more than three type sizes in one component;
- set Devanagari in all caps (there is no case, but the Latin habit produces bad spacing);
- add letter-spacing to Devanagari;
- use the logo as a letter in a sentence.

---

## 7. Loading and fallback

- **Production:** self-host Archivo, Inter and Noto Sans Devanagari through `next/font/local`. Preload the Latin body and display; do not preload every weight.
- **Logo:** the SVG wordmarks are outlined, so the logo never depends on a font loading.
- **Body fallback:** if Noto Sans Devanagari fails, the browser may fall back to Nirmala UI. That is acceptable for body copy only, never for the logo or a measured lockup. Check the line height and व/न distinction after any fallback change.
- **No hotlinking:** do not load fonts from `fonts.googleapis.com` in production. The test pages may use Google Fonts; the product must self-host.
- **Licence:** keep the OFL licence files with the TTFs. The families are open-licence, but the licence still travels with the files.

---

## 8. Open typography items

- The final self-hosted TTF re-run is required before print approval. The current final-face re-run used the Google Fonts build.
- The 28 px vs 20 px 1× decision is parked in `../strategy.md` §9.
- The 6 mm measured print proof is pending.
- The Hindi taglines **“लंबे रास्ते के लिए बने।”** and **“घर लौटने तक साथ।”** are flagged for native review. Do not set them as final until that review is back.
