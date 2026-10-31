import Link from "next/link";

export const metadata = {
  title: "Sāntvana — concept storefront",
  description:
    "Phase 4 Milestone 1 concept storefront. Catalogue publishing is gated until open product fields are resolved.",
  robots: { index: false, follow: false },
};

export default function HomePage() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-between px-5 py-10 sm:px-8 lg:py-16">
        <header className="flex items-center justify-between gap-6">
          <p className="font-display text-lg font-semibold tracking-[-0.02em]">
            Sāntvana
          </p>
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Concept · not for launch
          </p>
        </header>

        <section className="max-w-3xl py-20">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Phase 4 · Milestone 1
          </p>
          <h1 className="mt-5 font-display text-5xl font-semibold leading-[0.95] tracking-[-0.045em] sm:text-7xl">
            A catalogue that
            <br />
            refuses to guess.
          </h1>
          <p className="mt-8 max-w-xl font-body text-lg leading-8 text-muted">
            The storefront shows published products only. Product facts stay
            hidden until the manufacturer, tax and legal fields are resolved.
          </p>
          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              className="rounded-full bg-ink px-6 py-3 font-body text-sm text-paper transition-colors hover:bg-ground"
              href="/catalogue"
            >
              View catalogue
            </Link>
            <Link
              className="rounded-full border border-black/15 px-6 py-3 font-body text-sm transition-colors hover:bg-white/60"
              href="/brand"
            >
              Brand system
            </Link>
          </div>
        </section>

        <footer className="border-t border-black/10 pt-6 font-body text-xs leading-6 text-muted">
          No print, domain or ad spend until the attorney opinion and
          native-speaker test are back. The name is not cleared.
        </footer>
      </div>
    </main>
  );
}
