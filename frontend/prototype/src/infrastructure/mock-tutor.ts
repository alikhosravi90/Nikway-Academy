import { z } from "zod";
import type { TutorPort } from "../domain/ports";
export class MockTutor implements TutorPort {
  async reply(input: string, locale: "fa" | "en") {
    const prompt = z.string().trim().min(1).max(600).parse(input);
    if (/سیستم|بازخورد|system|feedback/i.test(prompt))
      return locale === "fa"
        ? "در تفکر سیستمی، به ارتباط اجزا و الگوی رفتار در طول زمان نگاه می‌کنیم. مثال: افزایش سفارش اضطراری می‌تواند برنامهٔ تولید را مختل کند و تأخیر بیشتری بسازد. تمرین: دو متغیر و جهت اثر آن‌ها را نام ببرید. منبع نمونه: راهنمای حلقه‌های بازخورد در کتابخانه."
        : "Systems thinking examines relationships and behavior over time. Emergency orders can disrupt schedules and create more delays. Name two variables and their influence. Sample source: Feedback loops guide.";
    if (/تحول|دیجیتال|digital|transform/i.test(prompt))
      return locale === "fa"
        ? "از یک مسئلهٔ قابل اندازه‌گیری شروع کنید: مثلاً کاهش زمان پاسخ‌گویی. سپس وضعیت موجود، نتیجهٔ هدف و یک آزمایش کوچک را تعریف کنید. ابزار دیجیتال را پس از روشن شدن مسئله انتخاب کنید. منبع نمونه: بوم نقشهٔ راه تحول دیجیتال."
        : "Start with a measurable problem, define the current state and desired outcome, then design a small experiment. Choose technology after clarifying the problem. Sample source: Digital transformation canvas.";
    if (/گلوگاه|ناب|مسئله|bottleneck|lean|problem/i.test(prompt))
      return locale === "fa"
        ? "ظرفیت مراحل را مقایسه کنید؛ مرحله با کمترین ظرفیت می‌تواند خروجی کل جریان را محدود کند. افزایش ظرفیت مرحلهٔ غیرگلوگاهی لزوماً خروجی را بیشتر نمی‌کند. این موضوع را در آزمایشگاه تولید امتحان کنید."
        : "Compare stage capacities. The slowest stage limits throughput; improving other stages may not help. Try this in the simulation lab.";
    return locale === "fa"
      ? "برای این پرسش پاسخ اختصاصی ندارم؛ این نسخه فقط سه پاسخ نمونه دربارهٔ تفکر سیستمی، تحول دیجیتال و گلوگاه تولید دارد. یکی از این موضوع‌ها را انتخاب کنید."
      : "This mock supports systems thinking, digital transformation, and bottlenecks only. Please choose one of these topics.";
  }
}
