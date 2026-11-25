import { it, expect } from "vitest";
import { MockTutor } from "../src/infrastructure/mock-tutor";
const tutor = new MockTutor();
it("answers the three supported topics and acknowledges unknowns", async () => {
  expect(await tutor.reply("سیستم و بازخورد", "fa")).toContain("ارتباط اجزا");
  expect(await tutor.reply("تحول دیجیتال", "fa")).toContain("قابل اندازه‌گیری");
  expect(await tutor.reply("گلوگاه", "fa")).toContain("کمترین ظرفیت");
  expect(await tutor.reply("astronomy", "en")).toContain("only");
});
it("rejects blank and oversized prompts at the adapter boundary", async () => {
  await expect(tutor.reply("  ", "fa")).rejects.toThrow();
  await expect(tutor.reply("a".repeat(601), "en")).rejects.toThrow();
});
