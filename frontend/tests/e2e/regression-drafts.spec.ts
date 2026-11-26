import { test, expect, type Page } from "@playwright/test";
import { existsSync, readFileSync } from "node:fs";
const file =
  process.env.E2E_CREDENTIALS_FILE || "../infra/runtime/credentials.json";
const credentials = existsSync(file)
  ? JSON.parse(readFileSync(file, "utf8"))
  : {};
async function login(page: Page, role = "learner-a") {
  test.skip(!credentials[role], "Requires private real OIDC test credentials.");
  await page.goto("/");
  await page
    .getByRole("button", { name: "ورود به آکادمی", exact: true })
    .click();
  await page.locator("#username").fill(credentials[role].username);
  await page.locator("#password").fill(credentials[role].password);
  await page.locator("#kc-login").click();
  await expect(page.locator("#main")).toBeVisible();
}
async function navigate(page: Page, name: string) {
  await page
    .getByRole("navigation", { name: "ناوبری اصلی" })
    .getByRole("button", { name, exact: true })
    .click();
}
function trackWrites(page: Page) {
  const writes: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (
      url.pathname.startsWith("/api/") &&
      !["GET", "HEAD", "OPTIONS"].includes(request.method())
    )
      writes.push(`${request.method()} ${url.pathname}`);
  });
  return writes;
}
test("unsent assignment draft survives leaving workspace and stays scoped to its course", async ({
  page,
}) => {
  await login(page);
  const writes = trackWrites(page);
  await page
    .getByRole("button", { name: "مشاهده دوره", exact: true })
    .first()
    .click();
  const draft =
    "Unsent local draft: preserve this practice evidence while navigating.";
  const field = page.getByLabel("متن پاسخ و شواهد تمرین", { exact: true });
  await expect(
    field,
    "Read-only prerequisite: existing learner enrollment from learning regression fixture",
  ).toBeVisible();
  await field.fill(draft);
  await navigate(page, "پروفایل");
  await navigate(page, "فضای یادگیری");
  await expect(field).toHaveValue(draft);
  await navigate(page, "دوره‌ها");
  const courses = page.getByRole("button", {
    name: "مشاهده دوره",
    exact: true,
  });
  if ((await courses.count()) > 1) {
    await courses.nth(1).click();
    if (await field.isVisible()) await expect(field).not.toHaveValue(draft);
    await navigate(page, "دوره‌ها");
  }
  await page
    .getByRole("button", { name: "مشاهده دوره", exact: true })
    .first()
    .click();
  await expect(field).toHaveValue(draft);
  expect(writes).toEqual([]);
});
test("unsent reviewer feedback survives leaving review without sending it or leaking to another submission", async ({
  page,
}) => {
  await login(page, "reviewer-a");
  const writes = trackWrites(page);
  await navigate(page, "بازبینی تکالیف");
  const fields = page.getByLabel("بازخورد بازبین", { exact: true });
  await expect(
    fields.first(),
    "Read-only prerequisite: existing submitted assignment fixture",
  ).toBeVisible();
  const id = await fields.first().getAttribute("id");
  expect(id).toBeTruthy();
  const draft =
    "Unsent reviewer feedback: add one reproducible verification receipt.";
  await fields.first().fill(draft);
  if ((await fields.count()) > 1)
    await expect(fields.nth(1)).not.toHaveValue(draft);
  await navigate(page, "داشبورد");
  await navigate(page, "پروفایل");
  await navigate(page, "بازبینی تکالیف");
  await expect(page.locator(`[id="${id}"]`)).toHaveValue(draft);
  expect(writes).toEqual([]);
});
test("open mobile drawer resets modal state on desktop resize and remains usable when resized back", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page);
  const trigger = page.getByRole("button", { name: "فهرست", exact: true });
  await trigger.click();
  await expect(
    page.getByRole("dialog", { name: "فهرست ناوبری" }),
  ).toBeVisible();
  await page.setViewportSize({ width: 1440, height: 1000 });
  await expect(page.getByRole("dialog")).toHaveCount(0);
  await expect(page.locator(".main-column")).not.toHaveAttribute("inert", "");
  await navigate(page, "پروفایل");
  await expect(page.getByLabel("سبک بصری", { exact: true })).toBeVisible();
  await page.setViewportSize({ width: 390, height: 844 });
  await expect(trigger).toHaveAttribute("aria-expanded", "false");
  await trigger.click();
  await expect(
    page.getByRole("dialog", { name: "فهرست ناوبری" }),
  ).toBeVisible();
  await page.keyboard.press("Escape");
  await expect(trigger).toBeFocused();
});
