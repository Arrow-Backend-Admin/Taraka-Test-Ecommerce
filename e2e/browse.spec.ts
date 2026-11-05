import { expect, test } from "@playwright/test";

import {
  expectNoSeriousAxeViolations,
  gotoCatalogue,
  openFirstProduct,
  throttleTo3G,
} from "./helpers";

test.describe("browse", () => {
  test("catalogue and product detail render on a mobile viewport", async ({
    page,
  }) => {
    await gotoCatalogue(page);
    const cards = page.locator('ul li a[href^="/catalogue/"]');
    await expect(cards.first()).toBeVisible();
    expect(await cards.count()).toBeGreaterThan(0);

    await openFirstProduct(page);
    await expect(page.getByRole("heading", { name: "Images" })).toBeVisible();
    await expect(page.getByRole("heading", { name: "Sizes" })).toBeVisible();
    await expect(page.getByText(/Choose a UK size/)).toBeVisible();
  });

  test("catalogue stays usable on throttled 3G", async ({ page }) => {
    await throttleTo3G(page);
    const started = Date.now();
    await gotoCatalogue(page);
    const firstProduct = page.locator('ul li a[href^="/catalogue/"]').first();
    await expect(firstProduct).toBeVisible({ timeout: 30_000 });
    // A catalogue page that needs more than 30 seconds on 3G is not shippable
    // for this milestone; the budget is deliberately generous for CI runners.
    expect(Date.now() - started).toBeLessThan(30_000);
  });

  test("catalogue has no serious or critical axe violations", async ({
    page,
  }) => {
    await gotoCatalogue(page);
    await expectNoSeriousAxeViolations(page, "catalogue");
  });

  test("product detail has no serious or critical axe violations", async ({
    page,
  }) => {
    await openFirstProduct(page);
    await expectNoSeriousAxeViolations(page, "product detail");
  });
});
