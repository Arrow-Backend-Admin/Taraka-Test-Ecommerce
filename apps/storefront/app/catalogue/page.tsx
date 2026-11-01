import Link from "next/link";

import { PlaceholderImage } from "@/components/PlaceholderImage";
import {
  getCatalogue,
  previewDraftsEnabled,
  safeText,
} from "@/lib/api";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Catalogue — Sāntvana (concept)",
  description:
    "Concept catalogue for Sāntvana. Published products only; draft products and open fields are never shown unless the development preview is enabled.",
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
  const previewDrafts = previewDraftsEnabled();
  const products = await getCatalogue({ previewDrafts });

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
              {previewDrafts
                ? "Development draft preview. Draft products are visible, unresolved fields read “To be confirmed”, and every placeholder is labelled."
                : "Published products only. Draft products are never shown, and open fields are not rendered."}
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

        {previewDrafts ? (
          <div className="mt-8 rounded-lg border border-[#b9892f]/40 bg-[#fff4d6] p-5 font-body text-sm leading-6 text-[#5c4317]">
            <strong className="font-semibold">Draft preview, not production.</strong>{" "}
            This mode is development-only and is ignored when{" "}
            <code className="rounded bg-black/5 px-1 py-0.5">APP_ENV=production</code>.
            Placeholder images are not product photography and must never be used
            in ads, social posts or packaging.
          </div>
        ) : null}

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
              const image = product.images?.[0];

              return (
                <li
                  key={product.id}
                  className="overflow-hidden rounded-lg border border-black/10 bg-white/70"
                >
                  <Link
                    className="group block focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-4 focus-visible:outline-ink"
                    href={`/catalogue/${encodeURIComponent(product.slug)}`}
                  >
                    {image ? (
                      <PlaceholderImage
                        image={image}
                        sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                      />
                    ) : (
                      <div
                        className="aspect-[4/5] w-full"
                        style={{ backgroundColor: colour(product.colour_hex) }}
                        aria-label={`${colourName} colour swatch`}
                      />
                    )}
                    <div className="space-y-3 p-5">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
                          {category}
                          {subCategory ? ` · ${subCategory}` : ""}
                        </p>
                        <div className="flex gap-2">
                          {product.preview ? (
                            <span className="rounded-full border border-[#b9892f]/50 bg-[#fff4d6] px-2 py-1 font-body text-[0.65rem] uppercase tracking-[0.1em] text-[#5c4317]">
                              Draft
                            </span>
                          ) : null}
                          {product.hero ? (
                            <span className="rounded-full border border-black/15 px-2 py-1 font-body text-[0.7rem] uppercase tracking-[0.1em]">
                              Hero
                            </span>
                          ) : null}
                        </div>
                      </div>
                      <div>
                        <h2 className="font-display text-xl font-semibold">
                          {name}
                        </h2>
                        <p className="mt-1 font-body text-sm text-muted">
                          {colourName}
                          {tierLabel ? ` · ${tierLabel}` : ""}
                        </p>
                      </div>
                      {summary ? (
                        <p className="font-body text-sm leading-6 text-muted">
                          {summary}
                        </p>
                      ) : null}
                      <div className="flex items-end justify-between gap-3 pt-1">
                        <p className="font-display text-lg font-semibold">
                          {inr.format(product.price_inr)}
                        </p>
                        <p className="font-body text-xs text-muted">Incl. GST</p>
                      </div>
                      <p className="font-body text-xs text-muted underline decoration-black/20 underline-offset-4">
                        View product
                      </p>
                    </div>
                  </Link>
                </li>
              );
            })}
          </ul>
        )}

        <footer className="mt-16 border-t border-black/10 pt-6 font-body text-xs leading-6 text-muted">
          Concept only. No print, domain or ad spend until the attorney opinion
          and native-speaker test are back. The name is not cleared. Placeholder
          photography is not for ads, social posts or packaging.
        </footer>
      </div>
    </main>
  );
}
