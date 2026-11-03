import Link from "next/link";

import { CheckoutForm } from "@/components/CheckoutForm";

export const dynamic = "force-dynamic";

export const metadata = {
  title: "Checkout — Sāntvana (concept)",
  description:
    "Guest checkout for the Sāntvana concept storefront. Payment runs through Razorpay hosted checkout and is confirmed by a signed webhook.",
  robots: { index: false, follow: false },
};

export default function CheckoutPage() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-5xl px-5 py-10 sm:px-8 lg:py-16">
        <header className="border-b border-black/10 pb-8">
          <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
            Phase 4 · Milestone 3
          </p>
          <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em] sm:text-5xl">
            Checkout
          </h1>
          <p className="mt-4 max-w-2xl font-body text-base leading-7 text-muted">
            Guest checkout. Your size is reserved for a short window while you
            pay. Prices and GST are calculated on the server from the catalogue,
            never from the browser.
          </p>
          <nav className="mt-5 flex flex-wrap gap-4 font-body text-sm">
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/"
            >
              Home
            </Link>
            <Link
              className="underline decoration-black/20 underline-offset-4"
              href="/catalogue"
            >
              Catalogue
            </Link>
          </nav>
        </header>

        <CheckoutForm />

        <footer className="mt-12 border-t border-black/10 pt-6 font-body text-xs leading-5 text-muted">
          <p>
            Concept store. Shipping, returns and exchanges are not enabled in
            this milestone. No card data is stored by the store.
          </p>
        </footer>
      </div>
    </main>
  );
}
