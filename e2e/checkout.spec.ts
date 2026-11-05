import { expect, test } from "@playwright/test";

import {
  addFirstAvailableSize,
  fillCheckoutForm,
  openFirstProduct,
} from "./helpers";

async function reserveAndOpenCheckout(page: import("@playwright/test").Page) {
  await openFirstProduct(page);
  await addFirstAvailableSize(page);
  await page.getByRole("link", { name: "Checkout" }).first().click();
  await expect(
    page.getByRole("heading", { level: 1, name: "Checkout" }),
  ).toBeVisible();
  await expect(page.getByLabel("Full name")).toBeVisible();
}

test.describe("checkout and order", () => {
  test("guest can pay through the signed mock webhook and see a confirmed order", async ({
    page,
  }) => {
    await reserveAndOpenCheckout(page);
    await fillCheckoutForm(page);
    await page
      .getByRole("button", { name: "Create order and pay" })
      .click();

    await expect(
      page.getByText("Order created", { exact: false }),
    ).toBeVisible();
    const orderHeading = page.getByRole("heading", {
      level: 2,
      name: /^ord_/,
    });
    const publicId = (await orderHeading.textContent())?.trim() ?? "";
    expect(publicId).toMatch(/^ord_/);

    await page
      .getByRole("button", { name: "Simulate a successful payment" })
      .click();

    await expect(page).toHaveURL(new RegExp(`/orders/${publicId}$`));
    await expect(
      page.getByText("Payment confirmed", { exact: true }),
    ).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/Payment confirmed\./)).toBeVisible();
  });

  test("double-clicking the pay button cannot create two orders", async ({
    page,
  }) => {
    await reserveAndOpenCheckout(page);
    await fillCheckoutForm(page);

    const pay = page.getByRole("button", { name: "Create order and pay" });
    await pay.dblclick();

    await expect(
      page.getByText("Order created", { exact: false }),
    ).toBeVisible();
    // Exactly one order reference heading, and it is a high-entropy id.
    const orderHeadings = page.getByRole("heading", {
      level: 2,
      name: /^ord_/,
    });
    await expect(orderHeadings).toHaveCount(1);
    const publicId = (await orderHeadings.textContent())?.trim() ?? "";
    expect(publicId).toMatch(/^ord_[A-Za-z0-9_-]{24}$/);

    // The second click must not have produced a second order or an error.
    await expect(page.getByText(/Could not place the order/)).toHaveCount(0);
  });
});
