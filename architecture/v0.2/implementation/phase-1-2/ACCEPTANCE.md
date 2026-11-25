> ثبت این گزارش، شاهد اجرای محلی قبلی است؛ CI این مخزن نیست. تصاویر و گزارش HTML فقط در بستهٔ محلی هستند؛ خروجی JSON و لاگ‌ها همراه این ثبت منتشر می‌شوند.

# گزارش پذیرش فازهای ۱ و ۲

**وضعیت نهایی: PASS — در محدودهٔ محصول محلی و نمونهٔ نمایشی.**

تاریخ: ۲۵ نوامبر ۲۰۲۶. پیش‌نمایش: http://127.0.0.1:18765/?v=2#/dashboard

| معیار | نتیجه | شاهد |
|---|---|---|
| ثبت وضعیت موجود و حفظ نسخهٔ اولیه | PASS | `evidence/baseline.json` و `baseline-sha256.txt`؛ hash فایل HTML و فونت اولیه بعد از توسعه بدون تغییر |
| بازآرایی ماژولار و جداسازی داده، منطق و UI | PASS | `src/domain`، `data`، `infrastructure`، `components` و شش entry در `modules`؛ شرح در ARCHITECTURE.md |
| فناوری‌های درخواست‌شده | PASS | React، TypeScript strict، Vite، Tailwind، shadcn/ui، React Router، Zod، Dexie/IndexedDB، Vitest و Playwright؛ نسخه‌ها در dependencies.txt و package-lock.json |
| عملکرد شش ماژول | PASS | ۱۲ آزمون Playwright، گزارش HTML/JSON و تصاویر شش صفحه |
| حفظ قابلیت‌های قبلی | PASS | دوره و پیشرفت، جست‌وجو و فیلتر، مطالعه و نشان، مربی mock، نقشه و شواهد، شبیه‌سازی و بازخورد، reset؛ chat و مرحلهٔ lab در ناوبری حفظ می‌شوند |
| انتقال دادهٔ محلی موجود | PASS | آزمون legacy با [5,2,1] و sim=7؛ همچنین مشاهدهٔ دادهٔ واقعی مرورگر متصل [3,1,0] قبل/بعد، با حفظ کلید قدیمی؛ live-migration.json |
| آفلاین | PASS | reload با network offline و ناوبری شش ماژول؛ تست مستقل آفلاین در زیرپوشه |
| RTL/LTR و Responsive | PASS | فارسی/انگلیسی، ماندگاری زبان، عرض ۳۲۰ و ۳۹۰ بدون overflow، بررسی dialog و تصاویر desktop/mobile |
| Build و TypeScript | PASS | `evidence/build.log`؛ خروجی موفق، بدون هشدار chunk بزرگ پس از تفکیک vendorها |
| آزمون منطق و persistence | PASS | ۲۴ آزمون Vitest؛ `unit-green.log` |
| قابل حمل | PASS | static server روی زیرپوشه، لینک hash قدیمی و reload آفلاین؛ `portability.json` |
| مستندات و شواهد | PASS | README، ARCHITECTURE، CHANGELOG، این گزارش و evidence |
| بررسی وابستگی‌ها | PASS محدود | npm audit: صفر vulnerability گزارش‌شده در زمان اجرا؛ تضمین امنیت جامع نیست |

## شواهد اجرای نهایی

- Vitest: ۳ فایل، ۲۴ آزمون موفق؛ حدود ۵۵۷ میلی‌ثانیه روی این ماشین.
- Playwright: ۱۲ آزمون موفق؛ ۱۲٫۰ ثانیه روی Chromium نصب‌شده برای Playwright.
- Build: خروجی Vite موفق؛ chunk اصلی حدود ۹۶٫۵۵ KB خام، React runtime حدود ۲۵۰٫۶۹ KB و data core حدود ۱۹۵٫۱۴ KB؛ مجموع precache حدود ۸۲۹٫۵۶ KiB شامل فونت و ماژول‌ها.
- مسیرهای آزمون شامل دادهٔ خراب، ورودی ناشناخته، ثبت تکراری درس/تلاش، تغییر هم‌زمان دو اتصال، export/import، reload، reset و متن HTML در چت هستند.
- `unit-red.log` و `e2e-red.log` شکست‌های مرحلهٔ ابتدایی قبل از تکمیل پیاده‌سازی را نگه می‌دارند. `e2e-before-mobile-fix.log` ایراد کشف‌شده در Grid موبایل را ثبت می‌کند. خروجی نهایی در `unit-green.log`، `e2e.log` و `playwright-results.json` است.

## رفع نقص و آزمون مجدد

۱. گزینهٔ منسوخ baseUrl در TypeScript حذف و paths نسبی استفاده شد.
۲. مرورگر Chromium مطابق نسخهٔ Playwright نصب شد.
۳. عرض intrinsic فرم مربی باعث overflow موبایل بود؛ ستون‌های minmax(0,1fr) و حداقل عرض مناسب آیتم‌ها/ورودی اصلاح شدند.
۴. تست reload بعد از تکمیل درس باید منتظر پایان transaction و بسته‌شدن modal می‌ماند؛ شرط observable موفقیت اضافه شد تا نتیجهٔ ذخیره با زمان‌بندی کلیک اشتباه نشود.
۵. وابستگی‌های ابزار ساخت که audit متوسط داشتند به نسخهٔ اصلاح‌شده override شدند؛ build و کل suite پس از تغییر دوباره موفق شدند.
۶. chunk مشترک بزرگ به runtime و data-core تفکیک شد و build و suite دوباره اجرا شدند.
۷. مرورگر در آدرس اصلی HTML قدیمی را از cache نشان می‌داد؛ query نسخه (?v=2) برای اولین بازدید جدید استفاده شد. Origin تغییر نکرد و migration واقعی تأیید شد.

## حدود اعتبار نتیجه

- PASS مربوط به فازهای ۱ و ۲ و اجرای محلی است؛ backend، API واقعی، LLM واقعی، احراز هویت، sync ابری و انتشار تولید پیاده نشده‌اند.
- API-Ready و LLM-Agnostic با قرارداد و adapter جدا فراهم شده‌اند؛ صحت اتصال به سرویس آینده هنوز موضوع آزمون نیست.
- آزمون مرورگر در Chromium انجام شده؛ Firefox/Safari و دستگاه فیزیکی در این مأموریت آزمون نشده‌اند. ممیزی کامل WCAG و تست بار انجام نشده است.
- آفلاین بعد از دریافت موفق دارایی‌ها فعال می‌شود. دادهٔ هر origin/profile مستقل است؛ انتقال پروفایل دیگر نیازمند فایل خروجی/ورودی است. دادهٔ قدیمی حذف نشده است.
- مدل قابلیت گفت‌وگوی اولیه در دسترس نبود؛ معماری و رفتار از کد فعلی و شش قابلیت تعریف‌شده حفظ شده‌اند.
