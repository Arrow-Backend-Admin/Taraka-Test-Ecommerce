export default function Loading() {
  return (
    <main className="min-h-screen bg-paper text-ink" aria-busy="true">
      <div className="mx-auto w-full max-w-6xl px-5 py-10 sm:px-8 lg:py-16">
        <p className="font-body text-[0.75rem] uppercase tracking-[0.14em] text-muted">
          Loading
        </p>
        <div className="mt-4 h-10 w-2/3 max-w-md animate-pulse rounded bg-black/10" />
        <div className="mt-4 h-4 w-full max-w-xl animate-pulse rounded bg-black/10" />
        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2].map((item) => (
            <div
              key={item}
              className="overflow-hidden rounded-lg border border-black/10 bg-white/60"
            >
              <div className="aspect-[4/5] w-full animate-pulse bg-black/10" />
              <div className="space-y-3 p-5">
                <div className="h-3 w-1/3 animate-pulse rounded bg-black/10" />
                <div className="h-5 w-2/3 animate-pulse rounded bg-black/10" />
                <div className="h-3 w-full animate-pulse rounded bg-black/10" />
              </div>
            </div>
          ))}
        </div>
        <p className="mt-8 font-body text-sm text-muted">
          Reading the catalogue and reservation state…
        </p>
      </div>
    </main>
  );
}
