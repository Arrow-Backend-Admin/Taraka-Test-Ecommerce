"use client";

import Link from "next/link";
import { useEffect } from "react";

export default function Error({
  error,
  retry,
}: {
  error: unknown;
  retry: () => void;
}) {
  useEffect(() => {
    // Keep the detail in the browser console only. The production UI never
    // renders an exception message to a customer.
    console.error(error);
  }, [error]);

  return (
    <main className="min-h-screen bg-paper text-ink">
      <div className="mx-auto w-full max-w-2xl px-5 py-20 sm:px-8">
        <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
          Something went wrong
        </p>
        <h1 className="mt-3 font-display text-4xl font-semibold tracking-[-0.035em]">
          This page could not load.
        </h1>
        <p className="mt-4 font-body leading-7 text-muted">
          The store hit an unexpected problem. No payment is taken by this
          screen. Try again, or return to the catalogue and start from a fresh
          reservation.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <button
            type="button"
            onClick={() => retry()}
            className="rounded-full bg-ink px-6 py-3 font-body text-sm text-paper transition-colors hover:bg-ground"
          >
            Try again
          </button>
          <Link
            href="/catalogue"
            className="rounded-full border border-black/15 px-6 py-3 font-body text-sm transition-colors hover:bg-white/60"
          >
            Return to the catalogue
          </Link>
        </div>
      </div>
    </main>
  );
}
