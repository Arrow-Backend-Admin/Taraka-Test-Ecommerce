# Sāntvana

Concept D2C footwear brand for India. Phase 1 strategy is approved as v1.1; the
naming memo is a risk memo, not a clearance opinion. Phase 2 is the bilingual
visual system: logo suite, colour, typography, imagery, graphic language,
packaging, collateral and design tokens. Phase 3 is the 30-product catalogue,
GST/pricing model, policies, size guide and merchandising plan.

**Status: concept only.** Phase 2 is approved as a concept visual system. Phase 3
is approved as working data, with its open items kept. Phase 4 Milestone 1 is in
progress. No print, domain or ad spend until the attorney opinion and
native-speaker connotation test are back. The name is not cleared.

## View the brand system

```bash
npm install
npm run dev
```

Open `http://localhost:3000/brand`.

The route is a concept brand book, not the storefront. It self-hosts Archivo,
Inter, Noto Sans Devanagari and Noto Serif Devanagari (test only) through
`next/font/local`.

Build checks:

```bash
npm run typecheck
npm run build
```

## Where things are

| Path | Contents |
|---|---|
| `brand/strategy.md` | Phase 1 strategy, v1.1 approvals and open items |
| `brand/naming.md` | Naming risk memo, spelling policy and clearance status |
| `brand/logos/` | Legibility test, harness and decision record |
| `brand/phase-2/` | Phase 2 specs, tokens, static tests and social boards |
| `brand/phase-3/` | Phase 3 catalogue, GST/pricing, policies, size guide, merchandising and seed |
| `brand/phase-4/` | Phase 4 schema gap report and build notes |
| `app/brand/page.tsx` | `/brand` concept route |
| `public/brand/` | Served copies of logos, tokens, tests, social boards and licences |
| `app/fonts/`, `public/fonts/` | Self-hosted TTFs and OFL licence files |

## Reproduce

```bash
python brand/phase-2/generate-logos.py
python brand/phase-2/contrast.py
python brand/phase-3/build_catalogue.py
python brand/phase-3/validate_catalogue.py
python brand/phase-3/seed.py --dry-run
```

The logo SVGs are outlined and self-contained. The contrast ratios are
calculated, not estimated. The social boards are fixed-size HTML/CSS concept
templates; export only after the name is cleared. The Phase 3 seed script needs
`DATABASE_URL` and SQLAlchemy 2.0; `--dry-run` needs neither. See
`brand/phase-3/README.md` for the PostgreSQL command and the open items.

## Guardrails

- No material, sustainability, grip or fit claim without evidence.
- No lorem ipsum, TODO placeholders or invented product facts.
- No hard-coded secrets.
- The Devanagari wordmark has a 20 px absolute screen floor and a 6 mm measured
  print floor. Below 20 px, use the monogram or symbol.
