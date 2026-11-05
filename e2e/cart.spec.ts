import { expect, test } from "@playwright/test";

import { addFirstAvailableSize, openFirstProduct } from "./helpers";

test.describe("guest cart", () => {
  test("a size can be reserved and released from a fresh cart", async ({
    page,
  }) => {
    await openFirstProduct(page);
    await addFirstAvailableSize(page);

    const cart = page.getByRole("region", { name: "Guest cart" });
    await expect(cart.getByText(/Reserved until/)).toBeVisible();
    await expect(cart.getByText(/unit|units/).first()).toBeVisible();
    await expect(
      cart.getByRole("link", { name: "Checkout" }),
    ).toBeVisible();

    await cart.getByRole("button", { name: "Remove" }).first().click();
    await expect(
      cart.getByText(/Your cart is empty/),
    ).toBeVisible();
  });

  test("cart survives a reload through the httpOnly cookie", async ({
    page,
  }) => {
    await openFirstProduct(page);
    await addFirstAvailableSize(page);
    const cart = page.getByRole("region", { name: "Guest cart" });
    await expect(cart.getByText(/Reserved until/)).toBeVisible();

    await page.reload();
    await expect(
      page.getByRole("region", { name: "Guest cart" }).getByText(/Reserved until/),
    ).toBeVisible();
  });
});
