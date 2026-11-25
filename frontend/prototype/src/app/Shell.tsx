import { Suspense, useState, useEffect, useRef } from "react";
import { NavLink, Link, Outlet, useLocation } from "react-router-dom";
import { useI18n } from "../i18n/provider";
import { useLearning, download } from "./provider";
import { services } from "./services";
import { modules } from "./registry";
import { useOffline } from "./offline";
import { Button } from "../components/ui/button";
import { Modal } from "../components/shared";
export function Shell() {
  const { t, locale, setLocale } = useI18n(),
    { act, pending, notice, setError } = useLearning();
  const [reset, setReset] = useState(false);
  const file = useRef<HTMLInputElement>(null);
  const { pathname } = useLocation(),
    offline = useOffline();
  const current = modules.find((m) => pathname === `/${m.id}`) ?? modules[0];
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);
  return (
    <>
      <a className="skip-link" href="#main-content">
        {t("رفتن به محتوا", "Skip to content")}
      </a>
      <aside className="sidebar">
        <Link className="brand" to="/dashboard" dir="ltr">
          <b>↗</b>NIKWAY
        </Link>
        <div className="brand-sub muted">
          {t(
            "سیستم‌عامل یادگیری و رشد",
            "Learning and growth operating system",
          )}
        </div>
        <div className="muted sidebar-caption">
          {t("فضای یادگیری شما", "Your learning space")}
        </div>
        <nav aria-label={t("ناوبری اصلی", "Main navigation")}>
          {modules.map((m) => (
            <NavLink key={m.id} to={`/${m.id}`}>
              <span aria-hidden>{m.icon}</span>
              {t(m.name[0], m.name[1])}
            </NavLink>
          ))}
        </nav>
        <div className="side-bottom">
          <span className="avatar">{t("م‌خ", "MK")}</span>
          <strong className="small">
            {t("یادگیرنده آزمایشی", "Synthetic Learner")}
          </strong>
          <p className="muted">
            {t("مسیر: مشاور تحول سازمانی", "Path: Transformation consultant")}
          </p>
          <Button variant="outline" size="sm" onClick={() => setReset(true)}>
            {t("بازنشانی نمونه", "Reset demo")}
          </Button>
        </div>
      </aside>
      <main id="main-content" tabIndex={-1}>
        <header>
          <span>
            {t("فضای شخصی", "Personal space")} /{" "}
            {t(current.name[0], current.name[1])}
          </span>
          <div className="header-actions">
            <span className="pill">
              {t("نسخهٔ نمایشی • داده‌های نمونه", "Prototype • Sample data")}
            </span>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setLocale(locale === "fa" ? "en" : "fa")}
            >
              {locale === "fa" ? "English" : "فارسی"}
            </Button>
          </div>
        </header>
        <div className="content">
          <Suspense
            fallback={<p role="status">{t("در حال بارگذاری…", "Loading…")}</p>}
          >
            <Outlet />
          </Suspense>
          <footer>
            <div>
              NIKWAY Learning OS —{" "}
              {t(
                "نمونهٔ تعاملی • داده‌ها فقط در همین مرورگر نگهداری می‌شوند.",
                "Interactive prototype • Data stays in this browser.",
              )}
            </div>
            <div className="footer-tools">
              <span data-testid="offline-status">
                {offline.ready
                  ? t("آمادهٔ استفاده آفلاین", "Ready for offline use")
                  : offline.failed
                    ? t(
                        "ذخیرهٔ آفلاین در این مرورگر در دسترس نیست",
                        "Offline caching unavailable in this browser",
                      )
                    : t(
                        "در حال آماده‌سازی آفلاین…",
                        "Preparing offline cache…",
                      )}
              </span>
              {offline.update && (
                <Button size="sm" variant="outline" onClick={offline.update}>
                  {t(
                    "نسخهٔ جدید آماده است؛ بارگذاری",
                    "Update available; reload",
                  )}
                </Button>
              )}
              <Button
                size="sm"
                variant="ghost"
                onClick={async () => {
                  try {
                    download(
                      await services.learning.exportBackup(),
                      "nikway-learning-backup.json",
                    );
                  } catch {
                    setError(
                      t("خروجی داده‌ها آماده نشد.", "Could not export data."),
                    );
                  }
                }}
              >
                {t("خروجی داده‌ها", "Export data")}
              </Button>
              <Button
                size="sm"
                variant="ghost"
                onClick={() => file.current?.click()}
              >
                {t("ورود فایل پشتیبان", "Import backup")}
              </Button>
              <input
                ref={file}
                className="sr-only"
                type="file"
                aria-label={t("ورود داده‌ها", "Import data")}
                accept=".json"
                onChange={async (e) => {
                  const f = e.target.files?.[0];
                  if (!f) return;
                  try {
                    if (f.size > 1_000_000) throw Error("File too large");
                    await services.learning.importBackup(await f.text());
                    setError("");
                    notice(
                      t(
                        "داده‌ها با موفقیت وارد شدند",
                        "Data imported successfully",
                      ),
                    );
                  } catch {
                    setError(
                      t(
                        "فایل نامعتبر است؛ داده‌های فعلی تغییر نکردند.",
                        "Invalid file. Current data is unchanged.",
                      ),
                    );
                  } finally {
                    e.target.value = "";
                  }
                }}
              />
            </div>
          </footer>
        </div>
      </main>
      <Modal
        open={reset}
        onClose={() => setReset(false)}
        title={t("بازنشانی دادهٔ نمایشی", "Reset sample data")}
        description={t(
          "پیشرفت، نشان‌ها و تعداد تمرین‌ها به وضعیت اولیه برمی‌گردند. نسخهٔ قبلی برای بازیابی در پایگاه محلی نگهداری می‌شود.",
          "Progress, bookmarks and attempt count return to defaults. A recovery copy is kept in the local database.",
        )}
      >
        <div className="filters">
          <Button
            disabled={pending}
            onClick={async () => {
              if (await act({ type: "reset" })) {
                setReset(false);
                notice(t("داده‌های نمایشی بازنشانی شدند", "Sample data reset"));
              }
            }}
          >
            {t("تأیید بازنشانی", "Confirm reset")}
          </Button>
          <Button variant="outline" onClick={() => setReset(false)}>
            {t("انصراف", "Cancel")}
          </Button>
        </div>
      </Modal>
    </>
  );
}
