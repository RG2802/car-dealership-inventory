import { test, expect } from "@playwright/test";

test("admin manages inventory, filters and purchases; responsive screenshots", async ({
  page,
}) => {
  await page.goto("/");
  await page.screenshot({ path: "../docs/login.png", fullPage: true });
  await page.getByLabel("Email address").fill("admin@example.com");
  await page.getByLabel("Password", { exact: true }).fill("AdminTesting42!");
  await page.getByRole("button", { name: "Sign in", exact: true }).click();
  await expect(
    page.getByRole("heading", { name: "Find your next drive." }),
  ).toBeVisible();
  await expect(page.locator(".vehicle-card")).toHaveCount(6);
  await page.screenshot({
    path: "../docs/dashboard-desktop.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 390, height: 844 });
  await page.screenshot({
    path: "../docs/dashboard-mobile.png",
    fullPage: true,
  });
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= window.innerWidth,
    ),
  ).toBe(true);
  await page.setViewportSize({ width: 1440, height: 1050 });
  await page.getByRole("button", { name: "Add vehicle" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Make", { exact: true }).fill("Test");
  await dialog.getByLabel("Model", { exact: true }).fill("Roadster");
  await dialog.getByLabel("Price (USD)").fill("12345.67");
  await dialog.getByLabel("Quantity", { exact: true }).fill("1");
  await dialog.getByRole("button", { name: "Save changes" }).click();
  const card = page.locator(".vehicle-card").filter({ hasText: "Roadster" });
  await expect(card).toBeVisible();
  await card.getByRole("button", { name: "Purchase", exact: true }).click();
  await expect(
    card.getByRole("button", { name: "Out of stock" }),
  ).toBeDisabled();
  await card.getByRole("button", { name: "Restock" }).click();
  await dialog.getByLabel("Units to add").fill("3");
  await dialog.getByRole("button", { name: "Save changes" }).click();
  await expect(card).toContainText("3 in stock");
  await card.getByRole("button", { name: "Edit", exact: true }).click();
  await dialog.getByLabel("Model", { exact: true }).fill("Roadster Plus");
  await dialog.getByRole("button", { name: "Save changes" }).click();
  await expect(card).toContainText("Roadster Plus");
  await page
    .locator(".filters")
    .getByLabel("Make", { exact: true })
    .fill("Test");
  await page.getByRole("button", { name: "Search", exact: true }).click();
  await expect(page.locator(".vehicle-card")).toHaveCount(1);
  await card.getByRole("button", { name: "Delete", exact: true }).click();
  await dialog.getByRole("button", { name: "Confirm delete" }).click();
  await expect(
    page.getByRole("heading", { name: "No vehicles found" }),
  ).toBeVisible();
  await page.getByRole("button", { name: "Reset", exact: true }).click();
  await expect(page.locator(".vehicle-card")).toHaveCount(6);
  await page.getByRole("button", { name: "Sign out" }).click();
  await expect(
    page.getByRole("heading", { name: "Good to see you again." }),
  ).toBeVisible();
});

test("buyer registers, sees sold-out state and cannot see admin controls", async ({
  page,
}) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Create an account" }).click();
  await page.getByLabel("Email address").fill("buyer-browser@example.com");
  await page.getByLabel("Password", { exact: true }).fill("BuyerTesting42!");
  await page
    .getByRole("button", { name: "Create account", exact: false })
    .click();
  await expect(page.locator(".vehicle-card")).toHaveCount(6);
  await expect(page.getByRole("button", { name: "Add vehicle" })).toHaveCount(
    0,
  );
  await expect(
    page.getByRole("button", { name: "Delete", exact: true }),
  ).toHaveCount(0);
  await expect(
    page.getByRole("button", { name: "Out of stock" }),
  ).toBeDisabled();
  await page
    .locator(".vehicle-card")
    .filter({ hasText: "Camry" })
    .getByRole("button", { name: "Purchase", exact: true })
    .click();
  await expect(page.getByRole("status")).toContainText("Purchase recorded");
});
