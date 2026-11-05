import Link from "next/link";

export default function NotFound() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-2xl px-5 py-20 sm:px-8">
        <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
          Not found
        </p>
        <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em]">
          This page does not exist.
        </h1>
        <p className="mt-4 font-body leading-7 text-muted">
          The link may be old, or the order reference may be wrong. Order links
          are private capability links and are not listed anywhere.
        </p>
        <Link
          href="/catalogue"
          className="mt-8 inline-block rounded-full bg-ink px-6 py-3 font-body text-sm text-paper transition-colors hover:bg-ground"
        >
          Return to the catalogue
        </Link>
      </div>
    </main>
  );
}
