# NIKWAY Learning OS — v2

نمونهٔ فارسی/انگلیسی و RTL/LTR، توسعه‌یافته از HTML موجود؛ بدون backend یا AI واقعی.

## اجرای محلی
نیازمند Node.js 22.22+ و npm.

```sh
npm ci
npm run dev -- --port 18766
```

نسخهٔ buildشده و آفلاین:

```sh
npm run build
npm run preview -- --port 18765
```

آدرس: http://127.0.0.1:18765
برای انتقال خودکار دادهٔ قدیمی همان آدرس و همان مرورگر/پروفایل نسخهٔ قبلی را استفاده کنید. پورت یا hostname دیگر storage مشترک ندارد. کلید قدیمی حذف نمی‌شود.

## آزمون

```sh
npm test
npx playwright install chromium
npm run build
npm run test:e2e
```

Playwright سرور تست مستقل روی پورت 18767 اجرا می‌کند و از contextهای جدا استفاده می‌کند؛ دادهٔ واقعی مرورگر کاربر را reset نمی‌کند. برای دیدن گزارش: `npx playwright show-report evidence/playwright-report`.

## فایل‌ها
- `src/modules/`: شش ماژول مستقل.
- `src/domain/`: schema، قواعد و قراردادها.
- `src/infrastructure/`: Dexie و مربی mock.
- `src/components/`: اجزای مشترک و shadcn/ui.
- `src/data/`، `src/i18n/`، `src/styles/`: محتوای اصلی، زبان و ظاهر.
- `docs/ARCHITECTURE.md`: معماری، migration و محدودیت‌ها.
- `docs/CHANGELOG.md`: تغییرات.
- `evidence/`: خروجی آزمون، build و تصاویر.

نسخهٔ اولیه در پوشهٔ هم‌سطح `../nikway-learning-os` دست‌نخورده باقی مانده است. متن مدل قابلیت گفت‌وگوی اولیه بازیابی نشده بود؛ دامنه بر اساس شش ماژول موجود است.

## منابع فنی
- https://ui.shadcn.com/docs/installation/vite
- https://dexie.org/docs/Dexie/Dexie.transaction()
- https://vite.dev/guide/build

فونت Noto Sans Arabic و مجوز آن از نسخهٔ اولیه منتقل شده‌اند. کد Button و Dialog از رجیستری رسمی shadcn/ui به صورت محلی نصب و برای این محصول تنظیم شده است.
