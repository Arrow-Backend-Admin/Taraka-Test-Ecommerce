import Link from "next/link";
import { notFound } from "next/navigation";

import { PlaceholderImage } from "@/components/PlaceholderImage";
import { ProductPurchase } from "@/components/ProductPurchase";
import { getProduct, previewDraftsEnabled, safeText } from "@/lib/api";

export const dynamic = "force-dynamic";

const inr = new Intl.NumberFormat("en-IN", {
  style: "currency",
  currency: "INR",
  maximumFractionDigits: 0,
});

const MATERIAL_LABELS: Record<string, string> = {
  upper: "Upper",
  lining: "Lining",
  insole: "Insole",
  midsole: "Midsole",
  outsole: "Outsole",
};

export default async function ProductPage({
  params,
}: {
  params: Promise<{ slug: string }>;
}) {
  const { slug } = await params;
  const previewDrafts = previewDraftsEnabled();
  const product = await getProduct(slug, { previewDrafts });

  if (!product) notFound();

  const name = safeText(product.name) ?? "Product";
  const category = safeText(product.category) ?? "Catalogue";
  const subCategory = safeText(product.sub_category);
  const colourName = safeText(product.colour) ?? "Colour";
  const summary = safeText(product.summary);
  const description = safeText(product.description);
  const materials = Object.entries(product.materials ?? {});
  const sizes = product.sizes ?? [];
  const features = product.features ?? [];
  const images = product.images ?? [];
  const photoCredits = images.filter(
    (image) => image.kind === "photo" && image.photographer,
  );

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-6xl px-5 py-10 sm:px-8 lg:py-16">
        <nav className="flex flex-wrap gap-4 font-body text-sm">
          <Link
            className="underline decoration-black/20 underline-offset-4"
            href="/catalogue"
          >
            Catalogue
          </Link>
          <Link
            className="underline decoration-black/20 underline-offset-4"
            href="/"
          >
            Home
          </Link>
        </nav>

        {previewDrafts ? (
          <div className="mt-8 rounded-lg border border-[#b9892f]/40 bg-[#fff4d6] p-5 font-body text-sm leading-6 text-[#5c4317]">
            <strong className="font-semibold">Draft preview, not production.</strong>{" "}
            Unresolved fields read “To be confirmed”. Placeholder images are not
            product photography and must never be used in ads, social posts or
            packaging.
          </div>
        ) : null}

        <header className="mt-8 border-b border-black/10 pb-8">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            {category}
            {subCategory ? ` · ${subCategory}` : ""}
          </p>
          <div className="mt-3 flex flex-wrap items-end justify-between gap-6">
            <div>
              <h1 className="font-display text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">
                {name}
              </h1>
              <p className="mt-3 font-body text-base text-muted">
                {colourName}
              </p>
            </div>
            <p className="font-display text-2xl font-semibold">
              {inr.format(product.price_inr)}
            </p>
          </div>
          {summary ? (
            <p className="mt-5 max-w-3xl font-body text-base leading-7 text-muted">
              {summary}
            </p>
          ) : null}
        </header>

        <section className="mt-10" aria-labelledby="product-images">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <h2
              className="font-display text-2xl font-semibold"
              id="product-images"
            >
              Images
            </h2>
            <p className="font-body text-xs text-muted">
              Six roles · 4:5 · placeholders and “Image coming” blocks
            </p>
          </div>
          {images.length === 0 ? (
            <p className="mt-4 rounded-lg border border-black/10 bg-white/60 p-5 font-body text-sm text-muted">
              No images are attached to this product.
            </p>
          ) : (
            <ul className="mt-5 grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
              {images.map((image) => (
                <li key={image.filename}>
                  <figure>
                    <PlaceholderImage
                      image={image}
                      sizes="(min-width: 1024px) 33vw, (min-width: 640px) 50vw, 100vw"
                    />
                    <figcaption className="mt-2 font-body text-xs leading-5 text-muted">
                      {image.role}
                      {image.kind === "image_coming"
                        ? " · Image coming"
                        : image.photographer
                          ? ` · Photo: ${image.photographer}`
                          : ""}
                      {image.is_placeholder
                        ? " · Placeholder image, not the actual product"
                        : ""}
                    </figcaption>
                  </figure>
                </li>
              ))}
            </ul>
          )}
        </section>

        <div className="mt-12 grid gap-10 lg:grid-cols-[1.3fr_0.7fr]">
          <div className="space-y-8">
            <section aria-labelledby="description">
              <h2
                className="font-display text-2xl font-semibold"
                id="description"
              >
                Description
              </h2>
              <p className="mt-3 font-body leading-7 text-muted">
                {description ?? "To be confirmed"}
              </p>
            </section>

            <section aria-labelledby="features">
              <h2 className="font-display text-2xl font-semibold" id="features">
                Features
              </h2>
              <ul className="mt-3 list-disc space-y-2 pl-5 font-body leading-7 text-muted">
                {features.length > 0 ? (
                  features.map((feature, index) => (
                    <li key={`${feature}-${index}`}>{feature}</li>
                  ))
                ) : (
                  <li>To be confirmed</li>
                )}
              </ul>
            </section>

            <section aria-labelledby="sizes">
              <h2 className="font-display text-2xl font-semibold" id="sizes">
                Sizes
              </h2>
              <ProductPurchase slug={product.slug} sizes={sizes} />
            </section>

            {photoCredits.length > 0 ? (
              <section aria-labelledby="image-credits">
                <h2
                  className="font-display text-2xl font-semibold"
                  id="image-credits"
                >
                  Image credits
                </h2>
                <p className="mt-2 font-body text-sm leading-6 text-muted">
                  These are placeholder photographs, not the actual product.
                  Every source is CC0 1.0 or CC BY 4.0, cropped and resized.
                </p>
                <ul className="mt-4 space-y-4 font-body text-sm leading-6">
                  {photoCredits.map((image) => (
                    <li
                      className="rounded-md border border-black/10 bg-white/60 p-4"
                      key={`${image.filename}-credit`}
                    >
                      <p className="font-medium">
                        {image.source_title ?? image.role}
                      </p>
                      <p className="text-muted">
                        Photographer: {image.photographer}
                      </p>
                      <p className="text-muted">
                        Licence:{" "}
                        {image.licence_url ? (
                          <a
                            className="underline decoration-black/20 underline-offset-4"
                            href={image.licence_url}
                            rel="license noopener noreferrer"
                            target="_blank"
                          >
                            {image.licence_name}
                          </a>
                        ) : (
                          image.licence_name
                        )}
                      </p>
                      <p className="text-muted">
                        Source:{" "}
                        {image.source_url ? (
                          <a
                            className="underline decoration-black/20 underline-offset-4"
                            href={image.source_url}
                            rel="noopener noreferrer"
                            target="_blank"
                          >
                            {image.source ?? "Wikimedia Commons"}
                          </a>
                        ) : (
                          image.source
                        )}
                      </p>
                      <p className="text-muted">
                        Changes: {image.changes ?? "Cropped and resized"}
                      </p>
                      {image.attribution ? (
                        <p className="mt-2 text-xs text-muted">
                          {image.attribution}
                        </p>
                      ) : null}
                    </li>
                  ))}
                </ul>
                <p className="mt-3 font-body text-xs leading-5 text-muted">
                  Full source list and visual QA notes:{" "}
                  <Link
                    className="underline decoration-black/20 underline-offset-4"
                    href="/credits"
                  >
                    image credits
                  </Link>
                  .
                </p>
              </section>
            ) : null}
          </div>

          <aside className="space-y-8">
            <section aria-labelledby="materials">
              <h2
                className="font-display text-2xl font-semibold"
                id="materials"
              >
                Materials
              </h2>
              <dl className="mt-3 space-y-3 font-body text-sm">
                {materials.length > 0 ? (
                  materials.map(([key, value]) => (
                    <div
                      className="flex justify-between gap-4 border-b border-black/5 pb-2"
                      key={key}
                    >
                      <dt className="text-muted">
                        {MATERIAL_LABELS[key] ?? key}
                      </dt>
                      <dd className="text-right">{value}</dd>
                    </div>
                  ))
                ) : (
                  <p className="text-muted">To be confirmed</p>
                )}
              </dl>
            </section>

            <section aria-labelledby="fit-care">
              <h2
                className="font-display text-2xl font-semibold"
                id="fit-care"
              >
                Fit and care
              </h2>
              <p className="mt-3 font-body text-sm leading-6 text-muted">
                <span className="text-ink">Fit: </span>
                {safeText(product.fit_notes) ?? "To be confirmed"}
              </p>
              <p className="mt-3 font-body text-sm leading-6 text-muted">
                <span className="text-ink">Care: </span>
                {safeText(product.care) ?? "To be confirmed"}
              </p>
            </section>
          </aside>
        </div>

        <footer className="mt-16 border-t border-black/10 pt-6 font-body text-xs leading-6 text-muted">
          <p>
            Concept only. Placeholder photography is not for ads, social posts or
            packaging. No print, domain or ad spend until the attorney opinion and
            native-speaker test are back.
          </p>
          <p className="mt-2">
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/credits"
            >
              Placeholder image credits and visual QA
            </Link>
          </p>
        </footer>
      </div>
    </main>
  );
}
