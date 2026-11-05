import { defineConfig, devices } from "@playwright/test";

const apiUrl = process.env.E2E_API_URL ?? "http://127.0.0.1:8000";
const storefrontUrl = process.env.E2E_STOREFRONT_URL ?? "http://127.0.0.1:3000";
const python = process.env.PYTHON ?? "python";

/**
 * Mobile-first browser checks for the guest purchase path.
 *
 * The API and storefront must already be seeded with the development fixture:
 *
 *   cd apps/api
 *   alembic upgrade head
 *   python scripts/seed.py
 *
 * `npm run e2e` starts both servers when they are not already running. CI
 * seeds the database before calling Playwright.
 */
export default defineConfig({
  testDir: "./e2e",
  outputDir: "./test-results",
  timeout: 90_000,
  expect: { timeout: 15_000 },
  fullyParallel: false,
  workers: 1,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI
    ? [["list"], ["html", { outputFolder: "playwright-report", open: "never" }]]
    : [["list"]],
  use: {
    baseURL: storefrontUrl,
    trace: "retain-on-failure",
    screenshot: "only-on-failure",
    video: "retain-on-failure",
    locale: "en-IN",
    timezoneId: "Asia/Kolkata",
  },
  projects: [
    {
      name: "mobile-chromium",
      use: { ...devices["Pixel 7"] },
    },
  ],
  webServer: [
    {
      command: `${python} -m uvicorn app.main:app --host 127.0.0.1 --port 8000`,
      cwd: "apps/api",
      url: `${apiUrl}/health/live`,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        APP_ENV: "development",
        DATABASE_URL:
          process.env.DATABASE_URL ?? "sqlite:///./santvana-dev.db",
        ADMIN_API_TOKEN: "e2e-admin-token",
        RAZORPAY_MOCK: "true",
        RAZORPAY_KEY_ID: "rzp_test_mock",
        RAZORPAY_KEY_SECRET: "test-key-secret",
        RAZORPAY_WEBHOOK_SECRET: "test-webhook-secret",
        MAIL_ENABLED: "false",
        CORS_ORIGINS: storefrontUrl,
        STOREFRONT_URL: storefrontUrl,
      },
    },
    {
      command: "npm run dev --workspace @santvana/storefront",
      url: storefrontUrl,
      reuseExistingServer: !process.env.CI,
      timeout: 120_000,
      env: {
        API_URL: apiUrl,
        NEXT_PUBLIC_API_URL: apiUrl,
        APP_ENV: "development",
        PREVIEW_DRAFTS: "true",
      },
    },
  ],
});
