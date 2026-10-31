import Link from "next/link";

import { getCatalogue, safeText } from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Catalogue — Sāntvana (concept)",
  description:
    "Concept catalogue for Sāntvana. Published products only; draft products and open fields are never shown.",
  robots: { index: false, follow: false },
};

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

function colour(value: string): string {
  return /^#[0-9a-f]{6}$/i.test(value) ? value : "#D9CBB4";
}

export default async function CataloguePage() {
  const products = await getCatalogue();

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-6xl px-5 py-10 sm:px-8 lg:py-16">
        <header className="flex flex-wrap items-end justify-between gap-6 border-b border-black/10 pb-8">
          <div>
            <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
              Phase 4 · Milestone 1
            </p>
            <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">
              Catalogue
            </h1>
            <p className="mt-4 max-w-2xl font-body text-base leading-7 text-muted">
              Published products only. Draft products are never shown, and open
              fields are not rendered.
            </p>
          </div>
          <nav className="flex gap-4 font-body text-sm">
            <Link className="underline decoration-black/20 underline-offset-4" href="/">
              Home
            </Link>
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/brand"
            >
              Brand system
            </Link>
          </nav>
        </header>

        {products.length === 0 ? (
          <section className="mt-12 max-w-2xl rounded-lg border border-black/10 bg-white/60 p-8">
            <h2 className="font-display text-2xl font-semibold">
              No products are published yet
            </h2>
            <p className="mt-4 font-body leading-7 text-muted">
              The Phase 3 catalogue is loaded as draft while manufacturer, tax,
              legal and launch-stock fields remain open. A product becomes
              visible only after every open field is resolved and the publish
              guard passes.
            </p>
          </section>
        ) : (
          <ul className="mt-12 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {products.map((product) => {
              const name = safeText(product.name) ?? "Product";
              const summary = safeText(product.summary);
              const category = safeText(product.category) ?? "Catalogue";
              const subCategory = safeText(product.sub_category);
              const tierLabel = safeText(product.tier_label);
              const colourName = safeText(product.colour) ?? "Colour";

              return (
                <li
                  key={product.id}
                  className="overflow-hidden rounded-lg border border-black/10 bg-white/70"
                >
                  <div
                    className="aspect-[4/5] w-full"
                    style={{ backgroundColor: colour(product.colour_hex) }}
                    aria-label={`${colourName} colour swatch`}
                  />
                  <div className="space-y-3 p-5">
                    <div className="flex items-center justify-between gap-3">
                      <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
                        {category}
                        {subCategory ? ` · ${subCategory}` : ""}
                      </p>
                      {product.hero ? (
                        <span className="rounded-full border border-black/15 px-2 py-1 font-body text-[0.7rem] uppercase tracking-[0.1em]">
                          Hero
                        </span>
                      ) : null}
                    </div>
                    <div>
                      <h2 className="font-display text-xl font-semibold">{name}</h2>
                      <p className="mt-1 font-body text-sm text-muted">
                        {colourName}
                        {tierLabel ? ` · ${tierLabel}` : ""}
                      </p>
                    </div>
                    {summary ? (
                      <p className="font-body text-sm leading-6 text-muted">{summary}</p>
                    ) : null}
                    <div className="flex items-end justify-between gap-3 pt-1">
                      <p className="font-display text-lg font-semibold">
                        {inr.format(product.price_inr)}
                      </p>
                      <p className="font-body text-xs text-muted">Incl. GST</p>
                    </div>
                  </div>
                </li>
              );
            })}
          </ul>
        )}

        <footer className="mt-16 border-t border-black/10 pt-6 font-body text-xs leading-6 text-muted">
          Concept only. No print, domain or ad spend until the attorney opinion
          and native-speaker test are back. The name is not cleared.
        </footer>
      </div>
    </main>
  );
}
