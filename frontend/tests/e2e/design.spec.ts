import { test, expect, type Page } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";
import { readFileSync, existsSync } from "node:fs";

// Real OIDC + real backend reads. No mocked identity/API or learning-data writes.
const file =
  process.env.E2E_CREDENTIALS_FILE || "../infra/runtime/credentials.json";
const credentials = existsSync(file)
  ? JSON.parse(readFileSync(file, "utf8"))
  : {};
async function login(page: Page) {
  test.skip(
    !credentials["learner-a"],
    "Requires private runtime credentials for real OIDC.",
  );
  await page.goto("/");
  await page
    .getByRole("button", { name: "ورود به آکادمی", exact: true })
    .click();
  await page.locator("#username").fill(credentials["learner-a"].username);
  await page.locator("#password").fill(credentials["learner-a"].password);
  await page.locator("#kc-login").click();
  await expect(page.locator("#main")).toBeVisible();
}
async function accessible(page: Page) {
  await page.evaluate(() => document.fonts.ready);
  const result = await new AxeBuilder({ page })
    .withTags(["wcag2a", "wcag2aa", "wcag21aa", "wcag22aa"])
    .analyze();
  expect(
    result.violations.map((v) => ({
      id: v.id,
      impact: v.impact,
      nodes: v.nodes.map((n) => ({
        target: n.target,
        failure: n.failureSummary,
      })),
    })),
  ).toEqual([]);
}
async function noOverflow(page: Page) {
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth + 1,
    ),
  ).toBe(true);
}
async function navigate(page: Page, name: string) {
  const nav = page.getByRole("navigation", { name: "ناوبری اصلی" });
  if (!(await nav.isVisible()))
    await page.getByRole("button", { name: "فهرست", exact: true }).click();
  await nav
    .getByRole("button", {
      name: name === "مربی هوشمند" ? /^مربی هوشمند/ : name,
      exact: name !== "مربی هوشمند",
    })
    .click();
}

test("real authenticated ten-screen desktop accessibility and truthful capability states", async ({
  page,
}) => {
  test.setTimeout(180_000);
  await login(page);
  for (const name of [
    "داشبورد",
    "دوره‌ها",
    "فضای یادگیری",
    "مسیر یادگیری",
    "مربی هوشمند",
    "پیشرفت و تکالیف",
    "پروژه‌ها",
    "کتابخانه",
    "پروفایل",
    "مدیریت",
  ]) {
    await navigate(page, name);
    await expect(page.locator("#main")).toBeVisible();
    await noOverflow(page);
    await accessible(page);
  }
  for (const theme of ["light", "dark"]) {
    if (theme === "dark")
      await page.getByRole("button", { name: "تغییر پوسته" }).click();
    await expect(page.locator("html")).toHaveAttribute("data-theme", theme);
    for (const variant of ["jade", "ink", "paper"]) {
      await navigate(page, "پروفایل");
      await page.getByLabel("سبک بصری", { exact: true }).selectOption(variant);
      await expect(page.locator("html")).toHaveAttribute(
        "data-variant",
        variant,
      );
      await accessible(page);
      await navigate(page, "داشبورد");
      await accessible(page);
    }
  }
});

for (const width of [320, 390]) {
  test(`real learner mobile ${width}px RTL, keyboard and reduced preferences`, async ({
    page,
  }) => {
    await page.setViewportSize({ width, height: 844 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    await login(page);
    await expect(page.locator("html")).toHaveAttribute("dir", "rtl");
    await noOverflow(page);
    await accessible(page);
    await navigate(page, "پروفایل");
    await page.getByLabel(/^کاهش شفافیت/).check();
    await page.getByLabel(/^کاهش حرکت/).check();
    await expect(page.locator("html")).toHaveAttribute("data-solid", "true");
    await expect(page.locator("html")).toHaveAttribute("data-quiet", "true");
    expect(
      await page
        .locator(".glass")
        .first()
        .evaluate((el) => getComputedStyle(el).backdropFilter),
    ).toBe("none");
    await noOverflow(page);
    await accessible(page);
    await page.keyboard.press("Tab");
    expect(
      await page.evaluate(() => document.activeElement !== document.body),
    ).toBe(true);
  });
}

test("real learner locale and preferences persist without sensitive web storage or caches", async ({
  page,
}) => {
  await login(page);
  await page.getByRole("button", { name: "English", exact: true }).click();
  await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  await noOverflow(page);
  await accessible(page);
  await page.reload();
  await expect(page.locator("#main")).toBeVisible();
  await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
  const sensitive = await page.evaluate(async () => {
    const storage = [
      ...Object.entries(localStorage),
      ...Object.entries(sessionStorage),
    ]
      .filter(([key, value]) =>
        /access.?token|refresh.?token|id.?token|password|authorization|submission|wstoken/i.test(
          key + " " + value,
        ),
      )
      .map(([key]) => key);
    const cached: string[] = [];
    for (const name of await caches.keys()) {
      for (const request of await (await caches.open(name)).keys()) {
        if (
          /\/api(?:\/|$)|\/realms\/|webservice|wstoken|\/auth\//i.test(
            request.url,
          )
        )
          cached.push(new URL(request.url).pathname);
      }
    }
    return { storage, cached };
  });
  expect(sensitive).toEqual({ storage: [], cached: [] });
});

test("mobile menu traps keyboard focus and Escape restores trigger", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await login(page);
  const trigger = page.getByRole("button", { name: "فهرست", exact: true });
  await trigger.click();
  const dialog = page.getByRole("dialog", { name: "فهرست ناوبری" });
  await expect(dialog).toBeVisible();
  for (let i = 0; i < 24; i++) {
    await page.keyboard.press("Tab");
    expect(
      await dialog.evaluate((el) => el.contains(document.activeElement)),
    ).toBe(true);
  }
  await page.keyboard.press("Escape");
  await expect(dialog).toHaveCount(0);
  await expect(trigger).toBeFocused();
});

test("PWA offline navigation exposes public fallback without cached learning data", async ({
  page,
  context,
}) => {
  await login(page);
  await page.evaluate(() => navigator.serviceWorker.ready);
  await page.reload();
  await expect(page.locator("#main")).toBeVisible();
  const paths = await page.evaluate(async () => {
    const out: string[] = [];
    for (const name of await caches.keys())
      for (const request of await (await caches.open(name)).keys())
        out.push(new URL(request.url).pathname);
    return out;
  });
  expect(paths.length).toBeGreaterThan(0);
  expect(
    paths.every((p) =>
      ["/offline.html", "/icon.svg", "/icon-192.png", "/icon-512.png"].includes(
        p,
      ),
    ),
  ).toBe(true);
  await context.setOffline(true);
  await page.goto("/");
  await expect(page.locator("body")).toContainText("آفلاین");
  await expect(page.locator("body")).not.toContainText(
    "00000000-0000-4000-8000",
  );
});
