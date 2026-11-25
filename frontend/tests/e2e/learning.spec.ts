import { test, expect, Page } from "@playwright/test";
import { readFileSync, existsSync } from "node:fs";
const credentialPath =
  process.env.E2E_CREDENTIALS_FILE || "../infra/runtime/credentials.json";
const credentials = existsSync(credentialPath)
  ? JSON.parse(readFileSync(credentialPath, "utf8"))
  : {};
const learner =
  process.env.E2E_LEARNER_USERNAME || credentials["learner-a"]?.username;
const password =
  process.env.E2E_LEARNER_PASSWORD || credentials["learner-a"]?.password;
async function login(page: Page, user: string, pass: string) {
  await page.goto("/");
  await page.getByRole("button", { name: "ورود به آکادمی" }).click();
  await page.locator("#username").fill(user);
  await page.locator("#password").fill(pass);
  await page.locator("#kc-login").click();
  await expect(
    page.getByRole("navigation", { name: "ناوبری اصلی" }),
  ).toBeVisible();
}
test("real learner enrolls, persists completion, submits work, and signs out", async ({
  page,
}) => {
  test.skip(
    !learner || !password,
    "Supply runtime learner credentials; no fabricated auth or API responses.",
  );
  await login(page, learner!, password!);
  await page.getByRole("button", { name: "مشاهده دوره" }).first().click();
  const enroll = page.getByRole("button", {
    name: "ثبت‌نام در دوره",
    exact: true,
  });
  if (await enroll.isVisible()) await enroll.click();
  await expect(
    page.getByRole("heading", { name: "ارسال تکلیف" }),
  ).toBeVisible();
  const next = page
    .getByRole("button", { name: "ثبت تکمیل درس", exact: true })
    .first();
  while (await next.count()) {
    await next.click();
    await expect(page.getByRole("status")).toContainText("با موفقیت ثبت شد");
  }
  await expect(
    page.getByRole("button", { name: "تکمیل شده", exact: true }).first(),
  ).toBeDisabled();
  await page.reload();
  await page.getByRole("button", { name: "مشاهده دوره" }).first().click();
  await expect(
    page.getByRole("button", { name: "تکمیل شده", exact: true }).first(),
  ).toBeDisabled();
  const submission = `E2E learning evidence ${Date.now()}`;
  await page.getByLabel("متن پاسخ و شواهد تمرین").fill(submission);
  await page.getByRole("button", { name: "ارسال برای بازبینی" }).click();
  await expect(page.getByRole("status")).toContainText("با موفقیت ثبت شد");
  await page
    .getByRole("button", { name: "پیشرفت و تکالیف", exact: true })
    .click();
  await expect(page.getByText(submission, { exact: true })).toBeVisible();
  await expect(
    page.getByRole("button", { name: "بازبینی تکالیف", exact: true }),
  ).toHaveCount(0);
  await page.getByRole("button", { name: "خروج", exact: true }).click();
  await expect(
    page.getByRole("button", { name: "ورود به آکادمی" }),
  ).toBeVisible();
  expect(
    await page.evaluate(() =>
      Object.keys(localStorage).some((k) => /token/i.test(k)),
    ),
  ).toBe(false);
});
test("real reviewer supplies feedback and requests revision", async ({
  page,
}) => {
  const user =
      process.env.E2E_REVIEWER_USERNAME || credentials["reviewer-a"]?.username,
    pass =
      process.env.E2E_REVIEWER_PASSWORD || credentials["reviewer-a"]?.password;
  test.skip(!user || !pass, "Supply runtime reviewer credentials.");
  await login(page, user!, pass!);
  await page
    .getByRole("button", { name: "بازبینی تکالیف", exact: true })
    .click();
  const item = page
    .locator("article")
    .filter({ hasText: "E2E learning evidence" })
    .first();
  await expect(item).toBeVisible();
  await item
    .getByLabel("بازخورد بازبین")
    .fill("Please add a concrete verification receipt.");
  await item.getByRole("button", { name: "درخواست اصلاح" }).click();
  await expect(page.getByRole("status")).toContainText("با موفقیت ثبت شد");
  await expect(item).toContainText("revision_requested");
});

test("API rejects anonymous, forged, learner review and cross-tenant access", async ({
  browser,
  request,
}) => {
  const other = credentials["learner-b"];
  test.skip(
    !learner || !password || !other,
    "Supply both tenant credentials for real OIDC isolation test.",
  );
  expect((await request.get("/api/me")).status()).toBe(401);
  expect(
    (
      await request.get("/api/me", {
        headers: { Authorization: "Bearer forged.invalid.token" },
      })
    ).status(),
  ).toBe(401);
  const ctxA = await browser.newContext(),
    ctxB = await browser.newContext();
  try {
    const pageA = await ctxA.newPage();
    const reqA = pageA.waitForRequest((r) => r.url().endsWith("/api/me"));
    await login(pageA, learner!, password!);
    const headersA = { Authorization: (await reqA).headers()["authorization"] };
    const pageB = await ctxB.newPage();
    const reqB = pageB.waitForRequest((r) => r.url().endsWith("/api/me"));
    await login(pageB, other.username, other.password);
    const headersB = { Authorization: (await reqB).headers()["authorization"] };
    const meA = await (
        await request.get("/api/me", { headers: headersA })
      ).json(),
      meB = await (await request.get("/api/me", { headers: headersB })).json();
    expect(meA.tenant_id).not.toBe(meB.tenant_id);
    const own = await (
      await request.get("/api/submissions", { headers: headersA })
    ).json();
    expect(own.every((s: { subject: string }) => s.subject === meA.sub)).toBe(
      true,
    );
    const courses = await (
      await request.get("/api/courses", { headers: headersA })
    ).json();
    expect(courses.length).toBeGreaterThan(0);
    const denied = await request.post(`/api/courses/${courses[0].id}/enroll`, {
      headers: headersB,
      data: {},
    });
    expect([403, 404]).toContain(denied.status());
    await request.post(`/api/courses/${courses[0].id}/enroll`, {
      headers: headersA,
      data: {},
    });
    for (const lesson of courses[0].lessons) {
      const complete = await request.post(
        `/api/courses/${courses[0].id}/lessons/${lesson.id}/complete`,
        { headers: headersA, data: {} },
      );
      expect(complete.ok()).toBeTruthy();
    }
    const sub = await request.post(
      `/api/courses/${courses[0].id}/submissions`,
      { headers: headersA, data: { content: "E2E tenant isolation evidence" } },
    );
    expect(sub.ok()).toBeTruthy();
    const submission = await sub.json();
    const deniedReview = await request.post(
      `/api/submissions/${submission.id}/review`,
      {
        headers: headersA,
        data: { decision: "accepted", feedback: "Unauthorized learner review" },
      },
    );
    expect(deniedReview.status()).toBe(403);
    const progressB = await (
      await request.get("/api/progress", { headers: headersB })
    ).json();
    expect(
      progressB.submissions.some((s: { id: string }) => s.id === submission.id),
    ).toBe(false);
  } finally {
    await ctxA.close();
    await ctxB.close();
  }
});
