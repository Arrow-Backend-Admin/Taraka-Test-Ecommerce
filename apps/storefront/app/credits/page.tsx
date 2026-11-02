import Link from "next/link";

import creditsData from "./credits.json";

export const metadata = {
  title: "Placeholder image credits — Sāntvana (concept)",
  description:
    "Sources, licences, changes and visual QA for the concept storefront placeholder images.",
  robots: { index: false, follow: false },
};

export default function CreditsPage() {
  const sources = creditsData.sources;
  const grey = creditsData.grey;

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 lg:py-16">
        <nav className="flex flex-wrap gap-4 font-body text-sm">
          <Link className="underline decoration-black/20 underline-offset-4" href="/">
            Home
          </Link>
          <Link
            className="underline decoration-black/20 underline-offset-4"
            href="/catalogue"
          >
            Catalogue
          </Link>
          <Link
            className="underline decoration-black/20 underline-offset-4"
            href="/brand"
          >
            Brand system
          </Link>
        </nav>

        <header className="mt-8 border-b border-black/10 pb-8">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Phase 4 · Milestone 2
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">
            Placeholder image credits
          </h1>
          <p className="mt-4 max-w-3xl font-body text-base leading-7 text-muted">
            {creditsData.notice}. {creditsData.usage} This page records every
            source, licence, change and visual QA result for the concept
            storefront.
          </p>
          <p className="mt-3 font-body text-sm leading-6 text-muted">
            Generated {creditsData.generated_at}. {sources.length} reviewed
            photographs and {grey.length} neutral “Image coming” blocks.
          </p>
        </header>

        <section className="mt-10" aria-labelledby="policy">
          <h2 className="font-display text-2xl font-semibold" id="policy">
            Source policy
          </h2>
          <p className="mt-3 font-body leading-7 text-muted">
            {creditsData.source_policy}
          </p>
          <p className="mt-3 font-body text-sm leading-6 text-muted">
            Every photograph was centre-cropped to 4:5 and resized to 800×1000.
            Grey blocks are generated, not photographed. These images are
            temporary placeholders and must never be used in ads, social posts or
            packaging.
          </p>
        </section>

        <section className="mt-10" aria-labelledby="sources">
          <h2 className="font-display text-2xl font-semibold" id="sources">
            Reviewed photographs
          </h2>
          <ul className="mt-4 space-y-4">
            {sources.map((source) => (
              <li
                className="rounded-lg border border-black/10 bg-white/60 p-5 font-body text-sm leading-6"
                key={`${source.category}-${source.role}`}
              >
                <p className="font-medium">
                  {source.category} · {source.role}
                </p>
                <p className="text-muted">{source.source_title}</p>
                <p className="mt-2 text-muted">
                  Photographer: {source.photographer}
                </p>
                <p className="text-muted">
                  Licence:{" "}
                  <a
                    className="underline decoration-black/20 underline-offset-4"
                    href={source.licence_url}
                    rel="license noopener noreferrer"
                    target="_blank"
                  >
                    {source.licence_name}
                  </a>
                </p>
                <p className="text-muted">
                  Source:{" "}
                  <a
                    className="underline decoration-black/20 underline-offset-4"
                    href={source.source_url}
                    rel="noopener noreferrer"
                    target="_blank"
                  >
                    Wikimedia Commons
                  </a>
                </p>
                <p className="text-muted">Changes: {source.changes}</p>
                <p className="mt-2 text-xs text-muted">
                  Visual QA ({source.qa.method}): {source.qa.result} —{" "}
                  {source.qa.notes}
                </p>
              </li>
            ))}
          </ul>
        </section>

        <section className="mt-10" aria-labelledby="grey">
          <h2 className="font-display text-2xl font-semibold" id="grey">
            “Image coming” blocks
          </h2>
          <p className="mt-3 font-body text-sm leading-6 text-muted">
            No suitable unbranded, correctly angled source was available for
            these category and role combinations. A neutral grey 4:5 block is
            used instead of a mismatched photograph.
          </p>
          <div className="mt-4 overflow-x-auto">
            <table className="w-full border-collapse font-body text-sm">
              <thead>
                <tr className="border-b border-black/10 text-left">
                  <th className="py-2 pr-4 font-medium">Category</th>
                  <th className="py-2 pr-4 font-medium">Role</th>
                  <th className="py-2 font-medium">Reason</th>
                </tr>
              </thead>
              <tbody>
                {grey.map((slot) => (
                  <tr
                    className="border-b border-black/5 align-top"
                    key={`${slot.category}-${slot.role}`}
                  >
                    <td className="py-2 pr-4">{slot.category}</td>
                    <td className="py-2 pr-4">{slot.role}</td>
                    <td className="py-2 text-muted">{slot.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="mt-16 border-t border-black/10 pt-6 font-body text-xs leading-6 text-muted">
          <p>
            Concept only. No print, domain or ad spend until the attorney opinion
            and native-speaker test are back. The name is not cleared.
          </p>
          <p className="mt-2">
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/catalogue"
            >
              Back to catalogue
            </Link>
          </p>
        </footer>
      </div>
    </main>
  );
}
