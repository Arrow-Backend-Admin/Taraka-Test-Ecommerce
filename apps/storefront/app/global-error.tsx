"use client";

export default function GlobalError({ retry }: { retry: () => void }) {
  return (
    <html lang="en">
      <body>
        <main style={{ fontFamily: "system-ui, sans-serif", padding: "4rem 1.5rem" }}>
          <p style={{ letterSpacing: "0.14em", textTransform: "uppercase" }}>
            Something went wrong
          </p>
          <h1 style={{ fontSize: "2rem", marginTop: "0.75rem" }}>
            The store could not start this page.
          </h1>
          <p style={{ maxWidth: "42rem", lineHeight: 1.7 }}>
            No payment is taken by this screen. Try again, or return to the
            catalogue.
          </p>
          <button
            type="button"
            onClick={() => retry()}
            style={{
              marginTop: "1.5rem",
              padding: "0.75rem 1.5rem",
              borderRadius: "999px",
              border: "1px solid #111",
              background: "#111",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            Try again
          </button>
        </main>
      </body>
    </html>
  );
}
