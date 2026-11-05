import AxeBuilder from "@axe-core/playwright";
import { expect, type Page } from "@playwright/test";

export async function gotoCatalogue(page: Page): Promise<void> {
  await page.goto("/catalogue");
  await expect(
    page.getByRole("heading", { level: 1, name: "Catalogue" }),
  ).toBeVisible();
}

export async function openFirstProduct(page: Page): Promise<void> {
  await gotoCatalogue(page);
  const firstProduct = page.locator('ul li a[href^="/catalogue/"]').first();
  await expect(firstProduct).toBeVisible();
  await firstProduct.click();
  await expect(page.getByRole("heading", { level: 1 })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Sizes" })).toBeVisible();
}

export async function addFirstAvailableSize(page: Page): Promise<void> {
  const sizeButtons = page
    .locator("fieldset")
    .first()
    .locator("button[aria-pressed]");
  const count = await sizeButtons.count();
  expect(count).toBeGreaterThan(0);

  let added = false;
  for (let index = 0; index < count; index += 1) {
    const button = sizeButtons.nth(index);
    if (await button.isEnabled()) {
      await button.click();
      added = true;
      break;
    }
  }
  expect(added, "no size had stock in the seeded dev fixture").toBe(true);

  await page.getByRole("button", { name: "Add to cart" }).click();
  await expect(page.getByText(/Reserved \d+ x /)).toBeVisible();
}

export async function fillCheckoutForm(page: Page): Promise<void> {
  await page.getByLabel("Full name").fill("Asha Rao");
  await page.getByLabel("Email").fill("asha@example.com");
  await page.getByLabel("Mobile number").fill("9876543210");
  await page.getByLabel("Address line 1").fill("12 Lake View Road");
  await page.getByLabel("City").fill("Bengaluru");
  await page.getByLabel("State or union territory").selectOption("Karnataka");
  await page.getByLabel("Pincode").fill("560038");
}

/**
 * Chromium DevTools throttling profile close to "Fast 3G": 1.6 Mbps down,
 * 750 Kbps up and 150 ms latency. The network is restored when the test ends.
 */
export async function throttleTo3G(page: Page): Promise<void> {
  const session = await page.context().newCDPSession(page);
  await session.send("Network.enable");
  await session.send("Network.emulateNetworkConditions", {
    offline: false,
    latency: 150,
    downloadThroughput: (1.6 * 1024 * 1024) / 8,
    uploadThroughput: (750 * 1024) / 8,
    connectionType: "cellular3g",
  });
}

export async function expectNoSeriousAxeViolations(
  page: Page,
  context: string,
): Promise<void> {
  const results = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
    .analyze();
  const blocking = results.violations.filter(
    (violation) =>
      violation.impact === "serious" || violation.impact === "critical",
  );
  expect(
    blocking,
    `${context}: ${blocking
      .map((violation) => `${violation.id} (${violation.impact})`)
      .join(", ")}`,
  ).toEqual([]);
}
