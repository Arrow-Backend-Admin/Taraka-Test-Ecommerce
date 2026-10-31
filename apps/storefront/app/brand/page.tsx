import { Badge } from "@/components/ui/badge";
import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

type PaletteColour = {
  name: string;
  token: string;
  hex: string;
  role: string;
  dark?: boolean;
};

const nav = [
  { href: "#idea", label: "Idea" },
  { href: "#logo", label: "Logo" },
  { href: "#colour", label: "Colour" },
  { href: "#type", label: "Type" },
  { href: "#language", label: "Language" },
  { href: "#graphic", label: "Graphic" },
  { href: "#packaging", label: "Packaging" },
  { href: "#tokens", label: "Tokens" },
];

const stats = [
  { value: "2", label: "scripts, one signature" },
  { value: "20 px", label: "absolute Devanagari floor" },
  { value: "6 mm", label: "measured print floor" },
  { value: "5", label: "categories at launch" },
];

const personality = ["Calm", "Grounded", "Quietly bold", "Dependable"];

const palette: PaletteColour[] = [
  { name: "Ink", token: "ink", hex: "#171614", role: "Primary text, strong borders, dark surfaces", dark: true },
  { name: "Paper", token: "paper", hex: "#F5F1E8", role: "Default page and packaging background" },
  { name: "Ground", token: "ground", hex: "#2B2722", role: "Editorial dark surface", dark: true },
  { name: "Bone", token: "bone", hex: "#EAE3D6", role: "Raised surface, quiet section fill" },
  { name: "Sand", token: "sand", hex: "#D9CBB4", role: "Warm neutral surface; use ink for text" },
  { name: "Stone", token: "stone", hex: "#8C8578", role: "Decorative rules and 3:1 UI borders" },
  { name: "Muted", token: "muted", hex: "#6B655B", role: "Secondary text on paper and bone", dark: true },
  { name: "Clay", token: "clay", hex: "#A8452B", role: "Primary action, links, focus, one accent", dark: true },
  { name: "Clay light", token: "clay-light", hex: "#D98B6F", role: "Accent text on ink or ground" },
  { name: "Moss", token: "moss", hex: "#3E4A3A", role: "Secondary dark surface", dark: true },
  { name: "Moss light", token: "moss-light", hex: "#A8B5A0", role: "Muted text on dark" },
  { name: "Slate", token: "slate", hex: "#35424C", role: "Informational dark surface", dark: true },
  { name: "Ochre", token: "ochre", hex: "#946200", role: "Warning text and fill", dark: true },
  { name: "Red", token: "red", hex: "#A62B22", role: "Error text and fill", dark: true },
  { name: "Green", token: "green", hex: "#2F6B4F", role: "Success text and fill", dark: true },
  { name: "Blue", token: "blue", hex: "#2E5E7E", role: "Informational text and fill", dark: true },
];

const contrastPairs = [
  { pair: "Body text", fg: "Ink", bg: "Paper", ratio: "16.04:1", normal: "PASS", large: "PASS" },
  { pair: "Secondary text", fg: "Muted", bg: "Paper", ratio: "5.12:1", normal: "PASS", large: "PASS" },
  { pair: "Tertiary / large only", fg: "Stone", bg: "Paper", ratio: "3.24:1", normal: "FAIL", large: "PASS" },
  { pair: "Ink on stone", fg: "Ink", bg: "Stone", ratio: "4.94:1", normal: "PASS", large: "PASS" },
  { pair: "Body on dark", fg: "Paper", bg: "Ink", ratio: "16.04:1", normal: "PASS", large: "PASS" },
  { pair: "Secondary on dark", fg: "Sand", bg: "Ink", ratio: "11.33:1", normal: "PASS", large: "PASS" },
  { pair: "Accent on dark", fg: "Clay light", bg: "Ink", ratio: "6.78:1", normal: "PASS", large: "PASS" },
  { pair: "Primary button label", fg: "Paper", bg: "Clay", ratio: "5.25:1", normal: "PASS", large: "PASS" },
  { pair: "Link on paper", fg: "Clay", bg: "Paper", ratio: "5.25:1", normal: "PASS", large: "PASS" },
  { pair: "Success text", fg: "Green", bg: "Paper", ratio: "5.58:1", normal: "PASS", large: "PASS" },
  { pair: "Warning text", fg: "Ochre", bg: "Paper", ratio: "4.65:1", normal: "PASS", large: "PASS" },
  { pair: "Error text", fg: "Red", bg: "Paper", ratio: "6.23:1", normal: "PASS", large: "PASS" },
  { pair: "Info text", fg: "Blue", bg: "Paper", ratio: "6.17:1", normal: "PASS", large: "PASS" },
  { pair: "Muted on sand", fg: "Muted", bg: "Sand", ratio: "3.62:1", normal: "FAIL", large: "PASS" },
  { pair: "Clay on ink", fg: "Clay", bg: "Ink", ratio: "3.06:1", normal: "FAIL", large: "PASS" },
];

const typeScale = [
  { token: "display-large", size: "clamp(4.5rem, 10vw, 8rem)", lh: "0.92", family: "Archivo 600", use: "Campaign statement" },
  { token: "display", size: "clamp(3.5rem, 7vw, 5.5rem)", lh: "0.98", family: "Archivo 600", use: "Page title" },
  { token: "display-small", size: "clamp(2.5rem, 5vw, 3.5rem)", lh: "1.02", family: "Archivo 600", use: "Section title" },
  { token: "heading", size: "2rem", lh: "1.15", family: "Archivo 600", use: "Subsection" },
  { token: "heading-small", size: "1.5rem", lh: "1.25", family: "Archivo 500", use: "Card title" },
  { token: "body-large", size: "1.125rem", lh: "1.65", family: "Inter 400", use: "Lede, product description" },
  { token: "body", size: "1rem", lh: "1.6", family: "Inter 400", use: "Default" },
  { token: "small", size: "0.875rem", lh: "1.5", family: "Inter 400/500", use: "Caption, metadata" },
  { token: "micro", size: "0.75rem", lh: "1.4", family: "Inter 600, +0.14em", use: "Eyebrow, label, legal" },
];

const dotSizes = [
  { size: "16 px", sans: "2 × 2 px (4 px)", serif: "2 × 1 px (2 px)", note: "Below floor. The serif dot is one row." },
  { size: "20 px", sans: "2 × 3 px (6 px)", serif: "2 × 3 px (6 px)", note: "Both pass the dot check; sans is more solid." },
  { size: "24 px", sans: "3 × 3 px (9 px)", serif: "3 × 3 px (7 px)", note: "Both pass; sans has more ink." },
  { size: "28 px", sans: "4 × 3 px (12 px)", serif: "3 × 3 px (9 px)", note: "Sans is visibly stronger." },
  { size: "32 px", sans: "4 × 5 px (16 px)", serif: "4 × 4 px (13 px)", note: "Both comfortable; sans has more presence." },
];

const openItems = [
  {
    n: "01",
    title: "The 1× rule",
    status: "Founder decision",
    body: "The 20 px floor stands. The earlier Nirmala UI test produced a 28 px practical 1× minimum. The final Noto Sans Devanagari 600 re-run passes at 20 px/1×. Keep 28 px for comfort, or adopt 20 px with 24 px recommended.",
  },
  {
    n: "02",
    title: "The isolated-conjunct label",
    status: "Wording guardrail",
    body: "The isolated त्व is a unit check only. It can pass while the full word fails. The full word governs. Never quote the isolated result as approval.",
  },
  {
    n: "03",
    title: "The Noto Sans/Serif test",
    status: "Re-run pending",
    body: "Noto Sans Devanagari 600 is selected; Noto Serif was tested and rejected for text. The final-face re-run used the Google Fonts build. Re-run with the self-hosted TTF before print approval.",
  },
  {
    n: "04",
    title: "The 6 mm print proof",
    status: "Physical proof pending",
    body: "The screen test cannot prove the print floor. Produce a measured 6 mm Devanagari wordmark height on the actual shoebox and care-card stock.",
  },
  {
    n: "05",
    title: "Name clearance and connotation",
    status: "Blocked",
    body: "The attorney opinion and native-speaker test are founder-run. Sāntvana is not cleared. No print, domain or ad spend until both are back.",
  },
];

const packagingSpecs = [
  ["Shoe box", "330 × 210 × 120 mm", "Two-piece, 1.2–1.5 mm uncoated board, Ink + Clay, no laminate"],
  ["Mailer", "360 × 240 × 140 mm", "E-flute corrugated, one-colour Ink, paper tape"],
  ["Tissue", "500 × 750 mm", "17 gsm, one-colour tread field at 8–12% tint"],
  ["Care card", "90 × 150 mm", "300 gsm uncoated, Ink + Clay, two sides"],
  ["Sticker", "70 mm circle", "80 gsm uncoated, Ink only, seals the tissue"],
  ["Hangtag", "45 × 90 mm", "350 gsm uncoated, Ink + Clay, cotton string"],
  ["Size guide", "105 × 148 mm", "120 gsm uncoated, Ink only, no brand story"],
];

function SectionHeader({
  number,
  kicker,
  title,
  intro,
}: {
  number: string;
  kicker: string;
  title: string;
  intro?: string;
}) {
  return (
    <div className="grid gap-6 border-t border-ink pt-6 md:grid-cols-[11rem_1fr] md:gap-12">
      <div className="eyebrow text-clay">
        {number} / {kicker}
      </div>
      <div>
        <h2 className="display-md max-w-[18ch] text-balance">{title}</h2>
        {intro ? (
          <p className="mt-5 max-w-2xl text-base leading-relaxed text-muted md:text-lg">
            {intro}
          </p>
        ) : null}
      </div>
    </div>
  );
}

function VerdictBadge({ value }: { value: string }) {
  return (
    <Badge variant={value === "PASS" ? "pass" : "fail"} className="whitespace-nowrap">
      {value}
    </Badge>
  );
}

function Swatch({ colour }: { colour: PaletteColour }) {
  return (
    <div className="border border-stone/60">
      <div
        className={cn(
          "flex min-h-28 flex-col justify-between p-4",
          colour.dark ? "text-paper" : "text-ink",
        )}
        style={{ backgroundColor: colour.hex }}
      >
        <span className="font-display text-lg font-semibold tracking-tight">
          {colour.name}
        </span>
        <span className="font-mono text-[0.6875rem] uppercase tracking-[0.08em]">
          {colour.hex}
        </span>
      </div>
      <div className="bg-paper p-4">
        <p className="mono-token text-muted">--color-{colour.token}</p>
        <p className="mt-1 text-xs leading-relaxed text-muted">{colour.role}</p>
      </div>
    </div>
  );
}

function MiniBoard({
  tone,
  headline,
  body,
  logo,
  logoWidth = 686,
  logoHeight = 320,
  ratio,
  aspect,
}: {
  tone: "paper" | "dark" | "ground";
  headline: string;
  body: string;
  logo: string;
  logoWidth?: number;
  logoHeight?: number;
  ratio: string;
  aspect: string;
}) {
  return (
    <div
      className={cn(
        "relative flex flex-col overflow-hidden border border-stone/60 p-4",
        tone === "paper" && "bg-paper text-ink",
        tone === "dark" && "bg-ink text-paper",
        tone === "ground" && "bg-ground text-paper",
      )}
      style={{ aspectRatio: aspect }}
    >
      <div
        className={cn(
          "eyebrow",
          tone === "paper" ? "text-clay" : "text-clay-light",
        )}
      >
        Sāntvana · {ratio}
      </div>
      <p className="mt-auto font-display text-2xl font-semibold leading-[0.95] tracking-[-0.035em]">
        {headline}
      </p>
      <p className="mt-2 max-w-[28ch] text-[0.6875rem] leading-relaxed opacity-80">{body}</p>
      <div
        className={cn(
          "mt-3 h-[4px] w-24",
          tone === "paper" ? "bg-clay" : "bg-clay-light",
        )}
      />
      <img
        src={logo}
        width={logoWidth}
        height={logoHeight}
        alt="Sāntvana bilingual lockup"
        className={cn(
          "mt-4 w-full",
          ratio === "1:1" ? "max-w-[170px]" : "max-w-[190px]",
        )}
      />
    </div>
  );
}

export default function BrandPage() {
  return (
    <div id="top" className="min-h-screen bg-paper text-ink">
      <header className="border-b border-stone/60">
        <div className="container-brand flex flex-wrap items-center justify-between gap-5 py-5">
          <a href="#top" className="flex items-center gap-3">
            <img
              src="/brand/logos/santvana-symbol.svg"
              width={64}
              height={64}
              alt=""
              className="h-8 w-8"
            />
            <span>
              <span className="block font-display text-base font-semibold leading-none tracking-tight">
                Sāntvana
              </span>
              <span className="mt-1 block text-[0.625rem] font-medium uppercase tracking-[0.14em] text-muted">
                Brand system · Phase 2
              </span>
            </span>
            <span className="sr-only">Back to top</span>
          </a>
          <nav className="hidden items-center gap-5 text-xs font-medium text-muted lg:flex" aria-label="Sections">
            {nav.map((item) => (
              <a key={item.href} href={item.href} className="hover:text-ink">
                {item.label}
              </a>
            ))}
          </nav>
          <span className="concept-badge">Concept · not for print</span>
        </div>
      </header>

      <main>
        <section className="relative overflow-hidden border-b border-stone/60">
          <div className="container-brand grid gap-12 py-14 md:py-20 lg:grid-cols-[1.05fr_0.95fr] lg:items-center lg:gap-16">
            <div>
              <span className="concept-badge">Phase 2 · awaiting founder approval</span>
              <h1 className="display-xl mt-8 max-w-[11ch] text-balance">
                Calm, grounded, quietly bold.
              </h1>
              <p className="mt-7 max-w-xl text-lg leading-relaxed text-muted">
                A bilingual visual system for the long way home. One name in two
                scripts, a ground mark built from tread, warm paper and ink, and a
                type pairing that holds at 20 px.
              </p>
              <div className="mt-8 flex flex-wrap gap-3">
                <a href="#logo" className={buttonVariants()}>
                  See the system
                </a>
                <a href="#approval" className={buttonVariants({ variant: "outline" })}>
                  Open items
                </a>
              </div>
              <p className="mt-6 max-w-lg text-xs leading-relaxed text-muted">
                No print, domain or ad spend until the attorney opinion in{" "}
                <span className="mono-token">brand/naming.md §6</span>. Every asset on
                this page is a concept.
              </p>
            </div>

            <div className="relative">
              <div className="absolute -right-10 -top-10 h-48 w-48 tread-field-dark opacity-60" aria-hidden="true" />
              <div className="relative border border-ink bg-ground p-6 text-paper md:p-10">
                <div className="flex items-center justify-between gap-4 border-b border-paper/20 pb-4">
                  <span className="eyebrow text-clay-light">01 / Signature</span>
                  <span className="font-deva text-sm text-sand">सांत्वना</span>
                </div>
                <img
                  src="/brand/logos/santvana-stacked-reverse.svg"
                  width={600}
                  height={420}
                  alt="Sāntvana stacked bilingual lockup in paper on ink"
                  className="mx-auto mt-8 w-full max-w-[320px]"
                  loading="eager"
                />
                <div className="mt-8 flex items-end justify-between gap-4 border-t border-paper/20 pt-4">
                  <p className="max-w-[16ch] text-sm leading-snug text-sand">
                    Made for the long way home.
                  </p>
                  <span className="eyebrow text-paper/60">Concept</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="border-b border-stone/60 bg-bone">
          <div className="container-brand grid grid-cols-2 gap-px md:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="border-l border-stone/50 px-5 py-6 first:border-l-0">
                <p className="font-display text-3xl font-semibold tracking-tight md:text-4xl">
                  {stat.value}
                </p>
                <p className="mt-2 max-w-[18ch] text-xs leading-relaxed text-muted">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        </section>

        <section id="idea" className="section-space">
          <div className="container-brand">
            <SectionHeader
              number="01"
              kicker="The idea"
              title="A route, not a mood."
              intro="Sāntvana means solace, but the system is not a spa. It is the relief of a shoe that fits on the walk between the station and the desk. The ground is the hero; the mark is quiet; the promise is specific."
            />

            <div className="mt-12 grid gap-8 lg:grid-cols-[1fr_0.9fr]">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Personality</p>
                <div className="mt-4 flex flex-wrap gap-2">
                  {personality.map((item) => (
                    <Badge key={item} variant="outline" className="normal-case tracking-normal">
                      {item}
                    </Badge>
                  ))}
                </div>
                <p className="mt-8 max-w-xl text-base leading-relaxed text-muted">
                  Calm is not softness. Grounded is not rustic. Quietly bold is not a
                  loud logo. Dependable is not a warranty we cannot honour. The
                  identity has to look like it can carry a wet Monday.
                </p>
                <div className="mt-8 rule-long text-ink" />
                <p className="mt-5 max-w-xl text-sm leading-relaxed text-muted">
                  The previous arrow mark was dropped for a Class 25 collision. The
                  graphic language uses a line that stops, not an arrow that points.
                </p>
              </div>

              <div className="border border-ink bg-ink p-6 text-paper md:p-8">
                <p className="eyebrow text-clay-light">The promise</p>
                <p className="mt-5 font-display text-3xl font-semibold leading-[1.02] tracking-[-0.035em] md:text-4xl">
                  Right fit, first pair — or we exchange it free, twice.
                </p>
                <p className="mt-5 max-w-md text-sm leading-relaxed text-sand">
                  Confirmed policy. Free size exchange twice. 30-day returns from
                  delivery. No warranty in v1.
                </p>
                <div className="mt-8 border-t border-paper/20 pt-4">
                  <p className="font-deva text-xl leading-relaxed text-paper">
                    सांत्वना
                  </p>
                  <p className="mt-1 text-xs text-paper/60">
                    The Devanagari is the other half of the signature, not a caption.
                  </p>
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {[
                ["No wellness cues", "No lotus, hands, candles, pastels, spa stones or “mindful” bare feet."],
                ["No unverified claims", "No slip-proof, vegan, recycled or “fits Indian feet” copy without evidence."],
                ["No print release", "Concept work only until the attorney opinion, native review and 6 mm proof."],
              ].map(([title, body]) => (
                <div key={title} className="border-t border-ink pt-4">
                  <p className="font-display text-lg font-semibold tracking-tight">{title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="logo" className="section-space border-t border-stone/60 bg-bone">
          <div className="container-brand">
            <SectionHeader
              number="02"
              kicker="Signature"
              title="One name. Two scripts. One line."
              intro="The selected form is सांत्वना with the anusvara. The Latin is Sāntvana with a macron on the first ā only. The mark is outlined, one colour, and in production is never set below the Devanagari floor."
            />

            <div className="mt-12 border border-stone/60 bg-paper p-6 md:p-10">
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <p className="eyebrow text-clay">Primary horizontal lockup</p>
                  <p className="mt-2 max-w-md text-sm leading-relaxed text-muted">
                    Use at 300 px wide or larger on a 1× screen. The Devanagari line is
                    then about 29 px. At DPR ≥ 1.5, the lockup can go down to 208 px.
                  </p>
                </div>
                <Badge variant="outline">Outlined SVG</Badge>
              </div>
              <img
                src="/brand/logos/santvana-horizontal.svg"
                width={686}
                height={320}
                alt="Sāntvana horizontal bilingual lockup: ground mark, Latin Sāntvana, Devanagari सांत्वना"
                className="mx-auto mt-8 w-full max-w-[640px]"
              />
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  src: "/brand/logos/santvana-stacked.svg",
                  w: 600,
                  h: 420,
                  title: "Stacked lockup",
                  body: "Shoebox front, care card, hangtag. The square format that survives a centred panel.",
                  bg: "bg-paper",
                },
                {
                  src: "/brand/logos/santvana-horizontal-reverse.svg",
                  w: 686,
                  h: 320,
                  title: "Horizontal reverse",
                  body: "Ink, ground, moss and slate surfaces. Paper mark, no recolouring.",
                  bg: "bg-ink",
                },
                {
                  src: "/brand/logos/santvana-stacked-reverse.svg",
                  w: 600,
                  h: 420,
                  title: "Stacked reverse",
                  body: "Dark packaging and social. The symbol’s bars are the surface colour, not a second brand colour.",
                  bg: "bg-ground",
                },
                {
                  src: "/brand/logos/santvana-wordmark-latin.svg",
                  w: 376,
                  h: 149,
                  title: "Latin wordmark",
                  body: "Latin-only contexts. Never remove the macron from the display spelling.",
                  bg: "bg-paper",
                },
                {
                  src: "/brand/logos/santvana-wordmark-devanagari.svg",
                  w: 554,
                  h: 129,
                  title: "Devanagari wordmark",
                  body: "Hindi-first surfaces and packaging backs. Not a decorative subtitle.",
                  bg: "bg-bone",
                },
                {
                  src: "/brand/logos/santvana-symbol.svg",
                  w: 64,
                  h: 64,
                  title: "Ground mark + monogram",
                  body: "Symbol at 20–31 px; monogram at 16–19 px and favicon. Below 20 px, never the Devanagari wordmark.",
                  bg: "bg-paper",
                },
              ].map((asset) => {
                const dark = asset.bg === "bg-ink" || asset.bg === "bg-ground";
                return (
                  <div key={asset.title} className={cn("border border-stone/60 p-5", asset.bg)}>
                    <div className="flex min-h-28 items-center justify-center">
                      <img
                        src={asset.src}
                        width={asset.w}
                        height={asset.h}
                        alt={asset.title}
                        className={cn(
                          "max-h-24 w-auto",
                          asset.src.includes("wordmark") ? "max-w-[180px]" : "max-w-[210px]",
                          asset.src.includes("symbol") && "max-h-16",
                        )}
                      />
                    </div>
                    <p
                      className={cn(
                        "mt-4 font-display text-lg font-semibold tracking-tight",
                        dark ? "text-paper" : "text-ink",
                      )}
                    >
                      {asset.title}
                    </p>
                    <p className={cn("mt-1 text-xs leading-relaxed", dark ? "text-sand" : "text-muted")}>
                      {asset.body}
                    </p>
                  </div>
                );
              })}
            </div>

            <div className="mt-8 grid gap-8 lg:grid-cols-2">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Clear space</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  1× the Latin cap height on all four sides, never less than 24 px on
                  screen or 4 mm in print. The space is empty paper, not a busy image.
                </p>
                <div className="relative mt-6 border border-dashed border-clay p-8">
                  <span className="absolute left-2 top-2 font-mono text-[0.625rem] uppercase tracking-[0.1em] text-clay">
                    1×
                  </span>
                  <img
                    src="/brand/logos/santvana-horizontal.svg"
                    width={686}
                    height={320}
                    alt="Horizontal lockup inside its clear-space zone"
                    className="mx-auto w-full max-w-[360px]"
                  />
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">
                  Symbol: 0.5× symbol width. Monogram: 0.25× monogram width. If the
                  layout cannot give the lockup its clear space, use the symbol.
                </p>
              </div>

              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Minimum size</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  The floor is set by the Devanagari wordmark, not the whole lockup.
                  The final face passes at 20 px on 1×; 28 px is retained as the
                  conservative design rule pending founder decision.
                </p>
                <div className="mt-6 space-y-4">
                  {[
                    { size: 16, verdict: "Fail — below floor", pass: false },
                    { size: 20, verdict: "Pass — absolute floor", pass: true },
                    { size: 28, verdict: "Pass — conservative 1×", pass: true },
                    { size: 32, verdict: "Comfortable", pass: true },
                  ].map((row) => (
                    <div key={row.size} className="flex items-center gap-4 border-t border-stone/50 pt-3">
                      <span className="w-12 font-mono text-[0.6875rem] text-muted">{row.size} px</span>
                      <span className="font-deva min-w-0 flex-1" style={{ fontSize: `${row.size}px`, lineHeight: 1.2 }}>
                        सांत्वना
                      </span>
                      <Badge variant={row.pass ? "pass" : "fail"} className="hidden sm:inline-flex">
                        {row.verdict}
                      </Badge>
                    </div>
                  ))}
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">
                  Below 20 px: monogram at 16–19 px, symbol at 20–31 px. Print floor:
                  6 mm measured wordmark height, not point size.
                </p>
              </div>
            </div>

            <div className="mt-8 border border-ink bg-paper p-6 md:p-8">
              <p className="eyebrow text-clay">Do not</p>
              <div className="mt-5 grid gap-x-8 gap-y-3 text-sm leading-relaxed text-muted md:grid-cols-2">
                {[
                  "Stretch, squash, rotate or skew the lockup.",
                  "Set the Devanagari in Archivo, Inter or any Latin face.",
                  "Add a macron to the Devanagari, or remove the Latin macron.",
                  "Add a shadow, glow, bevel, outline or gradient.",
                  "Use the Devanagari as a pattern or texture.",
                  "Use the old conjunct SVG as a production asset.",
                  "Place the mark on a busy image without a flat scrim.",
                  "Use the wordmark below the minimum size.",
                ].map((item) => (
                  <p key={item} className="flex gap-3 border-t border-stone/40 pt-3">
                    <span className="font-mono text-[0.625rem] text-clay">×</span>
                    {item}
                  </p>
                ))}
              </div>
            </div>
          </div>
        </section>

        <section id="colour" className="section-space border-t border-stone/60">
          <div className="container-brand">
            <SectionHeader
              number="03"
              kicker="Colour"
              title="Ground, paper, one working accent."
              intro="Warm paper and near-black ink carry the system. Clay is the only loud colour; moss and slate hold quiet dark sections. No pastels, no gradients, no soft shadows. Every ratio below is calculated, not estimated."
            />

            <div className="mt-12 grid gap-4 md:grid-cols-3">
              {[
                { name: "Paper", hex: "#F5F1E8", text: "text-ink", note: "The default. Warm, not white." },
                { name: "Ink", hex: "#171614", text: "text-paper", note: "Text, rules, dark surfaces." },
                { name: "Clay", hex: "#A8452B", text: "text-paper", note: "One accent. Action, link, focus." },
              ].map((colour) => (
                <div
                  key={colour.name}
                  className={cn("flex min-h-48 flex-col justify-between border border-stone/60 p-6", colour.text)}
                  style={{ backgroundColor: colour.hex }}
                >
                  <p className="font-display text-3xl font-semibold tracking-tight">{colour.name}</p>
                  <div>
                    <p className="font-mono text-xs uppercase tracking-[0.08em]">{colour.hex}</p>
                    <p className="mt-2 max-w-[22ch] text-sm leading-snug">{colour.note}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              {palette.map((colour) => (
                <Swatch key={colour.token} colour={colour} />
              ))}
            </div>

            <div className="mt-10 border border-stone/60 bg-paper">
              <div className="flex flex-wrap items-end justify-between gap-4 border-b border-stone/60 p-5">
                <div>
                  <p className="eyebrow text-clay">Contrast table</p>
                  <p className="mt-2 max-w-xl text-sm leading-relaxed text-muted">
                    WCAG 2.2: 4.5:1 normal text, 3:1 large text and UI. Calculated in
                    <span className="mono-token"> brand/phase-2/contrast.py</span>.
                  </p>
                </div>
                <Badge variant="outline">Verified math</Badge>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-stone/60 text-[0.6875rem] uppercase tracking-[0.1em] text-muted">
                      <th className="p-4 font-semibold" scope="col">Pair</th>
                      <th className="p-4 font-semibold" scope="col">Foreground</th>
                      <th className="p-4 font-semibold" scope="col">Background</th>
                      <th className="p-4 font-semibold" scope="col">Ratio</th>
                      <th className="p-4 font-semibold" scope="col">Normal</th>
                      <th className="p-4 font-semibold" scope="col">Large / UI</th>
                    </tr>
                  </thead>
                  <tbody>
                    {contrastPairs.map((row) => (
                      <tr key={row.pair} className="border-b border-stone/30 last:border-b-0">
                        <td className="p-4 font-medium">{row.pair}</td>
                        <td className="p-4 text-muted">{row.fg}</td>
                        <td className="p-4 text-muted">{row.bg}</td>
                        <td className="p-4 font-mono text-xs">{row.ratio}</td>
                        <td className="p-4"><VerdictBadge value={row.normal} /></td>
                        <td className="p-4"><VerdictBadge value={row.large} /></td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              <div className="border-t border-stone/60 p-5 text-xs leading-relaxed text-muted">
                Read the failures: stone is a border and large-type colour, not body
                text. Muted on sand fails normal text; use ink on sand. Clay on ink is
                3.06:1; do not set ink body text on clay.
              </div>
            </div>

            <div className="mt-8 grid gap-6 border border-ink bg-ink p-6 text-paper md:grid-cols-[1fr_0.8fr] md:p-10">
              <div>
                <p className="eyebrow text-clay-light">Dark surfaces</p>
                <p className="mt-4 max-w-lg font-display text-3xl font-semibold leading-[1.02] tracking-[-0.035em]">
                  Dark sections are deliberate, not a theme toggle.
                </p>
                <p className="mt-4 max-w-lg text-sm leading-relaxed text-sand">
                  Use ink or ground for a full section. Paper text is 16.04:1 on ink.
                  Clay light is the accent at 6.78:1. Never use clay body text on ink.
                </p>
              </div>
              <img
                src="/brand/logos/santvana-horizontal-reverse.svg"
                width={686}
                height={320}
                alt="Sāntvana horizontal reverse lockup on ink"
                className="w-full max-w-[320px] self-center justify-self-start md:justify-self-end"
              />
            </div>
          </div>
        </section>

        <section id="type" className="section-space border-t border-stone/60 bg-bone">
          <div className="container-brand">
            <SectionHeader
              number="04"
              kicker="Typography"
              title="Archivo, Inter, Noto Sans Devanagari."
              intro="A sturdy grotesk for the display, a neutral UI face, and the Devanagari that survived the 20 px test. Noto Serif Devanagari was tested and rejected for text: smaller dot, narrower त्व aperture."
            />

            <div className="mt-12 border border-stone/60 bg-paper p-6 md:p-10">
              <div className="grid gap-10 lg:grid-cols-[1.1fr_0.9fr] lg:items-end">
                <div>
                  <p className="eyebrow text-clay">Latin display</p>
                  <p className="mt-4 font-display text-[clamp(4rem,12vw,9rem)] font-semibold leading-[0.85] tracking-[-0.055em]">
                    Sāntvana
                  </p>
                  <p className="mt-4 max-w-md text-sm leading-relaxed text-muted">
                    Macron on the first ā only. Final long ā unmarked. ASCII fallback
                    Santvana for URLs, handles and legal text.
                  </p>
                </div>
                <div className="border-t border-stone/60 pt-8 lg:border-l lg:border-t-0 lg:pl-10 lg:pt-0">
                  <p className="eyebrow text-clay">Devanagari display</p>
                  <p className="font-deva mt-4 text-[clamp(3.5rem,10vw,7.5rem)] font-semibold leading-[0.95]">
                    सांत्वना
                  </p>
                  <p className="mt-4 max-w-md text-sm leading-relaxed text-muted">
                    Anusvara, not the conjunct. सान्त्वना stays valid for search and
                    legal text, but it is not the logo.
                  </p>
                </div>
              </div>
              <div className="mt-10 grid gap-4 border-t border-stone/60 pt-6 md:grid-cols-3">
                {[
                  ["Archivo", "Display · 600", "Sturdy, slightly wide, quietly bold. The wordmark and headings."],
                  ["Inter", "Body · 400–600", "Neutral, legible, tabular numerals for prices and sizes."],
                  ["Noto Sans Devanagari", "All Devanagari · 400–700", "The final face. Holds the dot and the त्व counter at 20 px."],
                ].map(([name, weight, body]) => (
                  <div key={name}>
                    <p className="font-display text-lg font-semibold tracking-tight">{name}</p>
                    <p className="mt-1 font-mono text-[0.625rem] uppercase tracking-[0.1em] text-clay">{weight}</p>
                    <p className="mt-2 text-xs leading-relaxed text-muted">{body}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="eyebrow text-clay">Selected</p>
                  <Badge variant="pass">Noto Sans Devanagari</Badge>
                </div>
                <p className="font-deva mt-5 text-5xl font-semibold leading-tight">सांत्वना</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  At 20 px/1×, the dot is 2 × 3 px and the full-word त्व counter
                  survives. The final-face re-run is in{" "}
                  <span className="mono-token">legibility-test-anusvara.md §5</span>.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  {[20, 24, 28, 32].map((size) => (
                    <span key={size} className="border border-stone/60 px-3 py-2">
                      <span className="block font-mono text-[0.5625rem] uppercase tracking-[0.1em] text-muted">{size} px</span>
                      <span className="font-deva block" style={{ fontSize: `${size}px`, lineHeight: 1.2 }}>सांत्वना</span>
                    </span>
                  ))}
                </div>
              </div>

              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="eyebrow text-clay">Tested, not selected</p>
                  <Badge variant="outline">Noto Serif Devanagari</Badge>
                </div>
                <p className="font-deva-test mt-5 text-5xl font-semibold leading-tight">सांत्वना</p>
                <p className="mt-3 text-sm leading-relaxed text-muted">
                  The dot is 2 × 1 px at 16 px and the त्व aperture is narrower at
                  20–24 px. Serif is a possible one-off editorial voice, not the v1
                  text face.
                </p>
                <div className="mt-5 flex flex-wrap gap-3">
                  {[20, 24, 28, 32].map((size) => (
                    <span key={size} className="border border-stone/60 px-3 py-2">
                      <span className="block font-mono text-[0.5625rem] uppercase tracking-[0.1em] text-muted">{size} px</span>
                      <span className="font-deva-test block" style={{ fontSize: `${size}px`, lineHeight: 1.2 }}>सांत्वना</span>
                    </span>
                  ))}
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-8 lg:grid-cols-[0.9fr_1.1fr]">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Anusvara dot at 1×</p>
                <p className="mt-2 text-xs leading-relaxed text-muted">
                  Weight 600, 128/255 threshold. Measured from the rendered glyph.
                </p>
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full min-w-[420px] border-collapse text-left text-sm">
                    <thead>
                      <tr className="border-b border-stone/60 text-[0.625rem] uppercase tracking-[0.1em] text-muted">
                        <th className="py-3 pr-3 font-semibold" scope="col">Size</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">Sans</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">Serif</th>
                      </tr>
                    </thead>
                    <tbody>
                      {dotSizes.map((row) => (
                        <tr key={row.size} className="border-b border-stone/30 last:border-b-0">
                          <td className="py-3 pr-3 font-mono text-xs">{row.size}</td>
                          <td className="py-3 pr-3">{row.sans}</td>
                          <td className="py-3 pr-3 text-muted">{row.serif}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Type scale</p>
                <div className="mt-5 overflow-x-auto">
                  <table className="w-full min-w-[520px] border-collapse text-left text-sm">
                    <thead>
                      <tr className="border-b border-stone/60 text-[0.625rem] uppercase tracking-[0.1em] text-muted">
                        <th className="py-3 pr-3 font-semibold" scope="col">Token</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">Size</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">LH</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">Family</th>
                        <th className="py-3 pr-3 font-semibold" scope="col">Use</th>
                      </tr>
                    </thead>
                    <tbody>
                      {typeScale.map((row) => (
                        <tr key={row.token} className="border-b border-stone/30 last:border-b-0">
                          <td className="py-3 pr-3 font-mono text-[0.6875rem]">{row.token}</td>
                          <td className="py-3 pr-3 text-muted">{row.size}</td>
                          <td className="py-3 pr-3 font-mono text-xs">{row.lh}</td>
                          <td className="py-3 pr-3 text-muted">{row.family}</td>
                          <td className="py-3 pr-3 text-muted">{row.use}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {[
                ["Optical match", "Devanagari display at 0.64× the Latin wordmark. Body at 1.05×, with 1.65–1.8 line height. Never add letter-spacing to Devanagari."],
                ["No faux styles", "No faux italic, faux bold, outline type or all-caps Devanagari. Use real weights."],
                ["Self-host", "The product self-hosts Archivo, Inter and Noto Sans Devanagari. The logo is outlined, so it never depends on a font loading."],
              ].map(([title, body]) => (
                <div key={title} className="border-t border-ink pt-4">
                  <p className="font-display text-lg font-semibold tracking-tight">{title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
                </div>
              ))}
            </div>

            <div className="mt-8 flex flex-wrap gap-x-6 gap-y-2 border-t border-stone/60 pt-5 text-sm">
              <a href="/brand/type-test.html" className="link-underline">
                Open the type test
              </a>
              <a href="/brand/legibility-harness.html" className="link-underline">
                Open the legibility harness
              </a>
              <a href="/brand/contrast-report.md" className="link-underline">
                Contrast report
              </a>
              <a href="/fonts/OFL.txt" className="link-underline">
                Font licence
              </a>
            </div>
          </div>
        </section>

        <section id="language" className="section-space border-t border-stone/60">
          <div className="container-brand">
            <SectionHeader
              number="05"
              kicker="Language"
              title="Bilingual, not decorated."
              intro="The Devanagari is not a translation under the Latin. It is the other half of the name. The system uses both scripts with equal intent, but not at the same point size."
            />

            <div className="mt-12 grid gap-6 lg:grid-cols-2">
              <div className="border border-stone/60 bg-paper p-6 md:p-10">
                <p className="eyebrow text-clay">Latin</p>
                <p className="mt-5 font-display text-6xl font-semibold tracking-[-0.045em] md:text-7xl">
                  Sāntvana
                </p>
                <p className="mt-4 text-sm leading-relaxed text-muted">
                  Macron on the first ā only. ASCII fallback: Santvana. Pronunciation:
                  SAAN-tvuh-naa. Do not set it in all caps or add tracking.
                </p>
              </div>
              <div className="border border-stone/60 bg-bone p-6 md:p-10">
                <p className="eyebrow text-clay">Devanagari</p>
                <p className="font-deva mt-5 text-6xl font-semibold leading-tight md:text-7xl">
                  सांत्वना
                </p>
                <p className="mt-4 text-sm leading-relaxed text-muted">
                  Anusvara. सान्त्वना is valid for search and legal text, but it is not
                  the logo. No macron. No letter-spacing. No Latin face.
                </p>
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
              <div className="border border-ink bg-ink p-6 text-paper md:p-10">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="eyebrow text-clay-light">Hindi tagline · concept</p>
                  <Badge variant="outline" className="border-paper/30 text-paper">Native review pending</Badge>
                </div>
                <p className="font-deva mt-6 text-4xl font-semibold leading-[1.35] md:text-5xl">
                  लंबे रास्ते के लिए बने।
                </p>
                <p className="mt-4 max-w-lg text-sm leading-relaxed text-sand">
                  “Made for the long road.” An alternative that leans into the name is
                  “घर लौटने तक साथ।” (“With you until you get home.”) Both are flagged
                  for a native Hindi copywriter before use. Do not set them as final.
                </p>
              </div>
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Language rules</p>
                <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted">
                  {[
                    "The logo is सांत्वना. The search/legal variant is सान्त्वना.",
                    "Latin display is Sāntvana. URL/handle/legal is Santvana.",
                    "Do not add a macron to Devanagari or remove it from Latin.",
                    "The Hindi tagline is not approved until native review.",
                    "The name is not cleared. No public use before the attorney opinion.",
                  ].map((rule) => (
                    <p key={rule} className="border-t border-stone/40 pt-3">{rule}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="graphic" className="section-space border-t border-stone/60 bg-bone">
          <div className="container-brand">
            <SectionHeader
              number="06"
              kicker="Graphic language"
              title="The line stops. The ground stays."
              intro="A rule that does not point. A tread field that is texture, not logo. A crop that keeps the ground in frame. No arrows, chevrons or route-marker puns — the arrow was dropped for a Class 25 collision."
            />

            <div className="mt-12 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">The Long Line</p>
                <div className="mt-8 rule-long text-ink" />
                <p className="mt-8 text-xs leading-relaxed text-muted">
                  4 px ink on paper, 4 px paper on ink. 1 px stone and 2 px ink for quieter
                  rules. Square ends. No arrowheads, no dotted route lines.
                </p>
              </div>
              <div className="relative overflow-hidden border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">The Tread Field</p>
                <div className="tread-field absolute inset-x-0 bottom-0 h-32" aria-hidden="true" />
                <p className="relative mt-8 text-xs leading-relaxed text-muted">
                  The symbol’s three bars, repeated. 8–12% tint. Never behind body text
                  without a flat scrim.
                </p>
              </div>
              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Ground Crop</p>
                <div className="relative mt-6 h-24 overflow-hidden border border-stone/60 bg-sand">
                  <div className="absolute inset-x-0 bottom-0 h-10 bg-ground" />
                  <div className="absolute bottom-10 left-1/2 h-8 w-20 -translate-x-1/2 border border-ink bg-bone" />
                  <div className="absolute inset-3 border border-clay" />
                </div>
                <p className="mt-8 text-xs leading-relaxed text-muted">
                  Ground always in frame. The shoe is worn, not floating. Crop to the
                  ankle, sole and surface, not the face.
                </p>
              </div>
              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Mile Marks</p>
                <div className="mt-8 flex items-baseline gap-3">
                  <span className="font-display text-4xl font-semibold tracking-tight">01</span>
                  <span className="h-px flex-1 bg-ink" />
                </div>
                <div className="mt-3 flex items-baseline gap-3">
                  <span className="font-display text-4xl font-semibold tracking-tight">02</span>
                  <span className="h-px flex-1 bg-ink" />
                </div>
                <p className="mt-8 text-xs leading-relaxed text-muted">
                  Section numbers, not fake wayfinding. No dotted paths or journey
                  infographics.
                </p>
              </div>
            </div>

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <MiniBoard
                tone="paper"
                headline="Made for the long way home."
                body="Fit first. Free size exchange twice. 30-day returns from delivery."
                logo="/brand/logos/santvana-horizontal.svg"
                ratio="1:1"
                aspect="1 / 1"
              />
              <MiniBoard
                tone="dark"
                headline="Fit first."
                body="Free size exchange twice. 30-day returns from delivery."
                logo="/brand/logos/santvana-horizontal-reverse.svg"
                ratio="4:5"
                aspect="4 / 5"
              />
              <MiniBoard
                tone="paper"
                headline="Comfort, earned."
                body="Sneakers, runners, everyday, sandals, boots. Two drops a year."
                logo="/brand/logos/santvana-stacked.svg"
                logoWidth={600}
                logoHeight={420}
                ratio="9:16"
                aspect="9 / 16"
              />
            </div>
            <p className="mt-4 text-xs leading-relaxed text-muted">
              Scaled previews. Fixed-size concept boards:{" "}
              <a href="/brand/social/social-1x1.html" className="link-underline">
                1080 × 1080
              </a>
              ,{" "}
              <a href="/brand/social/social-4x5.html" className="link-underline">
                1080 × 1350
              </a>{" "}
              and{" "}
              <a href="/brand/social/social-9x16.html" className="link-underline">
                1080 × 1920
              </a>
              . Source files stay in <span className="mono-token">brand/phase-2/social/</span>.
              Export only after the name is cleared.
            </p>
          </div>
        </section>

        <section id="imagery" className="section-space border-t border-stone/60">
          <div className="container-brand">
            <SectionHeader
              number="07"
              kicker="Imagery"
              title="The ground is the hero."
              intro="Overcast light, concrete, tile, asphalt, paver blocks, wet edges, dust in the seams. The shoe is worn, not floating. The person is mid-day, not mid-yoga. No lotus, no hands in prayer, no candles, no pastel backdrops."
            />

            <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {[
                ["01", "Hero pair, 45°", "Both shoes on the ground, natural light, 4:5."],
                ["02", "Sole tread macro", "The three-bar geometry, raking light, 1:1."],
                ["03", "On-foot walking", "Mid-stride, ground visible, low three-quarter, 4:5."],
                ["04", "Wet pavement step", "One foot on wet concrete. No grip claim in the caption.", "dark"],
                ["05", "Stair descent", "Heel counter and flex, low angle, 4:5."],
                ["06", "Seated lace-tying", "Hands only, no face required, 1:1.", "ground"],
              ].map(([n, title, body, tone]) => (
                <div
                  key={n}
                  className={cn(
                    "relative flex aspect-[4/5] flex-col justify-between overflow-hidden border border-stone/60 p-5",
                    tone === "dark" ? "bg-ink text-paper" : tone === "ground" ? "bg-ground text-paper" : "bg-paper text-ink",
                  )}
                >
                  <div className={cn("absolute inset-0 opacity-60", tone ? "tread-field-dark" : "tread-field")} aria-hidden="true" />
                  <div className="relative flex items-center justify-between">
                    <span className={cn("eyebrow", tone ? "text-clay-light" : "text-clay")}>{n}</span>
                    <span className={cn("font-mono text-[0.625rem]", tone ? "text-paper/60" : "text-muted")}>4:5</span>
                  </div>
                  <div className="relative">
                    <p className="font-display text-2xl font-semibold leading-tight tracking-tight">{title}</p>
                    <p className={cn("mt-2 text-xs leading-relaxed", tone ? "text-sand" : "text-muted")}>{body}</p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 grid gap-8 lg:grid-cols-2">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Do</p>
                <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted">
                  {[
                    "Show the shoe on the ground it is built for.",
                    "Use overcast, ordinary light.",
                    "Show real wear and real feet.",
                    "Crop at the ankle and the sole.",
                    "Caption only what is evidenced.",
                  ].map((item) => (
                    <p key={item} className="border-t border-stone/40 pt-3">{item}</p>
                  ))}
                </div>
              </div>
              <div className="border border-ink bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Do not</p>
                <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted">
                  {[
                    "Float the shoe on a pastel sweep.",
                    "Use a spa, a candle, a lotus or a linen altar.",
                    "Smooth the skin, slim the foot or whiten the sole.",
                    "Claim slip-proof, vegan, recycled or sustainable without a certificate.",
                    "Use a gradient scrim or a soft glow behind type.",
                  ].map((item) => (
                    <p key={item} className="border-t border-stone/40 pt-3">{item}</p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </section>

        <section id="packaging" className="section-space border-t border-stone/60 bg-bone">
          <div className="container-brand">
            <SectionHeader
              number="08"
              kicker="Packaging"
              title="A quiet object. One true sentence."
              intro="Paper, ink, one clay rule. No foil, no laminate, no soft-touch, no plastic sleeve. The box should feel like something you keep for storage, not something you tear through."
            />

            <div className="mt-12 grid gap-8 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
              <div className="relative border border-stone/60 bg-paper p-6 md:p-10">
                <p className="eyebrow text-clay">Scale model · not to scale</p>
                <div className="relative mx-auto mt-10 h-72 w-full max-w-[360px]">
                  <div className="absolute left-0 top-8 h-56 w-[78%] border border-ink bg-bone p-6">
                    <img
                      src="/brand/logos/santvana-symbol.svg"
                      width={64}
                      height={64}
                      alt="Sāntvana ground mark"
                      className="h-12 w-12"
                    />
                    <p className="mt-8 font-display text-2xl font-semibold tracking-tight">Sāntvana</p>
                    <p className="mt-1 text-[0.625rem] uppercase tracking-[0.14em] text-muted">Made for the long way home.</p>
                    <div className="mt-5 h-1 w-20 bg-clay" />
                  </div>
                  <div className="absolute right-0 top-0 h-56 w-[22%] border border-ink bg-sand" />
                  <div className="absolute right-0 top-0 h-8 w-[22%] border border-ink bg-bone" />
                  <p className="absolute bottom-0 left-0 text-[0.625rem] leading-relaxed text-muted">
                    Front: stacked lockup at 72 mm in production. The symbol is shown
                    here so the scale model does not set the Devanagari below its floor.
                  </p>
                </div>
              </div>

              <div className="overflow-x-auto border border-stone/60 bg-paper">
                <table className="w-full min-w-[560px] border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-stone/60 text-[0.625rem] uppercase tracking-[0.1em] text-muted">
                      <th className="p-4 font-semibold" scope="col">Item</th>
                      <th className="p-4 font-semibold" scope="col">Size</th>
                      <th className="p-4 font-semibold" scope="col">Spec</th>
                    </tr>
                  </thead>
                  <tbody>
                    {packagingSpecs.map(([item, size, spec]) => (
                      <tr key={item} className="border-b border-stone/30 last:border-b-0">
                        <td className="p-4 font-medium">{item}</td>
                        <td className="p-4 font-mono text-xs">{size}</td>
                        <td className="p-4 text-muted">{spec}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            <div className="mt-8 grid gap-6 lg:grid-cols-2">
              <div className="border border-ink bg-ink p-6 text-paper md:p-8">
                <p className="eyebrow text-clay-light">Inside the box</p>
                <p className="mt-5 font-display text-3xl font-semibold leading-[1.02] tracking-[-0.035em]">
                  Sāntvana
                  <br />
                  Made for the long way home.
                </p>
                <p className="mt-5 max-w-md text-sm leading-relaxed text-sand">
                  Fit first. Free size exchange twice. 30-day returns from delivery.
                  Care: clean with a soft brush and mild soap. Air-dry away from direct
                  heat.
                </p>
                <p className="mt-5 text-xs text-paper/60">
                  No welcome essay. No playlist QR. No “tag us” demand.
                </p>
              </div>
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Legal panel · before print</p>
                <div className="mt-4 space-y-2 text-sm leading-relaxed text-muted">
                  {[
                    "Legal entity and registered address.",
                    "Manufacturing location and country of origin.",
                    "MRP in INR, inclusive of all taxes.",
                    "GST/HSN, batch, date of manufacture.",
                    "Customer care and grievance officer.",
                    "Return and exchange policy summary.",
                  ].map((item) => (
                    <p key={item} className="border-t border-stone/40 pt-2">{item}</p>
                  ))}
                </div>
                <p className="mt-4 text-xs font-medium text-clay">
                  No legal panel, no print. No placeholder text on a physical box.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="collateral" className="section-space border-t border-stone/60">
          <div className="container-brand">
            <SectionHeader
              number="09"
              kicker="Collateral"
              title="Functional, not decorative."
              intro="Business card, care card, size guide, shipping label and email. Every piece uses the same grid and type scale. Nothing carries a domain or QR until the domain is owned and the destination is live."
            />

            <div className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Business card</p>
                <div className="mt-6 flex aspect-[85/55] flex-col justify-between border border-stone/60 bg-bone p-4">
                  <div className="flex flex-col items-center gap-2">
                    <img
                      src="/brand/logos/santvana-symbol.svg"
                      width={64}
                      height={64}
                      alt="Sāntvana ground mark"
                      className="h-5 w-5"
                    />
                    <img
                      src="/brand/logos/santvana-wordmark-latin.svg"
                      width={376}
                      height={149}
                      alt="Sāntvana Latin wordmark"
                      className="w-12"
                    />
                  </div>
                  <div>
                    <p className="text-[0.625rem] font-medium">Name · Role</p>
                    <p className="text-[0.5625rem] text-muted">Phone · Email</p>
                  </div>
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">85 × 55 mm · 400 gsm uncoated · Ink + Clay.</p>
              </div>

              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Care card</p>
                <div className="mt-6 flex aspect-[90/150] flex-col justify-between border border-stone/60 bg-paper p-4">
                  <img
                    src="/brand/logos/santvana-stacked.svg"
                    width={600}
                    height={420}
                    alt="Sāntvana stacked lockup"
                    className="w-16"
                  />
                  <div>
                    <p className="text-[0.625rem] font-medium">Fit first.</p>
                    <p className="text-[0.5625rem] leading-relaxed text-muted">Free size exchange twice. 30-day returns.</p>
                  </div>
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">90 × 150 mm · 300 gsm uncoated · Ink + Clay.</p>
              </div>

              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Size guide</p>
                <div className="mt-6 flex aspect-[105/148] flex-col justify-between border border-stone/60 bg-bone p-4">
                  <p className="font-display text-lg font-semibold tracking-tight">Size guide</p>
                  <div className="space-y-1 text-[0.5625rem] text-muted">
                    <p>UK 6 · 24.0 cm</p>
                    <p>UK 7 · 25.0 cm</p>
                    <p>UK 8 · 26.0 cm</p>
                    <p>UK 9 · 27.0 cm</p>
                  </div>
                  <p className="text-[0.5625rem] text-muted">Between sizes? Take the half size up.</p>
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">105 × 148 mm · 120 gsm uncoated · Ink only.</p>
              </div>

              <div className="border border-stone/60 bg-paper p-5">
                <p className="eyebrow text-clay">Email</p>
                <div className="mt-6 border border-stone/60 bg-bone p-4">
                  <img
                    src="/brand/logos/santvana-horizontal.svg"
                    width={686}
                    height={320}
                    alt="Sāntvana horizontal lockup"
                    className="w-32"
                  />
                  <p className="mt-5 text-[0.625rem] font-medium">Order A-10428 is confirmed.</p>
                  <p className="mt-1 text-[0.5625rem] leading-relaxed text-muted">Packing today. Out the door tomorrow.</p>
                  <div className="mt-4 inline-block bg-clay px-3 py-1.5 text-[0.5625rem] text-paper">View order</div>
                </div>
                <p className="mt-4 text-xs leading-relaxed text-muted">600 px · horizontal lockup 300 px · Inter 16 px / 1.6.</p>
              </div>
            </div>

            <div className="mt-8 grid gap-4 md:grid-cols-3">
              {[
                ["No domain printed", "No URL, handle or QR until the domain is owned and the destination is live."],
                ["No placeholder legal", "The Phase 3 master data supplies entity, MRP, GST/HSN and country of origin."],
                ["No material claim", "No “recycled”, “sustainable”, “vegan” or “plastic-free” copy without a certificate."],
              ].map(([title, body]) => (
                <div key={title} className="border-t border-ink pt-4">
                  <p className="font-display text-lg font-semibold tracking-tight">{title}</p>
                  <p className="mt-2 text-sm leading-relaxed text-muted">{body}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        <section id="tokens" className="section-space border-t border-stone/60 bg-bone">
          <div className="container-brand">
            <SectionHeader
              number="10"
              kicker="Tokens"
              title="The system, in values."
              intro="Colour, type, space, radius, motion and logo rules in one place. The /brand route and the static tokens file use the same values. The contrast ratios are calculated from the hex values, not typed by hand."
            />

            <div className="mt-12 grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Token groups</p>
                <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted">
                  {[
                    ["Colour", "16 core values, semantic roles, status colours."],
                    ["Type", "Archivo, Inter, Noto Sans Devanagari; weights, tracking, optical factors."],
                    ["Space", "4 px base; 4–128 px scale; 20 px mobile gutter, 40 px desktop."],
                    ["Radius", "0, 4, 8, 12 px; 16 px symbol; pill reserved for tags."],
                    ["Motion", "120 ms state, 220 ms panel; cubic-bezier(0.2, 0.7, 0.2, 1)."],
                    ["Logo", "20 px floor, 28 px conservative 1×, 6 mm print, clear space 1× cap height."],
                  ].map(([title, body]) => (
                    <div key={title} className="border-t border-stone/40 pt-3">
                      <p className="font-medium text-ink">{title}</p>
                      <p className="mt-1 text-xs leading-relaxed text-muted">{body}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border border-ink bg-ink p-6 text-paper md:p-8">
                <div className="flex flex-wrap items-center justify-between gap-3">
                  <p className="eyebrow text-clay-light">CSS variables</p>
                  <a
                    href="/brand/tokens.json"
                    className="text-xs text-clay-light underline underline-offset-4 hover:text-paper"
                  >
                    tokens.json
                  </a>
                </div>
                <pre className="mono-token mt-5 overflow-x-auto whitespace-pre-wrap text-[0.6875rem] leading-relaxed text-sand">
{`:root {
  --color-ink: #171614;
  --color-paper: #F5F1E8;
  --color-ground: #2B2722;
  --color-bone: #EAE3D6;
  --color-sand: #D9CBB4;
  --color-stone: #8C8578;
  --color-muted: #6B655B;
  --color-clay: #A8452B;
  --color-clay-light: #D98B6F;
  --color-moss: #3E4A3A;
  --color-moss-light: #A8B5A0;
  --color-slate: #35424C;
  --color-ochre: #946200;
  --color-red: #A62B22;
  --color-green: #2F6B4F;
  --color-blue: #2E5E7E;

  --font-display: var(--font-archivo);
  --font-body: var(--font-inter);
  --font-deva: var(--font-noto-deva);

  --logo-devanagari-floor: 20px;
  --logo-devanagari-practical-1x: 28px;
  --logo-devanagari-print-floor: 6mm;
}`}
                </pre>
                <p className="mt-4 text-xs leading-relaxed text-paper/60">
                  Full token set: <span className="mono-token">brand/phase-2/tokens.json</span>{" "}
                  and <span className="mono-token">tokens.css</span>. The route mirrors
                  them in <span className="mono-token">app/globals.css</span>.
                </p>
              </div>
            </div>
          </div>
        </section>

        <section id="approval" className="section-space border-t border-stone/60">
          <div className="container-brand">
            <SectionHeader
              number="11"
              kicker="Approval"
              title="What is open. What is blocked."
              intro="Phase 2 is complete as a concept. It is not approved for production. The open items below are deliberate; none of them blocks further concept work, and all of them block print, domain or ad spend."
            />

            <div className="mt-12 grid gap-4">
              {openItems.map((item) => (
                <div key={item.n} className="grid gap-4 border-t border-ink pt-4 md:grid-cols-[4rem_1fr_auto] md:items-start md:gap-8">
                  <p className="font-mono text-xs text-clay">{item.n}</p>
                  <div>
                    <p className="font-display text-xl font-semibold tracking-tight">{item.title}</p>
                    <p className="mt-2 max-w-2xl text-sm leading-relaxed text-muted">{item.body}</p>
                  </div>
                  <Badge variant="outline" className="justify-self-start whitespace-nowrap md:justify-self-end">
                    {item.status}
                  </Badge>
                </div>
              ))}
            </div>

            <div className="mt-10 grid gap-6 lg:grid-cols-2">
              <div className="border border-stone/60 bg-paper p-6 md:p-8">
                <p className="eyebrow text-clay">Approval checklist</p>
                <div className="mt-4 space-y-3 text-sm leading-relaxed">
                  {[
                    ["Phase 1 v1.1 approved", true, "30 October 2026"],
                    ["Logo form सांत्वना selected", true, "30 October 2026"],
                    ["Final-face legibility re-run", true, "Noto Sans Devanagari 600"],
                    ["Small-size rule accepted", false, "20 px floor / monogram below"],
                    ["Phase 2 visual system approved", false, "This document"],
                    ["Attorney opinion", false, "Blocks print, domain, ad spend"],
                    ["Native-speaker connotation test", false, "Founder-run"],
                    ["6 mm measured print proof", false, "Physical stock"],
                  ].map(([label, done, note]) => (
                    <div key={String(label)} className="flex items-start gap-3 border-t border-stone/40 pt-3">
                      <span
                        aria-hidden="true"
                        className={cn("mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center border text-[0.625rem]", done ? "border-green bg-green text-paper" : "border-stone text-transparent")}
                      >
                        ✓
                      </span>
                      <span className="sr-only">{done ? "Done:" : "Pending:"}</span>
                      <span className="min-w-0 flex-1">
                        <span className="block font-medium">{label}</span>
                        <span className="block text-xs text-muted">{note}</span>
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border border-ink bg-ink p-6 text-paper md:p-8">
                <p className="eyebrow text-clay-light">Stop rule</p>
                <p className="mt-5 font-display text-3xl font-semibold leading-[1.02] tracking-[-0.035em]">
                  Concept work may continue. Production spend may not.
                </p>
                <p className="mt-5 max-w-md text-sm leading-relaxed text-sand">
                  No print, domain purchase, ad spend, co-branding or public launch
                  until the attorney opinion is back and the native-speaker test is
                  complete. If either fails, stop and re-cut the name before further
                  spend.
                </p>
                <div className="mt-8 border-t border-paper/20 pt-4">
                  <p className="font-deva text-2xl leading-relaxed">सांत्वना</p>
                  <p className="mt-1 text-xs text-paper/60">Sāntvana · Phase 2 · 30 October 2026</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="border-t border-paper/20 bg-ink text-paper">
        <div className="container-brand grid gap-8 py-12 md:grid-cols-[1fr_auto] md:items-end">
          <div>
            <img
              src="/brand/logos/santvana-horizontal-reverse.svg"
              width={686}
              height={320}
              alt="Sāntvana horizontal bilingual lockup, reverse"
              className="w-full max-w-[300px]"
            />
            <p className="mt-6 max-w-md text-sm leading-relaxed text-sand">
              Made for the long way home. Fit first. Comfort, earned.
            </p>
            <p className="mt-4 max-w-md text-xs leading-relaxed text-paper/60">
              Concept only. No print, domain or ad spend until the attorney opinion
              in <span className="mono-token">brand/naming.md §6</span>. The name is
              not cleared.
            </p>
          </div>
          <div className="flex flex-wrap gap-5 text-xs text-paper/60 md:justify-end">
            {nav.map((item) => (
              <a key={item.href} href={item.href} className="hover:text-paper">
                {item.label}
              </a>
            ))}
            <a href="#top" className="hover:text-paper">
              Top
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
}
