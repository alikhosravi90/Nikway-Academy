# NIKWAY Learning OS — معماری فازهای ۱ و ۲

## مرز محصول
نسخهٔ ۲ یک محصول محلی با داده‌های نمونه است. بک‌اند، احراز هویت، فراخوانی LLM، اتصال خدمات واقعی، انتشار عمومی و استقرار تولید در این مأموریت انجام نشده‌اند.

## تداوم نسخهٔ قبلی
مبدأ `../nikway-learning-os/index.html` است و دست‌نخورده باقی مانده. رنگ‌ها، فونت Noto، ساختار داشبورد و کارت‌ها از همان نسخه منتقل شده‌اند. `src/styles/legacy.css` استخراج مستقیم سبک قبلی با تبدیل خصوصیات چپ/راست به logical properties است. `src/data/catalog.json` مستقیماً از سه دوره، چهار منبع و شش شایستگی قبلی استخراج شده است. HTML رشته‌ای و رویدادهای inline به JSX و handlerهای React تبدیل شده‌اند؛ محصول جدید از یک قالب متفاوت یا دادهٔ جایگزین ساخته نشده است.

## وابستگی لایه‌ها

```text
app/registry + HashRouter + Shell
  ├─ modules/dashboard
  ├─ modules/academy
  ├─ modules/library
  ├─ modules/tutor
  ├─ modules/competency
  └─ modules/lab
        ↓
components/ (CourseDialog, CourseRow, Modal, Progress, Card, Heading)
        ↓
app/provider (state delivery, command handling, session lifetime)
        ↓
domain/ports → domain/model (Zod, pure state transitions)
        ↑
infrastructure/repository (Dexie transactions)
infrastructure/mock-tutor (prewritten replies)
```

هر ماژول یک entry point مستقل و chunk بارگذاری جدا دارد و مستقیماً از ماژول دیگر import نمی‌کند. ارتباط بین قابلیت‌ها از طریق route و پارامتر URL است. افزودن صفحه در `app/registry.ts` ناوبری و route آن را یکجا ثبت می‌کند. اجزای مشترک خارج از ماژول‌ها هستند.

## قراردادها و منطق
- `LearningPort`: initialize/read/dispatch/exportBackup/importBackup. رابط کاربری از Dexie استفاده مستقیم نمی‌کند. تزریق adapter در `app/services.ts` انجام می‌شود.
- `TutorPort`: دریافت prompt و locale و بازگرداندن پاسخ asynchronous. هیچ نام ارائه‌دهنده، کلید یا SDK مدل در رابط نیست.
- `domain/model.ts`: اعتبارسنجی، تکمیل ترتیبی و idempotent درس، نشان‌کردن، شناسهٔ یکتای تلاش، محاسبه ظرفیت و تحویل، و سطح شایستگی. هیچ DOM، React، fetch یا ذخیره‌سازی در این لایه نیست.
- API-Ready و LLM-Agnostic به معنای وجود مرزهای قابل جایگزینی است، نه اتصال واقعی یا تکمیل طراحی احراز هویت و همگام‌سازی سرور. اضافه‌کردن backend نیازمند قرارداد API، مدیریت conflict و مجوز جداست.

## ماندگاری و مهاجرت
پایگاه IndexedDB با نام `nikway-learning-os-v2`، schema version 1، دارای `states` و `archive` است. رکورد وضعیت `main` با schema داده version 2 ذخیره می‌شود.

۱. اگر رکورد معتبر جدید وجود داشته باشد، همان منبع حقیقت است.
۲. در نبود رکورد، کلید `nikway-demo-v1` از localStorage خوانده و با Zod اعتبارسنجی می‌شود.
۳. نسخهٔ خام قدیمی و رکورد جدید در یک transaction نوشته می‌شوند؛ کلید قدیمی حذف یا بازنویسی نمی‌شود.
۴. نبود کلید یعنی استفاده از seed اولیه؛ دادهٔ خراب یا storage مسدود باعث توقف قابل بازیابی می‌شود، نه reset خودکار.
۵. هر command در read/write transaction اجرا می‌شود؛ هم‌زمانی دو اتصال باعث از دست رفتن تغییرات مستقل نمی‌شود. درس با index و تلاش با شناسه از ثبت تکراری محافظت می‌شوند.
۶. reset و import از وضعیت قبلی نسخهٔ archive نگه می‌دارند. فایل JSON خروجی برای پشتیبان و جابه‌جایی دستی موجود است؛ import هم قالب نسخهٔ ۲ و هم شکل قدیمی را می‌پذیرد. فایل نامعتبر وضعیت فعلی را تغییر نمی‌دهد.

Origin مرورگر اهمیت دارد: `localhost` و `127.0.0.1`، پورت‌های متفاوت و پروفایل‌های مرورگر جداگانه، دادهٔ جدا دارند. پیش‌نمایش نهایی روی origin قدیمی `http://127.0.0.1:18765` اجرا می‌شود تا دادهٔ قبلی همان مرورگر قابل مهاجرت باشد. هیچ راهی برای مهاجرت خودکار دادهٔ origin یا پروفایل دیگر وجود ندارد؛ برای آن‌ها فایل پشتیبان باید منتقل شود. برنامه دادهٔ localStorage هر origin را خودکار یک‌بار منتقل می‌کند.

پیام‌های مربی و وضعیت مرحلهٔ شبیه‌سازی session-only هستند و هنگام رفت‌وبرگشت بین ماژول‌ها حفظ می‌شوند؛ با reload پاک می‌شوند. شمار تلاش، درس‌ها و نشان‌ها ماندگار هستند. زبان انتخاب‌شده در کلید جداگانه ذخیره می‌شود.

## آفلاین و قابلیت حمل
Vite PWA/Workbox همه chunkهای صفحه، CSS، HTML و فونت را پس از اولین بارگذاری آنلاین در service worker precache می‌کند. IndexedDB مستقل از شبکه کار می‌کند. اولین بازدید بدون دریافت فایل‌ها ممکن نیست. HTTPS یا localhost لازم است؛ پاک‌کردن داده‌های سایت/eviction مرورگر می‌تواند داده و cache را حذف کند. وضعیت آمادگی آفلاین در footer نمایش داده می‌شود. آپدیت service worker با انتخاب کاربر reload می‌شود و خودکار جلسهٔ فعال را قطع نمی‌کند.

`base: './'` و HashRouter امکان سرو از زیرپوشه را بدون rewrite سرور فراهم می‌کنند. اجرای مستقیم dist/index.html با file:// مسیر پشتیبانی‌شده نیست؛ یک static server محلی لازم است. همه فونت‌ها و دارایی‌های رابط محلی هستند.

## رابط و دسترس‌پذیری
Tailwind CSS v4 به همراه CSS اصلی؛ Button و Dialog رسمی shadcn/ui از CLI در سورس نگهداری می‌شوند. helper ادغام کلاس محلی است و طراحی رنگ/فاصله با هویت قبلی هماهنگ شده. Dialog مبتنی بر Radix: focus trap، Escape و عنوان/توضیح دسترس‌پذیر. nav با aria-current، دکمهٔ فیلتر با aria-pressed، فرم با label، progressbar، log زنده، skip link و reduced-motion ارائه شده‌اند.

I18n provider زبان فارسی/انگلیسی و اعداد locale-aware را ارائه می‌کند. کاتالوگ محتوای آموزشی جداست؛ متن‌های UI به صورت جفت‌های فارسی/انگلیسی از تابع t عبور می‌کنند. جهت document و modal مطابق زبان تغییر می‌کند؛ layout با logical CSS در RTL/LTR کار می‌کند. ترجمه‌ها نمونه‌اند و بازبینی حرفه‌ای زبانی نشده‌اند.

## آزمون‌ها
Vitest: قواعد domain، ورودی نامعتبر، migration، idempotency، هم‌زمانی، import/export و reset. از Dexie واقعی روی fake-indexeddb در آزمون سریع استفاده می‌شود؛ آزمون مرورگر نیز IndexedDB واقعی را اجرا می‌کند.
Playwright: شش ماژول، ماندگاری بعد از reload، منابع و جست‌وجو، مربی mock و متن تزریقی، مسیرهای شبیه‌سازی، RTL/LTR موبایل، آفلاین، دادهٔ خراب، reset، ورودی/خروجی و خطاهای runtime/network. خروجی واقعی و شواهد در `evidence/` قرار دارند.
