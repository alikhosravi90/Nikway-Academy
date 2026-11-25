import { test, expect, type Page } from "@playwright/test";
import { readFileSync, existsSync } from "node:fs";
const path =
  process.env.E2E_CREDENTIALS_FILE || "../infra/runtime/credentials.json";
const credentials = existsSync(path)
  ? JSON.parse(readFileSync(path, "utf8"))
  : {};
const title =
  process.env.E2E_IMPORTED_COURSE_TITLE || "مبانی مهندسی عامل: از هدف تا شواهد";
async function login(
  page: Page,
  identity: { username: string; password: string },
) {
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به آکادمی" }).click();
  await page.locator("#username").fill(identity.username);
  await page.locator("#password").fill(identity.password);
  await page.locator("#kc-login").click();
  await expect(
    page.getByRole("navigation", { name: "ناوبری اصلی" }),
  ).toBeVisible();
}
test("imported course objectives, practice and human rubric support a real learner-reviewer journey", async ({
  browser,
}, testInfo) => {
  test.skip(
    !credentials["learner-a"] ||
      !credentials["reviewer-a"] ||
      !credentials["learner-b"],
    "Runtime credentials are required; no mocked course or login.",
  );
  const learner = await browser.newContext(),
    reviewer = await browser.newContext(),
    other = await browser.newContext();
  const page = await learner.newPage();
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.addInitScript(() => {
    (window as any).__contentCsp = [];
    document.addEventListener("securitypolicyviolation", (e) =>
      (window as any).__contentCsp.push(e.violatedDirective),
    );
  });
  try {
    const responsePromise = page.waitForResponse(
      (r) => r.url().endsWith("/api/courses") && r.status() === 200,
    );
    await login(page, credentials["learner-a"]);
    const response = await responsePromise;
    const courses = await response.json();
    const course = courses.find((c: any) => c.title === title);
    expect(
      course,
      "The approved package must be admitted to tenant A before this test",
    ).toBeTruthy();
    expect(course.metadata?.assessment?.mode).toBe("human_review");
    const started = Date.now();
    await page
      .locator("article")
      .filter({ has: page.getByRole("heading", { name: title, exact: true }) })
      .getByRole("button", { name: "مشاهده دوره" })
      .click();
    await expect(
      page.getByRole("region", { name: "هدف‌های یادگیری" }),
    ).toBeVisible();
    const courseOpenMs = Date.now() - started;
    for (const objective of course.metadata.objectives)
      await expect(
        page.getByText(objective.description, { exact: true }).first(),
      ).toBeVisible();
    const enroll = page.getByRole("button", {
      name: "ثبت‌نام در دوره",
      exact: true,
    });
    if (await enroll.isVisible()) await enroll.click();
    for (const lesson of course.lessons) {
      await expect(
        page.getByRole("heading", { name: lesson.title, exact: true }),
      ).toBeVisible();
      await expect(
        page.getByText(lesson.content, { exact: true }),
      ).toBeVisible();
      if (lesson.metadata?.practice)
        await expect(
          page.getByText(lesson.metadata.practice.prompt, { exact: true }),
        ).toBeVisible();
    }
    await expect(
      page.getByRole("region", { name: "راهنمای تکلیف" }),
    ).toBeVisible();
    await page.getByText("معیارهای بازبینی انسانی", { exact: true }).click();
    for (const criterion of course.metadata.rubric.criteria)
      await expect(
        page.getByRole("heading", { name: criterion.description, exact: true }),
      ).toBeVisible();
    await expect(
      page.locator("article iframe, article script, article img"),
    ).toHaveCount(0);
    const field = page.getByLabel("متن پاسخ و شواهد تمرین");
    await expect(field).toHaveAttribute(
      "minlength",
      String(course.metadata.assessment.minCharacters),
    );
    await expect(field).toHaveAttribute(
      "maxlength",
      String(course.metadata.assessment.maxCharacters),
    );
    const next = page
      .getByRole("button", { name: "ثبت تکمیل درس", exact: true })
      .first();
    while (await next.count()) {
      await next.click();
      await expect(page.getByRole("status")).toContainText("با موفقیت ثبت شد");
    }
    const marker = `Imported course evidence ${Date.now()}`;
    const content =
      marker +
      "\n" +
      "شواهد آزمایشی: هدف، محدوده، اقدام و نتیجه بازبینی انسانی ثبت شد. ".repeat(
        Math.ceil(course.metadata.assessment.minCharacters / 60) + 1,
      );
    expect(content.length).toBeLessThanOrEqual(
      course.metadata.assessment.maxCharacters,
    );
    await field.fill(content);
    await page.getByRole("button", { name: "ارسال برای بازبینی" }).click();
    await expect(page.getByRole("status")).toContainText("با موفقیت ثبت شد");
    const reviewerPage = await reviewer.newPage();
    await login(reviewerPage, credentials["reviewer-a"]);
    await reviewerPage
      .getByRole("button", { name: "بازبینی تکالیف", exact: true })
      .click();
    const item = reviewerPage.locator("article").filter({ hasText: marker });
    await expect(
      item.getByRole("heading", { name: title, exact: true }),
    ).toBeVisible();
    await expect(
      item.getByRole("region", { name: "راهنمای تکلیف" }),
    ).toBeVisible();
    await item
      .getByLabel("بازخورد بازبین")
      .fill("شواهد آزمایشی با معیارهای اعلام‌شده بررسی و پذیرفته شد.");
    await item.getByRole("button", { name: "پذیرش تکلیف" }).click();
    await expect(item).toContainText("accepted");
    await page.reload();
    await page
      .getByRole("button", { name: "پیشرفت و تکالیف", exact: true })
      .click();
    await expect(
      page.locator("article").filter({ hasText: marker }),
    ).toContainText("accepted");
    const otherPage = await other.newPage();
    await login(otherPage, credentials["learner-b"]);
    await expect(
      otherPage.getByRole("heading", { name: title, exact: true }),
    ).toHaveCount(0);
    await page.setViewportSize({ width: 320, height: 800 });
    expect(
      await page.evaluate(
        () => document.documentElement.scrollWidth > innerWidth,
      ),
    ).toBe(false);
    expect(errors).toEqual([]);
    expect(await page.evaluate(() => (window as any).__contentCsp)).toEqual([]);
    await testInfo.attach("imported-course-measurements", {
      body: JSON.stringify(
        {
          courseOpenMs,
          courseApiResponseEndMs: response.request().timing().responseEnd,
          lessonCount: course.lessons.length,
          objectiveCount: course.metadata.objectives.length,
          mobileWidth: 320,
          pageErrors: errors,
          scope:
            "One local synthetic Chromium run; measurements are not a load-test or SLO result",
        },
        null,
        2,
      ),
      contentType: "application/json",
    });
  } finally {
    await learner.close();
    await reviewer.close();
    await other.close();
  }
});
