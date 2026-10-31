# Colour system — Sāntvana

**Phase 2 · 30 October 2026 · concept only**
All ratios below are calculated with the WCAG 2.2 relative-luminance formula in `contrast.py`. They are not estimates. Re-run `python brand/phase-2/contrast.py` to reproduce them.

---

## 1. The idea

The palette is **ground, paper and one working accent**. It is not a wellness palette: no pastels, no sage-and-blush, no gradients, no soft-focus beige. The base is warm paper and near-black ink; clay is the only loud colour, and it is used like a painted kerb, not a wash. Moss and slate carry quiet sections. Status colours are functional, not decorative.

**60 / 30 / 10:** roughly 60% paper or bone, 30% ink or ground, 10% clay, moss or slate. Clay should be a mark, a rule, a button or a single panel — not a background behind long copy.

---

## 2. Core palette

| Token | Hex | Role | Use on | Do not use for |
|---|---|---|---|---|
| **Ink** | `#171614` | Primary text, strong borders, dark surface | Paper, bone, sand | Long text on clay or moss |
| **Paper** | `#F5F1E8` | Default background, reverse text | Ink, ground, moss, slate | Body text on sand |
| **Ground** | `#2B2722` | Editorial dark surface | Paper, sand, moss-light | Small text on clay |
| **Bone** | `#EAE3D6` | Raised surface, quiet section | Ink, muted | Long text on sand |
| **Sand** | `#D9CBB4` | Warm neutral surface | Ink | Muted body text (3.62:1, fails normal text) |
| **Stone** | `#8C8578` | Decorative rules, 3:1 UI borders | Paper | Body text (3.24:1, fails normal text) |
| **Muted** | `#6B655B` | Secondary text | Paper, bone | Text on sand |
| **Clay** | `#A8452B` | Primary action, links, focus, one accent | Paper, bone | Ink text on clay (3.06:1) |
| **Clay hover** | `#8F3A24` | Primary action hover | Paper | — |
| **Clay pressed** | `#7A301D` | Primary action pressed | Paper | — |
| **Clay light** | `#D98B6F` | Accent text on dark | Ink, ground | Text on paper (2.37:1) |
| **Moss** | `#3E4A3A` | Secondary dark surface | Paper | Body text on ink (1.93:1) |
| **Moss hover** | `#323C2F` | Moss hover | Paper | — |
| **Moss light** | `#A8B5A0` | Muted text on dark | Ink, ground | Text on paper (1.90:1) |
| **Slate** | `#35424C` | Informational dark surface | Paper | Body text on ink (1.75:1) |
| **Ochre** | `#946200` | Warning text and fill | Paper | Large decorative fills on paper |
| **Red** | `#A62B22` | Error text and fill | Paper | — |
| **Green** | `#2F6B4F` | Success text and fill | Paper | — |
| **Blue** | `#2E5E7E` | Informational text and fill | Paper | — |
| **White** | `#FFFFFF` | Optical highlights and image masks only | — | Brand surfaces; it is colder than paper |

---

## 3. Contrast table

WCAG 2.2: **4.5:1** for normal text, **3:1** for large text (18 pt / 24 px regular, or 14 pt / 18.66 px bold) and UI components. "Large / UI" is the 3:1 check.

| Pair | Foreground | Background | Ratio | Normal text | Large / UI |
|---|---|---|---:|---|---|
| Body text | Ink `#171614` | Paper `#F5F1E8` | 16.04:1 | PASS | PASS |
| Secondary text | Muted `#6B655B` | Paper `#F5F1E8` | 5.12:1 | PASS | PASS |
| Tertiary / large only | Stone `#8C8578` | Paper `#F5F1E8` | 3.24:1 | FAIL | PASS |
| Ink on stone | Ink `#171614` | Stone `#8C8578` | 4.94:1 | PASS | PASS |
| Body text on dark | Paper `#F5F1E8` | Ink `#171614` | 16.04:1 | PASS | PASS |
| Secondary on dark | Sand `#D9CBB4` | Ink `#171614` | 11.33:1 | PASS | PASS |
| Muted on dark | Moss light `#A8B5A0` | Ink `#171614` | 8.42:1 | PASS | PASS |
| Accent on dark | Clay light `#D98B6F` | Ink `#171614` | 6.78:1 | PASS | PASS |
| Clay on ink | Clay `#A8452B` | Ink `#171614` | 3.06:1 | FAIL | PASS |
| Primary button label | Paper `#F5F1E8` | Clay `#A8452B` | 5.25:1 | PASS | PASS |
| Primary button hover | Paper `#F5F1E8` | Clay hover `#8F3A24` | 6.66:1 | PASS | PASS |
| Primary button pressed | Paper `#F5F1E8` | Clay pressed `#7A301D` | 8.21:1 | PASS | PASS |
| Link on paper | Clay `#A8452B` | Paper `#F5F1E8` | 5.25:1 | PASS | PASS |
| Focus ring on paper | Clay `#A8452B` | Paper `#F5F1E8` | 5.25:1 | PASS | PASS |
| Border strong | Ink `#171614` | Paper `#F5F1E8` | 16.04:1 | PASS | PASS |
| Border subtle | Stone `#8C8578` | Paper `#F5F1E8` | 3.24:1 | FAIL | PASS |
| Success text | Green `#2F6B4F` | Paper `#F5F1E8` | 5.58:1 | PASS | PASS |
| Warning text | Ochre `#946200` | Paper `#F5F1E8` | 4.65:1 | PASS | PASS |
| Error text | Red `#A62B22` | Paper `#F5F1E8` | 6.23:1 | PASS | PASS |
| Info text | Blue `#2E5E7E` | Paper `#F5F1E8` | 6.17:1 | PASS | PASS |
| Success fill label | Paper `#F5F1E8` | Green `#2F6B4F` | 5.58:1 | PASS | PASS |
| Warning fill label | Paper `#F5F1E8` | Ochre `#946200` | 4.65:1 | PASS | PASS |
| Error fill label | Paper `#F5F1E8` | Red `#A62B22` | 6.23:1 | PASS | PASS |
| Info fill label | Paper `#F5F1E8` | Blue `#2E5E7E` | 6.17:1 | PASS | PASS |
| Moss on paper | Moss `#3E4A3A` | Paper `#F5F1E8` | 8.30:1 | PASS | PASS |
| Slate on paper | Slate `#35424C` | Paper `#F5F1E8` | 9.15:1 | PASS | PASS |
| Ink on bone | Ink `#171614` | Bone `#EAE3D6` | 14.17:1 | PASS | PASS |
| Muted on bone | Muted `#6B655B` | Bone `#EAE3D6` | 4.52:1 | PASS | PASS |
| Ink on sand | Ink `#171614` | Sand `#D9CBB4` | 11.33:1 | PASS | PASS |
| Muted on sand | Muted `#6B655B` | Sand `#D9CBB4` | 3.62:1 | FAIL | PASS |
| Paper on moss | Paper `#F5F1E8` | Moss `#3E4A3A` | 8.30:1 | PASS | PASS |
| Paper on slate | Paper `#F5F1E8` | Slate `#35424C` | 9.15:1 | PASS | PASS |
| Paper on ground | Paper `#F5F1E8` | Ground `#2B2722` | 13.16:1 | PASS | PASS |

**Read the failures:** stone is a border and large-type colour, not body text; where stone is a surface, set ink on it (4.94:1). Muted on sand fails normal text; use ink on sand, or put muted text on paper/bone. Clay on ink is 3.06:1; do not set ink body text on clay. Clay light on paper is 2.37:1; do not use the dark-surface accent on light paper.

---

## 4. Semantic tokens

| Token | Value | Where |
|---|---|---|
| `surface-default` | Paper | Page background |
| `surface-raised` | Bone | Cards, quiet panels |
| `surface-inverse` | Ink | Dark sections, footer |
| `surface-editorial` | Ground | Full-bleed story panels |
| `text-primary` | Ink | Body and headings on light |
| `text-secondary` | Muted | Captions, metadata |
| `text-inverse` | Paper | Body and headings on dark |
| `text-inverse-secondary` | Sand | Captions on dark |
| `text-accent` | Clay | Links, inline emphasis |
| `text-accent-inverse` | Clay light | Accent on dark |
| `action-primary` | Clay | Primary button fill |
| `action-primary-hover` | Clay hover | Hover |
| `action-primary-pressed` | Clay pressed | Pressed |
| `focus-ring` | Clay | 2 px ring, 2 px offset |
| `border-strong` | Ink | Section rules, selected states |
| `border-subtle` | Stone | Quiet dividers, 3:1 UI borders |
| `status-success` | Green | Success text and fill |
| `status-warning` | Ochre | Warning text and fill |
| `status-error` | Red | Error text and fill |
| `status-info` | Blue | Informational text and fill |

---

## 5. Rules

1. **One accent per screen.** Clay is the action colour. If clay is the button, do not also use clay for a headline, a badge and a rule on the same screen.
2. **No gradients.** Flat fills only. Photography can have a natural tonal range; the interface cannot.
3. **No soft shadows.** Use a 1 px stone rule or a 2 px ink rule to separate surfaces. The only shadow allowed is a browser-native focus ring.
4. **No pastels.** Sand and bone are warm neutrals, not pastel pinks or sage. Do not tint them toward rose, lavender or mint.
5. **No colour-only meaning.** Status is always paired with a word or icon. Error red is not the only signal.
6. **No clay body text on ink.** Use paper or sand. Clay light is the dark-surface accent.
7. **No white as a brand surface.** Paper is the brand surface; white is reserved for image masks and optical highlights.
8. **Dark sections are deliberate.** Use ink or ground for a full section, not a card floating on paper. The contrast ratio is the point.

---

## 6. Accessibility notes

- Every text/background pair used in the product must be in the table above or calculated with `contrast.py`.
- Focus state: 2 px clay ring, 2 px offset, visible on paper, bone, sand and ink. On clay fills, use a paper ring.
- Disabled controls: use stone text on bone, with a 1 px stone border. Disabled text is exempt from WCAG contrast, but do not rely on colour alone; use the word "Unavailable" or a lock icon.
- Charts and diagrams: use ink, clay, moss and slate, plus pattern or label. Do not use red/green as the only distinction.
- Photography overlays: if text sits on an image, add a flat ink or paper scrim at the opacity that gets the pair to 4.5:1. Do not use a gradient scrim.
- Test the final rendered colours on the actual display. The ratios are math; the display is the proof.
