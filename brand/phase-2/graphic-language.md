# Graphic language — Sāntvana

**Phase 2 · 30 October 2026 · concept only**
No print, domain or ad spend until the attorney opinion in `../naming.md` §6 is back.

---

## 1. The idea: the long line

The primary tagline is **“Made for the long way home.”** The graphic language takes that literally, without turning it into a direction pun.

**The Long Line** is a horizontal rule — 4 px on screen, 2 mm in print — that runs across a layout and then stops. It is the ground line, the platform edge, the top of a wall, the line under a sentence. It never ends in an arrowhead, a chevron or a route marker. The previous arrow mark was dropped for a Class 25 collision; do not bring direction puns back through the graphics.

**The Tread Field** is the symbol's three staggered bars, repeated. It is a texture, not a logo. It appears on tissue, tape, social backgrounds and the inside of the box. It never sits behind body text without a flat scrim.

**The Ground Crop** is a photographic rule: the ground is always in the frame. The shoe is never floating. The crop favours the ankle, the sole and the surface over the face.

**Mile Marks** are section numbers set in Archivo 600: `01`, `02`, `03`. They are labels, not fake wayfinding. No arrows, no dotted paths, no "journey" infographics.

---

## 2. Components

### 2.1 The Long Line

- 4 px ink on paper; 4 px paper on ink; 2 px stone for quiet dividers.
- Full-bleed or inset to the grid; never both on the same screen.
- Can break around the logo, a number or a photograph. It cannot become a border around a card.
- No rounded ends. Square ends only.
- No arrowheads, no chevrons, no dotted or dashed route lines.

### 2.2 The Tread Field

- Built from the three bars: 34 × 7 units, 2-unit gap, staggered left/right.
- Repeat at 24–48 px intervals. At small sizes, reduce to two bars; at large sizes, keep three.
- Ink on paper at 6–10% opacity for backgrounds; paper on ink at 8–12%.
- Never use the wordmark as a pattern. Never use the Devanagari as a texture.
- On packaging tissue, print one colour at 8–12% tint. No full-bleed dark tissue.

### 2.3 Rule weights

- A 1 px stone rule under a section label; a 2 px ink rule under a selected tab; a 4 px clay rule for a single callout.
- Rules are horizontal or vertical. No diagonal dividers, no torn-paper edges, no blob masks.
- A rule can carry a short label at the left, but not a decorative dot at the end.

### 2.4 Type as image

- One statement per surface, left-aligned, ragged right.
- Display type can bleed off the right edge; body copy cannot.
- Use the tagline at 8–12 words maximum. Do not stack three taglines.
- No outline type, no gradient type, no type inside a circle.

### 2.5 Colour blocking

- A full-bleed ink or ground panel for a story beat; paper for the product.
- Clay is a 10% accent: a rule, a button, a single panel, a number.
- No split-screen pastel blocks. No rounded cards floating on a gradient.

---

## 3. Layout

- **Grid:** 12 columns on desktop, 4 on mobile. Gutter 20 px mobile / 40 px desktop. Max width 1280 px.
- **Margins:** 20 px mobile, 40 px desktop. The logo clear space is separate from the page margin.
- **Rhythm:** 64 px between mobile sections, 112 px desktop. One idea per section.
- **Alignment:** left-aligned by default. Centre only the stacked lockup on packaging and the social avatar.
- **Density:** one display element, one body block and one action per screen. If there are two CTAs, one is a text link.
- **No carousels** for the brand system. No auto-playing motion. No parallax.

---

## 4. Motion

- Motion is a reveal, not a performance. 120 ms for a state change, 220 ms for a panel.
- Ease: `cubic-bezier(0.2, 0.7, 0.2, 1)`.
- Respect `prefers-reduced-motion: reduce`; remove transforms and duration.
- No bouncing, no spring, no scroll-jacking, no marquee.
- The Long Line can draw in once on a section entry; it cannot loop.

---

## 5. Social templates

The templates are in `social/`. They are fixed-size HTML/CSS concept boards; export them to PNG only after the name is cleared. The `/brand` route shows scaled previews.

| Format | Size | Margins | Headline | Body | Logo |
|---|---|---:|---|---|---|
| Square | 1080 × 1080 | 72 px | 96 px Archivo 600 | 36 px Inter 400 | Horizontal, 300 px wide |
| Portrait | 1080 × 1350 | 72 px | 112 px Archivo 600 | 40 px Inter 400 | Horizontal, 340 px wide |
| Story | 1080 × 1920 | 96 px top/bottom, 72 px sides | 128 px Archivo 600 | 44 px Inter 400 | Stacked, 300 px wide |

**Rules:**

- One headline, one support line, one mark. No hashtag soup.
- Use the **Long Line** as a divider, not as a decorative frame.
- Use the **Tread Field** only at 8–12% tint behind a solid colour block, never behind the headline.
- Keep the lower 220 px of a story clear for the platform UI.
- Do not put the Devanagari wordmark below 28 px at 1×. On a 1080 px canvas, the horizontal lockup at 300 px wide gives a Devanagari line of about 29 px; that is at the conservative floor. At 280 px stacked, the Deva line is about 27 px; the boards use 300 px or the symbol instead.
- Captions carry the evidence. The image does not claim a test result.

**Template copy (confirmed language only):**

- “Made for the long way home.”
- “Fit first.”
- “Comfort, earned.”
- “Free size exchange twice. 30-day returns from delivery.”
- “Sneakers, runners, everyday, sandals, boots.”

Do not use “tested on wet tile”, “slip-proof”, “vegan”, “recycled” or “sustainable” in a template until the claims register has the evidence.

---

## 6. Email and web

- **Email header:** horizontal lockup 300–320 px wide on a paper background. No hero image in the first email; the mark and the order number are enough.
- **Web header:** horizontal lockup; the Devanagari line must be ≥ 28 px at 1× or ≥ 20 px at DPR ≥ 1.5. On a 1440 px header, the lockup is 300–320 px wide.
- **Favicon:** monogram at 16 px. Do not use the Devanagari wordmark.
- **Buttons:** clay fill, paper label, 2 px radius, no shadow. Focus ring 2 px clay with 2 px offset.
- **Cards:** 1 px stone border, no shadow, 8 px radius. The only rounded element is the card and the symbol; not every surface.
- **Empty states:** one line of plain copy, one action, no illustration of a sad shoe.

---

## 7. Do / do not

| Do | Do not |
|---|---|
| Use one idea per surface | Fill every corner with a badge, a rule and a sticker |
| Let the ground line carry the layout | Use arrows, chevrons or dotted route lines |
| Use the tread field as a quiet texture | Use the wordmark or Devanagari as a pattern |
| Keep the mark small and confident | Make the logo the headline |
| Use flat colour and hard rules | Use gradients, glows, blobs or glassmorphism |
| Use square rules and 8 px card radii | Use pill-shaped everything |
| Use real product detail | Use fake heritage badges, "est. 2026" crests or laurel wreaths |
| Use one accent per screen | Use clay, moss and ochre as equal loud colours |
