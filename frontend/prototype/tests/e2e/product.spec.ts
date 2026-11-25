import { test, expect } from "@playwright/test";
const legacy = { done: [5, 2, 1], saved: [0, 3], sim: 7 };
async function seed(
  page: import("@playwright/test").Page,
  raw = JSON.stringify(legacy),
) {
  await page.addInitScript((value) => {
    if (!localStorage.getItem("test-seeded")) {
      localStorage.setItem("nikway-demo-v1", value);
      localStorage.setItem("test-seeded", "yes");
    }
  }, raw);
  await page.goto("/");
}
async function nav(page: import("@playwright/test").Page, id: string) {
  await page.locator(`nav a[href="#/${id}"]`).click();
  await expect(page.locator('nav a[aria-current="page"]')).toHaveAttribute(
    "href",
    `#/${id}`,
  );
  const titles: Record<string, RegExp> = {
    dashboard: /سلام یادگیرنده آزمایشی|Welcome back/,
    academy: /آکادمی نیک‌وی|NIKWAY Academy/,
    library: /کتابخانه دانش|Knowledge library/,
    tutor: /مربی هوشمند شما|Your learning tutor/,
    competency: /نقشه شایستگی|Competency map/,
    lab: /آزمایشگاه شبیه‌سازی|Simulation lab/,
  };
  await expect(page.getByRole("heading", { level: 1 })).toHaveText(titles[id]);
  await page.evaluate(() => document.fonts.ready.then(() => true));
}
test("migrates real legacy shape and completes a lesson durably", async ({
  page,
}) => {
  await seed(page);
  await nav(page, "academy");
  await page.getByRole("button", { name: "ورود به دوره" }).first().click();
  await expect(page.getByRole("dialog")).toContainText("۵ از ۸");
  await page.getByRole("button", { name: "تکمیل این درس ✓" }).click();
  await expect(page.getByRole("dialog")).toBeHidden();
  await page.reload();
  await page.getByRole("button", { name: "ورود به دوره" }).first().click();
  await expect(page.getByRole("dialog")).toContainText("۶ از ۸");
  expect(
    await page.evaluate(() =>
      JSON.parse(localStorage.getItem("nikway-demo-v1")!),
    ),
  ).toEqual(legacy);
});
test("searches courses and resources, saves and reads a resource", async ({
  page,
}) => {
  await seed(page);
  await nav(page, "academy");
  await page.getByRole("textbox", { name: "جست‌وجوی دوره" }).fill("ناب");
  await expect(page.locator('[data-testid="course-card"]')).toHaveCount(1);
  await page.getByRole("textbox", { name: "جست‌وجوی دوره" }).fill("ناموجود");
  await expect(page.getByText("دوره‌ای پیدا نشد")).toBeVisible();
  await nav(page, "library");
  await page.getByRole("button", { name: "نشان‌شده‌ها", exact: true }).click();
  await expect(page.locator('[data-testid="resource-card"]')).toHaveCount(2);
  await page
    .getByRole("button", { name: "مطالعه", exact: true })
    .first()
    .click();
  await expect(page.getByRole("dialog")).toContainText("حلقه‌های تقویتی");
  await page.keyboard.press("Escape");
  await page
    .getByRole("button", { name: /حذف نشان/ })
    .first()
    .click();
  await expect(page.locator('[data-testid="resource-card"]')).toHaveCount(1);
  await page.reload();
  await page.getByRole("button", { name: "نشان‌شده‌ها", exact: true }).click();
  await expect(page.locator('[data-testid="resource-card"]')).toHaveCount(1);
});
test("tutor stays mocked and retains chat across navigation without executing user text", async ({
  page,
}) => {
  await seed(page);
  await nav(page, "tutor");
  await page
    .getByRole("button", { name: "تفکر سیستمی چیست؟", exact: true })
    .click();
  await expect(page.getByRole("log")).toContainText("ارتباط اجزا");
  await page
    .getByRole("textbox", { name: "پیام به مربی" })
    .fill("<img src=x onerror=alert(1)>");
  await page.getByRole("button", { name: "ارسال", exact: true }).click();
  await expect(page.getByRole("log")).toContainText("پاسخ اختصاصی ندارم");
  expect(await page.locator("[role=log] img").count()).toBe(0);
  await nav(page, "dashboard");
  await nav(page, "tutor");
  await expect(page.getByRole("log")).toContainText("<img src=x");
});
test("simulation branches update dashboard and competency evidence", async ({
  page,
}) => {
  await seed(page);
  await nav(page, "lab");
  await page.getByRole("button", { name: "شروع شبیه‌سازی" }).click();
  await expect(
    page.getByRole("button", { name: "اجرای تصمیم" }),
  ).toBeDisabled();
  await page.getByRole("button", { name: /افزایش ظرفیت آماده‌سازی/ }).click();
  await page.getByRole("button", { name: "اجرای تصمیم", exact: true }).click();
  await expect(
    page.getByText("ظرفیت اضافه شد، خروجی تغییری نکرد"),
  ).toBeVisible();
  await page.getByRole("button", { name: "آزمایش تصمیم دیگر" }).click();
  await page.getByRole("button", { name: /افزایش ظرفیت مونتاژ/ }).click();
  await page.getByRole("button", { name: "اجرای تصمیم", exact: true }).click();
  await expect(page.getByText("تصمیم مؤثر؛ گلوگاه بهبود یافت")).toBeVisible();
  await expect(page.getByTestId("delivery")).toContainText("۸۰");
  await nav(page, "competency");
  await page.getByRole("button", { name: /حل مسئله/ }).click();
  await expect(page.getByRole("dialog")).toContainText("۹ تمرین");
  await page.keyboard.press("Escape");
  await nav(page, "dashboard");
  await expect(page.getByTestId("simulation-count")).toHaveText("۹");
});
test("mobile RTL and English LTR navigation work without horizontal overflow", async ({
  page,
}) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await seed(page);
  for (const id of [
    "dashboard",
    "academy",
    "library",
    "tutor",
    "competency",
    "lab",
  ]) {
    await nav(page, id);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
    ).toBe(true);
  }
  await page.getByRole("button", { name: "English" }).click();
  await expect(page.locator("html")).toHaveAttribute("dir", "ltr");
  await nav(page, "academy");
  await expect(
    page.getByRole("heading", { name: "NIKWAY Academy" }),
  ).toBeVisible();
  await page.reload();
  await expect(page.locator("html")).toHaveAttribute("lang", "en");
  expect(
    await page.evaluate(
      () => document.documentElement.scrollWidth <= innerWidth,
    ),
  ).toBe(true);
});
test("offline reload and six modules work after first installation", async ({
  page,
  context,
}) => {
  await seed(page);
  await expect(page.getByTestId("offline-status")).toHaveText(
    "آمادهٔ استفاده آفلاین",
  );
  await page.evaluate(async () => {
    await navigator.serviceWorker.ready;
  });
  await context.setOffline(true);
  await page.reload();
  await expect(
    page.getByRole("heading", { name: /سلام یادگیرنده آزمایشی/ }),
  ).toBeVisible();
  for (const id of [
    "academy",
    "library",
    "tutor",
    "competency",
    "lab",
    "dashboard",
  ])
    await nav(page, id);
  await expect(page.getByTestId("simulation-count")).toHaveText("۷");
  await context.setOffline(false);
});
test("corrupt local data is preserved and shown as a recoverable error", async ({
  page,
}) => {
  await seed(page, "{broken");
  await expect(page.getByRole("alert")).toContainText("خواندن داده");
  expect(
    await page.evaluate(() => localStorage.getItem("nikway-demo-v1")),
  ).toBe("{broken");
  await expect(
    page.getByRole("button", { name: "دریافت نسخهٔ اصلی" }),
  ).toBeVisible();
});
test("reset asks for confirmation and never resurrects legacy progress", async ({
  page,
}) => {
  await seed(page);
  await page
    .getByRole("button", { name: "بازنشانی نمونه", exact: true })
    .click();
  await page.getByRole("button", { name: "انصراف", exact: true }).click();
  await expect(page.getByTestId("simulation-count")).toHaveText("۷");
  await page
    .getByRole("button", { name: "بازنشانی نمونه", exact: true })
    .click();
  await page.getByRole("button", { name: "تأیید بازنشانی" }).click();
  await expect(page.getByTestId("simulation-count")).toHaveText("۰");
  await page.reload();
  await expect(page.getByTestId("simulation-count")).toHaveText("۰");
});
test("portable export/import restores progress, invalid backup leaves state intact", async ({
  page,
}) => {
  await seed(page);
  const download = page.waitForEvent("download");
  await page.getByRole("button", { name: "خروجی داده‌ها" }).click();
  const file = await download;
  expect(file.suggestedFilename()).toContain("nikway");
  await page
    .getByLabel("ورود داده‌ها")
    .setInputFiles({
      name: "bad.json",
      mimeType: "application/json",
      buffer: Buffer.from("{bad"),
    });
  await expect(page.getByRole("alert")).toContainText("نامعتبر");
  await expect(page.getByTestId("simulation-count")).toHaveText("۷");
  await page
    .getByLabel("ورود داده‌ها")
    .setInputFiles({
      name: "valid.json",
      mimeType: "application/json",
      buffer: Buffer.from(JSON.stringify({ ...legacy, sim: 12 })),
    });
  await expect(page.getByTestId("simulation-count")).toHaveText("۱۲");
});
test("simulation session survives module navigation and back button", async ({
  page,
}) => {
  await seed(page);
  await nav(page, "lab");
  await page.getByRole("button", { name: "شروع شبیه‌سازی" }).click();
  await page.getByRole("button", { name: /افزایش ظرفیت مونتاژ/ }).click();
  await nav(page, "library");
  await page.goBack();
  await expect(
    page.getByRole("button", { name: /افزایش ظرفیت مونتاژ/ }),
  ).toHaveAttribute("aria-pressed", "true");
});
test("all six pages render without runtime exceptions or failed assets", async ({
  page,
}) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const failed: string[] = [];
  page.on("response", (r) => {
    if (r.status() >= 400) failed.push(r.url());
  });
  await seed(page);
  for (const id of [
    "academy",
    "library",
    "tutor",
    "competency",
    "lab",
    "dashboard",
  ]) {
    await nav(page, id);
    await expect(page.locator("h1")).toBeVisible();
  }
  expect(errors).toEqual([]);
  expect(failed).toEqual([]);
});
test("captures six desktop views and checks narrow-screen dialogs", async ({
  page,
}) => {
  await page.setViewportSize({ width: 1440, height: 1080 });
  await seed(page);
  for (const id of [
    "dashboard",
    "academy",
    "library",
    "tutor",
    "competency",
    "lab",
  ]) {
    await nav(page, id);
    await page.screenshot({
      path: `evidence/${id}-desktop.png`,
      fullPage: true,
    });
  }
  await page.setViewportSize({ width: 390, height: 844 });
  await nav(page, "dashboard");
  await page.screenshot({
    path: "evidence/dashboard-mobile.png",
    fullPage: true,
  });
  await page.setViewportSize({ width: 320, height: 740 });
  for (const id of [
    "dashboard",
    "academy",
    "library",
    "tutor",
    "competency",
    "lab",
  ]) {
    await nav(page, id);
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth <= innerWidth,
      ),
      id,
    ).toBe(true);
  }
  await nav(page, "academy");
  await page.getByRole("button", { name: "ورود به دوره" }).first().click();
  const box = await page.getByRole("dialog").boundingBox();
  expect(box!.x).toBeGreaterThanOrEqual(0);
  expect(box!.x + box!.width).toBeLessThanOrEqual(320);
  await page.keyboard.press("Escape");
  await expect(page.getByRole("dialog")).toBeHidden();
  await page.getByRole("button", { name: "English" }).click();
  await nav(page, "dashboard");
  await page.setViewportSize({ width: 1440, height: 1080 });
  await page.screenshot({
    path: "evidence/dashboard-english.png",
    fullPage: true,
  });
});
