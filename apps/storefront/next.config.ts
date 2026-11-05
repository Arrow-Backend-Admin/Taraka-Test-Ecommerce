import type { NextConfig } from "next";

const isProduction = process.env.APP_ENV === "production";
const apiOrigin = (
  process.env.NEXT_PUBLIC_API_URL ??
  process.env.API_URL ??
  "http://localhost:8000"
).replace(/\/$/, "");

/**
 * Storefront security headers.
 *
 * Scripts need `'unsafe-inline'` because this app does not yet run the
 * nonce-based proxy described in the Next.js CSP guide. The API, which handles
 * money and order data, has a strict `default-src 'none'` policy. Nonce-based
 * CSP for the storefront is tracked in docs/known-limitations.md.
 */
const csp = [
  "default-src 'self'",
  `script-src 'self' 'unsafe-inline' https://checkout.razorpay.com`,
  "style-src 'self' 'unsafe-inline'",
  "img-src 'self' data: blob:",
  "font-src 'self'",
  `connect-src 'self' ${apiOrigin} https://api.razorpay.com https://lumberjack.razorpay.com`,
  "frame-src https://api.razorpay.com https://checkout.razorpay.com",
  "object-src 'none'",
  "base-uri 'self'",
  "form-action 'self'",
  "frame-ancestors 'none'",
  isProduction ? "upgrade-insecure-requests" : "",
]
  .filter(Boolean)
  .join("; ");

const securityHeaders = [
  { key: "Content-Security-Policy", value: csp },
  { key: "X-Content-Type-Options", value: "nosniff" },
  { key: "X-Frame-Options", value: "DENY" },
  { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
  { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
  ...(isProduction
    ? [
        {
          key: "Strict-Transport-Security",
          value: "max-age=31536000; includeSubDomains",
        },
      ]
    : []),
];

const nextConfig: NextConfig = {
  reactStrictMode: true,
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: securityHeaders,
      },
    ];
  },
};

export default nextConfig;
