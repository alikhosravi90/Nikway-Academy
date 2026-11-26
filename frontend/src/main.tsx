import { useState, useEffect, useRef } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard,
  BookOpen,
  GraduationCap,
  Route,
  Bot,
  ClipboardCheck,
  FolderKanban,
  Library,
  UserRound,
  ShieldCheck,
  CalendarDays,
  LogOut,
  Sun,
  Moon,
  Menu,
  X,
  Search,
  ArrowUpLeft,
  ArrowUpRight,
  RefreshCw,
  ExternalLink,
  Sparkles,
  Layers,
  Check,
  LockKeyhole,
  WifiOff,
} from "lucide-react";
import "@fontsource-variable/vazirmatn";
import { auth, api } from "./api";
import {
  Card,
  Badge,
  Button,
  Progress,
  Empty,
  PageHeading,
  CourseCard,
  CompletionIcon,
} from "./components/ui";
import { LearningWorkspace, Submissions } from "./learning";
import {
  completion,
  readPreferences,
  safeMoodleUrl,
  type Course,
  type Identity,
  type Submission,
  type Workshop,
  type MoodleOverview,
  type PageId,
  type Preferences,
} from "./model";
import "./design.css";
const screens: [PageId, string, string, typeof BookOpen][] = [
  ["dashboard", "داشبورد", "Dashboard", LayoutDashboard],
  ["courses", "دوره‌ها", "Course catalog", BookOpen],
  ["workspace", "فضای یادگیری", "Learning workspace", GraduationCap],
  ["path", "مسیر یادگیری", "Learning path", Route],
  ["services", "مربی هوشمند", "AI tutor", Bot],
  ["progress", "پیشرفت و تکالیف", "Assessment", ClipboardCheck],
  ["projects", "پروژه‌ها", "Projects", FolderKanban],
  ["library", "کتابخانه", "Knowledge library", Library],
  ["workshops", "کارگاه‌ها", "Workshops", CalendarDays],
  ["profile", "پروفایل", "Profile", UserRound],
  ["admin", "مدیریت", "Administration", ShieldCheck],
];
const capabilitiesLabels: Record<string, [string, string]> = {
  authentication: ["ورود به حساب", "Authentication"],
  learning: ["یادگیری", "Learning"],
  workshops: ["کارگاه‌ها", "Workshops"],
  videoconferencing: ["جلسه آنلاین", "Video meetings"],
  ai_provider: ["مربی هوشمند", "AI provider"],
  mcp: ["اتصال ابزارهای بیرونی", "MCP"],
  tools: ["ابزارهای یادگیری", "Learning tools"],
  credentials: ["گواهی یادگیری", "Credentials"],
};
const stateLabels: Record<string, [string, string]> = {
  operational: ["فعال", "Operational"],
  registration_only: [
    "فقط ثبت‌نام؛ جلسه آنلاین متصل نیست",
    "Registration only; video not connected",
  ],
  not_integrated: ["متصل نشده", "Not connected"],
  disabled: ["غیرفعال", "Disabled"],
  read_only_progress: ["مشاهده پیشرفت", "Read-only progress"],
  not_issued: ["صادر نمی‌شود", "Not issued"],
};
function App() {
  const [preferences, setPreferences] = useState<Preferences>(readPreferences),
    [ready, setReady] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [page, setPage] = useState<PageId>("dashboard"),
    [navOpen, setNavOpen] = useState(false);
  const [assignmentDrafts, setAssignmentDrafts] = useState<
    Record<string, string>
  >({});
  const [feedbackDrafts, setFeedbackDrafts] = useState<Record<string, string>>(
    {},
  );
  const [me, setMe] = useState<Identity | null>(null),
    [courses, setCourses] = useState<Course[]>([]),
    [submissions, setSubmissions] = useState<Submission[]>([]),
    [workshops, setWorkshops] = useState<Workshop[]>([]),
    [capabilities, setCapabilities] = useState<Record<string, string>>({});
  const [moodle, setMoodle] = useState<MoodleOverview>({ enabled: false }),
    [moodleError, setMoodleError] = useState(""),
    [selected, setSelected] = useState<string | null>(null),
    [notice, setNotice] = useState(""),
    [query, setQuery] = useState(""),
    [filter, setFilter] = useState("all"),
    [online, setOnline] = useState(navigator.onLine);
  const mainRef = useRef<HTMLElement>(null);
  const en = preferences.locale === "en";
  const t = (fa: string, eng: string) => (en ? eng : fa);
  const Arrow = en ? ArrowUpRight : ArrowUpLeft;
  const reviewer = me?.role === "reviewer" || me?.role === "admin";
  const course = courses.find((c) => c.id === selected);
  const enrolled = courses.filter((c) => c.enrolled);
  const totalDone = courses.reduce((s, c) => s + c.completed_lessons.length, 0);
  const nextCourse =
    enrolled.find((c) => completion(c) < 100) || enrolled[0] || courses[0];
  useEffect(() => {
    const d = document.documentElement;
    d.dir = en ? "ltr" : "rtl";
    d.lang = preferences.locale;
    d.dataset.theme = preferences.theme;
    d.dataset.variant = preferences.variant;
    d.dataset.solid = String(preferences.solid);
    d.dataset.quiet = String(preferences.quiet);
    try {
      localStorage.setItem("nikway-preferences", JSON.stringify(preferences));
    } catch {}
  }, [preferences, en]);
  useEffect(() => {
    if (!navOpen) return;
    const panel = document.getElementById("side-panel");
    const controls = () =>
      Array.from(
        panel?.querySelectorAll<HTMLElement>(
          "button:not(:disabled), a[href]",
        ) || [],
      ).filter((node) => node.getClientRects().length > 0);
    const desktop = window.matchMedia("(min-width: 900px)");
    const closeAtDesktop = () => {
      if (!desktop.matches) return;
      setNavOpen(false);
      requestAnimationFrame(() => mainRef.current?.focus());
    };
    if (desktop.matches) {
      closeAtDesktop();
      return;
    }
    desktop.addEventListener("change", closeAtDesktop);
    controls()[0]?.focus();
    const handler = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setNavOpen(false);
        requestAnimationFrame(() =>
          document.getElementById("menu-toggle")?.focus(),
        );
      }
      if (event.key === "Tab") {
        const nodes = controls(),
          first = nodes[0],
          last = nodes[nodes.length - 1];
        if (event.shiftKey && document.activeElement === first) {
          event.preventDefault();
          last?.focus();
        } else if (!event.shiftKey && document.activeElement === last) {
          event.preventDefault();
          first?.focus();
        }
      }
    };
    document.addEventListener("keydown", handler);
    return () => {
      document.removeEventListener("keydown", handler);
      desktop.removeEventListener("change", closeAtDesktop);
    };
  }, [navOpen]);
  useEffect(() => {
    const yes = () => setOnline(true),
      no = () => setOnline(false);
    window.addEventListener("online", yes);
    window.addEventListener("offline", no);
    return () => {
      window.removeEventListener("online", yes);
      window.removeEventListener("offline", no);
    };
  }, []);
  const loadMoodle = async () => {
    try {
      const result = await api<MoodleOverview>("/integrations/moodle/overview");
      setMoodle(result);
      setMoodleError("");
    } catch {
      setMoodleError(
        t(
          "دریافت داده Moodle ممکن نشد. می‌توانید مستقیماً وارد Moodle شوید.",
          "Moodle data is unavailable. You can still open Moodle directly.",
        ),
      );
    }
  };
  const refresh = async () => {
    const identity = await api<Identity>("/me");
    setMe(identity);
    const [c, p, w, cap, lms] = await Promise.all([
      api<Course[]>("/courses"),
      api<{ submissions: Submission[] }>("/progress"),
      api<Workshop[]>("/workshops"),
      api<Record<string, string>>("/capabilities"),
      api<MoodleOverview>("/integrations/moodle"),
    ]);
    setCourses(c);
    setWorkshops(w);
    setCapabilities(cap);
    setMoodle(lms);
    setSubmissions(
      identity.role === "reviewer" || identity.role === "admin"
        ? await api<Submission[]>("/submissions")
        : p.submissions || [],
    );
    await loadMoodle();
  };
  useEffect(() => {
    auth
      .init({
        onLoad: "check-sso",
        pkceMethod: "S256",
        checkLoginIframe: false,
      })
      .then(async (logged) => {
        if (logged) await refresh();
        setReady(true);
      })
      .catch((e) => {
        setError(String(e));
        setReady(true);
      });
  }, []);
  async function act(fn: () => Promise<unknown>) {
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await fn();
      await refresh();
      setNotice(t("با موفقیت ثبت شد", "Saved successfully"));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  const navigate = (id: PageId) => {
    setPage(id);
    setNavOpen(false);
    setQuery("");
    setNotice("");
    requestAnimationFrame(() => mainRef.current?.focus());
    window.scrollTo({ top: 0, behavior: "instant" });
  };
  const open = (c: Course) => {
    setSelected(c.id);
    navigate("workspace");
  };
  const moodleBase = safeMoodleUrl(moodle.url, moodle.url);
  const visibleCourses = courses.filter(
    (c) =>
      (filter !== "enrolled" || c.enrolled) &&
      `${c.title} ${c.description}`
        .toLocaleLowerCase()
        .includes(query.toLocaleLowerCase()),
  );
  const PreferenceControls = (
    <div className="utility-actions">
      <Button
        variant="ghost"
        size="icon"
        aria-label={t("تغییر پوسته", "Toggle theme")}
        onClick={() =>
          setPreferences({
            ...preferences,
            theme: preferences.theme === "light" ? "dark" : "light",
          })
        }
      >
        {preferences.theme === "light" ? (
          <Moon aria-hidden="true" />
        ) : (
          <Sun aria-hidden="true" />
        )}
      </Button>
      <Button
        variant="ghost"
        className="locale-toggle"
        onClick={() =>
          setPreferences({ ...preferences, locale: en ? "fa" : "en" })
        }
      >
        {en ? "فارسی" : "English"}
      </Button>
    </div>
  );
  if (!ready)
    return (
      <main className="boot" aria-busy="true">
        <span className="brand-symbol">N</span>
        <p>{t("در حال اتصال به آکادمی…", "Connecting to your academy…")}</p>
      </main>
    );
  if (!auth.authenticated)
    return (
      <main className="welcome">
        <header>
          <div className="brand">
            <span className="brand-symbol">N</span>
            <span>
              NIKWAY <small>ACADEMY</small>
            </span>
          </div>
          {PreferenceControls}
        </header>
        <div className="welcome-grid">
          <section>
            <p className="eyebrow">A LITTLE LEARNING. A REAL DIFFERENCE.</p>
            <h1>
              {t(
                "جای کوچک امروز، برای رشد بزرگ فردا.",
                "A little space today. A bigger possibility tomorrow.",
              )}
            </h1>
            <p>
              {t(
                "یاد بگیرید، تجربه کنید و با بازخورد بهتر شوید. همه چیز برای قدم بعدی شما، در یک فضای آرام.",
                "Learn, put it into practice, and grow with feedback. Everything for your next step, in one calm space.",
              )}
            </p>
            {error && (
              <p role="alert" className="error-banner">
                {error}
              </p>
            )}
            <Button
              className="primary-cta"
              onClick={() =>
                auth.login({ redirectUri: window.location.origin + "/" })
              }
            >
              {t("ورود به آکادمی", "Sign in to Academy")}
              <Arrow aria-hidden="true" />
            </Button>
            <p className="muted small">
              <LockKeyhole size={15} aria-hidden="true" />{" "}
              {t(
                "ورود با حساب سازمانی • محیط محلی",
                "Organization sign-in · Local workspace",
              )}
            </p>
          </section>
          <div className="welcome-art" aria-hidden="true">
            <div className="art-orbit" />
            <span className="art-tile tile-one">
              <BookOpen size={38} />
            </span>
            <span className="art-tile tile-two">
              <Route size={38} />
            </span>
            <span className="art-tile tile-three">
              <Sparkles size={38} />
            </span>
            <div className="art-label">
              LEARN
              <br />
              MAKE
              <br />
              GROW<span>نیک‌راه</span>
            </div>
          </div>
        </div>
        <footer>{t("یادگیری برای عمل", "Learning, put into practice")}</footer>
      </main>
    );
  return (
    <div className="app-shell">
      <a className="skip-link" href="#main">
        {t("رفتن به محتوا", "Skip to content")}
      </a>
      {navOpen && (
        <button
          className="nav-scrim"
          aria-label={t("بستن فهرست", "Close menu")}
          onClick={() => {
            setNavOpen(false);
            requestAnimationFrame(() =>
              document.getElementById("menu-toggle")?.focus(),
            );
          }}
        />
      )}
      <aside
        id="side-panel"
        role={navOpen ? "dialog" : undefined}
        aria-modal={navOpen ? true : undefined}
        aria-label={t("فهرست ناوبری", "Navigation menu")}
        className={`sidebar glass ${navOpen ? "is-open" : ""}`}
      >
        <div className="brand">
          <span className="brand-symbol">N</span>
          <span>
            NIKWAY <small>ACADEMY</small>
          </span>
          <Button
            className="mobile-only"
            variant="ghost"
            size="icon"
            aria-label={t("بستن فهرست", "Close menu")}
            onClick={() => {
              setNavOpen(false);
              requestAnimationFrame(() =>
                document.getElementById("menu-toggle")?.focus(),
              );
            }}
          >
            <X aria-hidden="true" />
          </Button>
        </div>
        <p className="sidebar-caption">
          {t("فضای رشد شما", "YOUR LEARNING SPACE")}
        </p>
        <nav aria-label={t("ناوبری اصلی", "Main navigation")}>
          {screens.map(([id, fa, eng, Icon], i) => (
            <div key={id}>
              {(i === 4 || i === 9) && <div className="nav-divider" />}
              <button
                aria-current={page === id ? "page" : undefined}
                onClick={() => navigate(id)}
              >
                <Icon size={20} aria-hidden="true" />
                <span>{t(fa, eng)}</span>
                {id === "services" && (
                  <span
                    className="nav-dot"
                    aria-label={t("متصل نشده", "Not connected")}
                  />
                )}
              </button>
            </div>
          ))}
          {reviewer && (
            <button
              aria-current={page === "review" ? "page" : undefined}
              onClick={() => navigate("review")}
            >
              <ClipboardCheck size={20} aria-hidden="true" />
              {t("بازبینی تکالیف", "Review assignments")}
            </button>
          )}
        </nav>
        <div className="sidebar-bottom">
          {moodle.enabled && moodleBase && (
            <a
              className="moodle-launch"
              href={moodleBase}
              target="_blank"
              rel="noopener noreferrer"
            >
              <GraduationCap size={20} aria-hidden="true" />
              {t("ورود به Moodle ↗", "Open Moodle ↗")}
            </a>
          )}
          <button
            className="account-switch"
            onClick={() => navigate("profile")}
          >
            <span className="avatar">
              <UserRound size={21} aria-hidden="true" />
            </span>
            <span>
              {reviewer
                ? t("بازبین یادگیری", "Learning reviewer")
                : t("یادگیرنده نیک‌راه", "NIKWAY learner")}
              <small>{t("حساب سازمانی", "Organization account")}</small>
            </span>
          </button>
          <Button
            variant="ghost"
            onClick={() =>
              auth.logout({ redirectUri: window.location.origin + "/" })
            }
          >
            <LogOut aria-hidden="true" />
            {t("خروج", "Sign out")}
          </Button>
        </div>
      </aside>
      <div className="main-column" inert={navOpen}>
        <header className="topbar glass">
          <div className="breadcrumb">
            <Button
              className="mobile-only"
              variant="ghost"
              size="icon"
              id="menu-toggle"
              aria-controls="side-panel"
              aria-label={t("فهرست", "Menu")}
              aria-expanded={navOpen}
              onClick={() => setNavOpen(!navOpen)}
            >
              <Menu aria-hidden="true" />
            </Button>
            <span>{t("فضای یادگیری", "Learning space")}</span>
            <span aria-hidden="true">/</span>
            <strong>
              {screens.find((s) => s[0] === page)?.[en ? 2 : 1] ||
                t("بازبینی", "Review")}
            </strong>
          </div>
          <div className="topbar-actions">
            <span className="local-indicator">
              <i />
              {t("محیط محلی", "Local workspace")}
            </span>
            {PreferenceControls}
            <Button
              variant="ghost"
              size="icon"
              aria-label={t("تازه‌سازی", "Refresh")}
              disabled={busy}
              onClick={() => act(async () => {})}
            >
              <RefreshCw size={18} aria-hidden="true" />
            </Button>
          </div>
        </header>
        <main
          id="main"
          ref={mainRef}
          tabIndex={-1}
          className="workspace"
          aria-busy={busy}
        >
          {!online && (
            <p role="alert" className="error-banner">
              <WifiOff aria-hidden="true" />
              {t(
                "آفلاین هستید. برای دریافت و ثبت اطلاعات، دوباره متصل شوید.",
                "You are offline. Reconnect to load or save learning data.",
              )}
            </p>
          )}
          {error && (
            <div role="alert" className="error-banner">
              {error}
              <Button variant="outline" onClick={() => act(async () => {})}>
                {t("تلاش دوباره", "Retry")}
              </Button>
            </div>
          )}
          {notice && (
            <p role="status" className="notice">
              <Check size={18} aria-hidden="true" />
              {notice}
            </p>
          )}
          {page === "dashboard" && (
            <>
              <PageHeading
                eyebrow={t(
                  "هر روز، یک قدم رو به جلو",
                  "ONE STEP FORWARD, EVERY DAY",
                )}
                title={t(
                  "سلام، به فضای یادگیری‌ات خوش آمدی",
                  "Welcome to your learning space",
                )}
                description={t(
                  "لازم نیست همه چیز را امروز یاد بگیری. از قدم بعدی شروع کن.",
                  "You don’t need to learn everything today. Just take the next step.",
                )}
              />
              <div className="dashboard-bento">
                <section className="continue-card">
                  <div>
                    <Badge>{t("قدم بعدی شما", "YOUR NEXT STEP")}</Badge>
                    <h2>
                      {nextCourse
                        ? nextCourse.title
                        : t(
                            "مسیرت را با یک دوره آغاز کن",
                            "Start your journey with a course",
                          )}
                    </h2>
                    <p>
                      {nextCourse
                        ? t(
                            "با یک درس یا یک تمرین، یادگیری را به عمل تبدیل کن.",
                            "Turn learning into practice with a lesson or an assignment.",
                          )
                        : t(
                            "دوره‌های موجود برای سازمانت را ببین.",
                            "Explore courses available to your organization.",
                          )}
                    </p>
                    <Button
                      className="primary-cta"
                      onClick={() =>
                        nextCourse ? open(nextCourse) : navigate("courses")
                      }
                    >
                      {t("ادامه یادگیری", "Continue learning")}
                      <Arrow aria-hidden="true" />
                    </Button>
                  </div>
                  <div className="growth-mark" aria-hidden="true">
                    <div />
                    <div />
                    <div />
                    <span>↗</span>
                  </div>
                </section>
                <Card className="today-card">
                  <span className="icon-tile">
                    <ClipboardCheck aria-hidden="true" />
                  </span>
                  <h2>{t("یادگیری، با بازخورد", "Learning with feedback")}</h2>
                  <p>
                    {t(
                      "تمرین‌هایت را مرور کن و قدم بعدی را از بازخورد بازبین پیدا کن.",
                      "Review your work and find your next step in reviewer feedback.",
                    )}
                  </p>
                  <button
                    className="text-link"
                    onClick={() => navigate("progress")}
                  >
                    {t("مشاهده تکالیف", "View assignments")}
                    <Arrow size={18} aria-hidden="true" />
                  </button>
                </Card>
                <div className="metrics">
                  <Card>
                    <span className="metric-icon">
                      <BookOpen aria-hidden="true" />
                    </span>
                    <div>
                      <strong>
                        {enrolled.length.toLocaleString(en ? "en" : "fa")}
                      </strong>
                      <p>{t("دوره ثبت‌نام‌شده", "Enrolled courses")}</p>
                    </div>
                  </Card>
                  <Card>
                    <span className="metric-icon">
                      <Check aria-hidden="true" />
                    </span>
                    <div>
                      <strong>
                        {totalDone.toLocaleString(en ? "en" : "fa")}
                      </strong>
                      <p>{t("درس تکمیل‌شده", "Completed lessons")}</p>
                    </div>
                  </Card>
                  <Card>
                    <span className="metric-icon">
                      <ClipboardCheck aria-hidden="true" />
                    </span>
                    <div>
                      <strong>
                        {submissions.length.toLocaleString(en ? "en" : "fa")}
                      </strong>
                      <p>{t("تکلیف ثبت‌شده", "Submitted assignments")}</p>
                    </div>
                  </Card>
                </div>
              </div>
              <div className="section-heading">
                <div>
                  <h2>{t("دوره‌های شما", "Your courses")}</h2>
                  <p className="muted">
                    {t(
                      "مسیرهای واقعی، متناسب با فضای سازمان شما",
                      "Real learning paths in your organization",
                    )}
                  </p>
                </div>
                <Button variant="ghost" onClick={() => navigate("courses")}>
                  {t("همه دوره‌ها", "All courses")}
                  <Arrow aria-hidden="true" />
                </Button>
              </div>
              <div className="course-grid">
                {courses.slice(0, 3).map((c) => (
                  <CourseCard
                    key={c.id}
                    course={c}
                    onOpen={() => open(c)}
                    en={en}
                  />
                ))}
              </div>
              {!courses.length && (
                <Empty
                  title={t("دوره‌ای در دسترس نیست", "No courses available")}
                >
                  {t(
                    "پس از انتشار دوره برای سازمان شما، اینجا نمایش داده می‌شود.",
                    "Courses published for your organization will appear here.",
                  )}
                </Empty>
              )}
              <MoodleSection
                moodle={moodle}
                error={moodleError}
                en={en}
                retry={loadMoodle}
              />
            </>
          )}
          {page === "courses" && (
            <>
              <PageHeading
                eyebrow="COURSE CATALOG"
                title={t(
                  "چه چیزی می‌خواهی یاد بگیری؟",
                  "What would you like to learn?",
                )}
                description={t(
                  "یک مسیر انتخاب کن و با سرعت خودت پیش برو.",
                  "Choose a path and learn at your own pace.",
                )}
              />
              <div className="filter-bar">
                <label className="search-field">
                  <Search size={20} aria-hidden="true" />
                  <span className="sr-only">
                    {t("جست‌وجوی دوره", "Search courses")}
                  </span>
                  <input
                    type="search"
                    placeholder={t("جست‌وجو در دوره‌ها…", "Search courses…")}
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                  />
                </label>
                <div
                  className="segmented"
                  aria-label={t("فیلتر دوره‌ها", "Filter courses")}
                >
                  {[
                    ["all", "همه دوره‌ها", "All courses"],
                    ["enrolled", "دوره‌های من", "My courses"],
                  ].map(([id, fa, eng]) => (
                    <button
                      key={id}
                      aria-pressed={filter === id}
                      onClick={() => setFilter(id)}
                    >
                      {t(fa, eng)}
                    </button>
                  ))}
                </div>
              </div>
              <div className="course-grid">
                {visibleCourses.map((c) => (
                  <CourseCard
                    key={c.id}
                    course={c}
                    onOpen={() => open(c)}
                    en={en}
                  />
                ))}
              </div>
              {!visibleCourses.length && (
                <Empty title={t("دوره‌ای پیدا نشد", "No courses found")}>
                  {t(
                    "عبارت جست‌وجو یا فیلتر را تغییر بده.",
                    "Try another search or filter.",
                  )}
                </Empty>
              )}
              <MoodleSection
                moodle={moodle}
                error={moodleError}
                en={en}
                retry={loadMoodle}
              />
            </>
          )}
          {page === "workspace" && (
            <LearningWorkspace
              key={selected}
              course={course}
              content={selected ? assignmentDrafts[selected] || "" : ""}
              setContent={(value) => {
                if (selected)
                  setAssignmentDrafts((drafts) => ({
                    ...drafts,
                    [selected]: value,
                  }));
              }}
              busy={busy}
              act={act}
              back={() => navigate("courses")}
              en={en}
            />
          )}
          {page === "path" && (
            <>
              <PageHeading
                eyebrow="LEARNING PATH"
                title={t(
                  "قدم‌های کوچک، رشد پیوسته",
                  "Small steps. Steady growth.",
                )}
                description={t(
                  "ترتیب درس‌ها و هدف‌های دوره؛ پیشرفت از سرور آکادمی دریافت می‌شود.",
                  "Course sequence and objectives, using progress from Academy.",
                )}
              />
              {courses.map((c) => (
                <Card className="path-card" key={c.id}>
                  <div className="section-heading">
                    <h2 dir="auto">{c.title}</h2>
                    <Button variant="outline" onClick={() => open(c)}>
                      {t("مشاهده دوره", "View course")}
                    </Button>
                  </div>
                  <Progress
                    value={completion(c)}
                    label={t("تکمیل درس‌ها", "Lesson completion")}
                  />
                  <ol className="path-steps">
                    {c.lessons.map((l, i) => (
                      <li key={l.id}>
                        <span className="step-number">
                          {c.completed_lessons.includes(l.id) ? (
                            <Check aria-hidden="true" />
                          ) : (
                            i + 1
                          )}
                        </span>
                        <div>
                          <h3 dir="auto">{l.title}</h3>
                          <p className="muted">
                            {c.completed_lessons.includes(l.id)
                              ? t("تکمیل شده", "Completed")
                              : t("در مسیر یادگیری", "On your learning path")}
                          </p>
                        </div>
                      </li>
                    ))}
                  </ol>
                  <p className="muted">
                    {t(
                      "تکمیل درس‌ها معادل قبولی تکلیف نیست.",
                      "Lesson completion is separate from assessment approval.",
                    )}
                  </p>
                </Card>
              ))}
            </>
          )}
          {page === "services" && (
            <>
              <PageHeading
                eyebrow="AI TUTOR"
                title={t(
                  "با یک پرسش خوب شروع کن",
                  "Start with a good question",
                )}
                description={t(
                  "فضایی برای فکر کردن درباره چیزی که یاد می‌گیری.",
                  "A space to reflect on what you are learning.",
                )}
              />
              <Card className="tutor-card">
                <span className="large-icon">
                  <Bot size={36} aria-hidden="true" />
                </span>
                <Badge tone="warning">
                  {t("مربی هوشمند هنوز متصل نیست", "AI tutor is not connected")}
                </Badge>
                <h2>
                  {t(
                    "پاسخ واقعی، وقتی اتصال آماده باشد",
                    "Real answers, when a provider is connected",
                  )}
                </h2>
                <p>
                  {t(
                    "در این نسخه پاسخ هوش مصنوعی تولید نمی‌شود. برای تمرین می‌توانی از پرسش‌های تأمل و منابع دوره استفاده کنی.",
                    "This version does not generate AI answers. Use the reflection prompts and course materials for practice.",
                  )}
                </p>
                <div className="prompt-grid">
                  {[
                    t(
                      "این مفهوم را کجا می‌توانم به کار ببرم؟",
                      "Where could I apply this concept?",
                    ),
                    t(
                      "چه شواهدی نشان می‌دهد یاد گرفته‌ام؟",
                      "What evidence would show I learned it?",
                    ),
                    t(
                      "کدام بخش هنوز برایم روشن نیست؟",
                      "Which part is still unclear?",
                    ),
                  ].map((p) => (
                    <div className="prompt" key={p}>
                      <Sparkles size={18} aria-hidden="true" />
                      {p}
                    </div>
                  ))}
                </div>
                <Button variant="outline" onClick={() => navigate("library")}>
                  {t("رفتن به منابع یادگیری", "Explore learning resources")}
                  <Arrow aria-hidden="true" />
                </Button>
              </Card>
            </>
          )}
          {(page === "progress" || page === "review") && (
            <>
              <PageHeading
                eyebrow="ASSESSMENT & FEEDBACK"
                title={
                  page === "review"
                    ? t("بازبینی تکالیف", "Review assignments")
                    : t("پیشرفت و تکالیف", "Assessment & feedback")
                }
                description={t(
                  "شواهد یادگیری و بازخورد انسانی، در کنار هم.",
                  "Learning evidence and human feedback, together.",
                )}
              />
              <Submissions
                items={submissions}
                feedback={feedbackDrafts}
                setFeedback={setFeedbackDrafts}
                courses={courses}
                review={page === "review" && reviewer}
                busy={busy}
                act={act}
                en={en}
              />
            </>
          )}
          {page === "projects" && (
            <>
              <PageHeading
                eyebrow="PROJECTS"
                title={t(
                  "دانسته‌هایت را به عمل تبدیل کن",
                  "Put what you know into practice",
                )}
                description={t(
                  "پروژه‌های این نسخه همان تمرین‌های دوره و شواهد ارسالی شما هستند.",
                  "Projects in this version are course practices and your submitted evidence.",
                )}
              />
              <div className="course-grid">
                {courses
                  .filter((c) => c.metadata?.assessment)
                  .map((c) => (
                    <Card key={c.id}>
                      <Badge>
                        {t("تمرین کاربردی دوره", "Course practice")}
                      </Badge>
                      <h2 dir="auto">{c.title}</h2>
                      <p dir="auto">{c.metadata?.assessment?.prompt}</p>
                      <Button onClick={() => open(c)}>
                        {t("باز کردن تمرین", "Open practice")}
                        <Arrow aria-hidden="true" />
                      </Button>
                    </Card>
                  ))}
              </div>
              {!courses.some((c) => c.metadata?.assessment) && (
                <Empty
                  title={t(
                    "هنوز تمرینی تعریف نشده",
                    "No practice projects yet",
                  )}
                >
                  {t(
                    "تمرین‌های منتشرشده دوره اینجا نمایش داده می‌شوند.",
                    "Published course practices will appear here.",
                  )}
                </Empty>
              )}
            </>
          )}
          {page === "library" && (
            <>
              <PageHeading
                eyebrow="KNOWLEDGE LIBRARY"
                title={t(
                  "یک مرجع، برای قدم بعدی",
                  "A reference for your next step",
                )}
                description={t(
                  "درس‌های دوره‌های در دسترس؛ محتوای اصلی بدون تغییر نمایش داده می‌شود.",
                  "Lessons from available courses, preserving the original content.",
                )}
              />
              <label className="search-field">
                <Search aria-hidden="true" />
                <span className="sr-only">
                  {t("جست‌وجوی منابع", "Search resources")}
                </span>
                <input
                  type="search"
                  placeholder={t("جست‌وجو در منابع…", "Search resources…")}
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                />
              </label>
              <div className="library-list">
                {courses.flatMap((c) =>
                  c.lessons
                    .filter((l) =>
                      `${l.title} ${l.content}`
                        .toLowerCase()
                        .includes(query.toLowerCase()),
                    )
                    .map((l) => (
                      <Card key={l.id}>
                        <span className="icon-tile">
                          <BookOpen aria-hidden="true" />
                        </span>
                        <div>
                          <p className="muted small" dir="auto">
                            {c.title}
                          </p>
                          <h2 dir="auto">{l.title}</h2>
                          <p className="excerpt" dir="auto">
                            {l.content}
                          </p>
                        </div>
                        <Button variant="outline" onClick={() => open(c)}>
                          {t("مطالعه در دوره", "Read in course")}
                        </Button>
                      </Card>
                    )),
                )}
              </div>
              {courses.flatMap((c) =>
                c.lessons.filter((l) =>
                  `${l.title} ${l.content}`
                    .toLowerCase()
                    .includes(query.toLowerCase()),
                ),
              ).length === 0 && (
                <Empty title={t("منبعی پیدا نشد", "No resources found")}>
                  {t("عبارت دیگری را جست‌وجو کنید.", "Try another search.")}
                </Empty>
              )}
            </>
          )}
          {page === "profile" && (
            <>
              <PageHeading
                eyebrow="YOUR SPACE"
                title={t("فضایی به سلیقه تو", "Make this space yours")}
                description={t(
                  "تنظیم‌های نمایش روی همین دستگاه ذخیره می‌شوند؛ اطلاعات یادگیری ذخیره آفلاین نمی‌شود.",
                  "Display preferences stay on this device. Learning data is not stored offline.",
                )}
              />
              <div className="settings-grid">
                <Card>
                  <h2>{t("تنظیم‌های نمایش", "Display preferences")}</h2>
                  <label htmlFor="variant">
                    {t("سبک بصری", "Visual style")}
                  </label>
                  <select
                    id="variant"
                    value={preferences.variant}
                    onChange={(e) =>
                      setPreferences({
                        ...preferences,
                        variant: e.target.value as Preferences["variant"],
                      })
                    }
                  >
                    <option value="jade">
                      {t("یشمی آرام · Focus Jade", "Focus Jade")}
                    </option>
                    <option value="ink">
                      {t("استودیوی تیره · Studio Ink", "Studio Ink")}
                    </option>
                    <option value="paper">
                      {t("کاغذ گرم · Warm Paper", "Warm Paper")}
                    </option>
                  </select>
                  <div className="preference-row">
                    <label htmlFor="solid">
                      {t("کاهش شفافیت", "Reduce transparency")}
                      <small>
                        {t(
                          "سطوح کاملاً مات برای تمرکز بیشتر",
                          "Opaque surfaces for easier focus",
                        )}
                      </small>
                    </label>
                    <input
                      id="solid"
                      type="checkbox"
                      checked={preferences.solid}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          solid: e.target.checked,
                        })
                      }
                    />
                  </div>
                  <div className="preference-row">
                    <label htmlFor="quiet">
                      {t("کاهش حرکت", "Reduce motion")}
                      <small>
                        {t(
                          "بدون انیمیشن و انتقال‌های بصری",
                          "No decorative animations or transitions",
                        )}
                      </small>
                    </label>
                    <input
                      id="quiet"
                      type="checkbox"
                      checked={preferences.quiet}
                      onChange={(e) =>
                        setPreferences({
                          ...preferences,
                          quiet: e.target.checked,
                        })
                      }
                    />
                  </div>
                  <Button variant="outline" onClick={() => navigate("kit")}>
                    <Layers aria-hidden="true" />
                    {t(
                      "مشاهده کیت رابط و سه طرح",
                      "UI kit and design variants",
                    )}
                  </Button>
                </Card>
                <Card>
                  <h2>{t("حساب سازمانی", "Organization account")}</h2>
                  <dl className="account-details">
                    <dt>{t("نقش", "Role")}</dt>
                    <dd>{me?.role}</dd>
                    <dt>{t("شناسه سازمان", "Organization ID")}</dt>
                    <dd>
                      <bdi>{me?.tenant_id}</bdi>
                    </dd>
                    <dt>{t("شناسه حساب", "Account ID")}</dt>
                    <dd>
                      <bdi>{me?.sub}</bdi>
                    </dd>
                  </dl>
                  <p className="muted">
                    {t(
                      "اطلاعات هویتی توسط سرویس ورود سازمان مدیریت می‌شود.",
                      "Identity details are managed by your organization’s sign-in service.",
                    )}
                  </p>
                </Card>
              </div>
            </>
          )}
          {page === "admin" && (
            <>
              <PageHeading
                eyebrow="ADMINISTRATION"
                title={t("مدیریت فضای یادگیری", "Learning administration")}
                description={t(
                  "وضعیت واقعی قابلیت‌ها و محدوده دسترسی حساب شما.",
                  "Actual service availability and your account permissions.",
                )}
              />
              {reviewer ? (
                <Card>
                  <h2>{t("بازبینی انسانی", "Human review")}</h2>
                  <p>
                    {t(
                      "بازبینی تکالیف در محدوده سازمان شما در دسترس است. تغییر تنظیمات زیرساخت از این رابط فعال نیست.",
                      "Assignment review is available within your organization. Infrastructure settings cannot be changed here.",
                    )}
                  </p>
                  <Button onClick={() => navigate("review")}>
                    {t("بازبینی تکالیف", "Review assignments")}
                  </Button>
                  <CapabilityList values={capabilities} en={en} />
                </Card>
              ) : (
                <Card>
                  <span className="large-icon">
                    <ShieldCheck aria-hidden="true" />
                  </span>
                  <h2>
                    {t(
                      "دسترسی مدیریت ندارید",
                      "Administration access is restricted",
                    )}
                  </h2>
                  <p>
                    {t(
                      "با نقش یادگیرنده وارد شده‌اید. برای تغییرات مدیریتی با مسئول سازمان هماهنگ کنید.",
                      "You are signed in as a learner. Contact your organization administrator for management changes.",
                    )}
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => navigate("dashboard")}
                  >
                    {t("بازگشت به یادگیری", "Back to learning")}
                  </Button>
                </Card>
              )}
            </>
          )}
          {page === "workshops" && (
            <>
              <PageHeading
                eyebrow="WORKSHOPS"
                title={t("با هم یاد بگیریم", "Learn together")}
                description={t(
                  "ثبت‌نام کارگاه فعال است؛ جلسه آنلاین در این نسخه متصل نیست.",
                  "Workshop registration is available. Video meetings are not connected.",
                )}
              />
              {!workshops.length && (
                <Empty
                  title={t(
                    "کارگاهی برنامه‌ریزی نشده",
                    "No workshops scheduled",
                  )}
                >
                  {t(
                    "کارگاه‌های سازمان شما اینجا نمایش داده می‌شوند.",
                    "Your organization’s workshops will appear here.",
                  )}
                </Empty>
              )}
              {workshops.map((w) => (
                <Card key={w.id}>
                  <h2>{w.title}</h2>
                  <p>{w.description}</p>
                  {w.starts_at && (
                    <p>
                      <bdi>{w.starts_at}</bdi>
                    </p>
                  )}
                  <Button
                    disabled={busy || w.registered}
                    onClick={() =>
                      act(() => api(`/workshops/${w.id}/register`, {}))
                    }
                  >
                    {w.registered
                      ? t("ثبت‌نام شده", "Registered")
                      : t("ثبت‌نام در کارگاه", "Register for workshop")}
                  </Button>
                </Card>
              ))}
            </>
          )}
          {page === "kit" && (
            <>
              <PageHeading
                eyebrow="NIKWAY DESIGN SYSTEM"
                title={t(
                  "یک زبان مشترک، سه حال‌وهوا",
                  "One shared language. Three moods.",
                )}
                description={t(
                  "نمونه‌های واقعی اجزای رابط؛ محتوا از سیستم طراحی است، نه داده یادگیری.",
                  "Live component examples, not learning data.",
                )}
              />
              <div className="variant-grid">
                {(["jade", "ink", "paper"] as const).map((v, i) => (
                  <Card key={v} data-preview={v}>
                    <div className="variant-swatch">
                      <span />
                      <span />
                      <span />
                    </div>
                    <h2>{["Focus Jade", "Studio Ink", "Warm Paper"][i]}</h2>
                    <p>
                      {
                        [
                          t(
                            "آرام و متمرکز؛ انتخاب پیش‌فرض",
                            "Calm and focused; the default",
                          ),
                          t(
                            "دقیق و فنی؛ آبی جوهری",
                            "Precise and technical; ink blue",
                          ),
                          t(
                            "گرم و کتاب‌محور؛ ماسه‌ای",
                            "Warm and editorial; soft sand",
                          ),
                        ][i]
                      }
                    </p>
                    <Button
                      variant={
                        preferences.variant === v ? "default" : "outline"
                      }
                      aria-pressed={preferences.variant === v}
                      onClick={() =>
                        setPreferences({ ...preferences, variant: v })
                      }
                    >
                      {preferences.variant === v
                        ? t("انتخاب شده", "Selected")
                        : t("انتخاب طرح", "Choose style")}
                    </Button>
                  </Card>
                ))}
              </div>
              <Card>
                <h2>{t("اتم‌ها و حالت‌ها", "Atoms and states")}</h2>
                <div className="actions">
                  <Button>{t("اقدام اصلی", "Primary action")}</Button>
                  <Button variant="outline">
                    {t("اقدام دوم", "Secondary action")}
                  </Button>
                  <Button disabled>{t("غیرفعال", "Disabled")}</Button>
                  <Badge tone="success">{t("موفق", "Success")}</Badge>
                  <Badge tone="warning">
                    {t("نیازمند توجه", "Needs attention")}
                  </Badge>
                </div>
                <Progress
                  value={45}
                  label={t(
                    "نمونه پیشرفت (داده نمایشی)",
                    "Example progress (demo data)",
                  )}
                />
                <p className="muted">
                  {t(
                    "فونت وزیرمتن • فاصله‌گذاری بر پایه ۴ و ۸ • هدف لمس حداقل ۴۴ پیکسل",
                    "Vazirmatn · 4/8 spacing scale · minimum 44px touch targets",
                  )}
                </p>
              </Card>
            </>
          )}
        </main>
        <footer className="app-footer">
          <span>NIKWAY ACADEMY</span>
          <p>
            {t(
              "برای رشد، قدم بعدی کافی است.",
              "For growth, the next step is enough.",
            )}
          </p>
          <span>
            {t(
              "داده زنده • ذخیره‌سازی در سرور",
              "Live data · Stored on the server",
            )}
          </span>
        </footer>
      </div>
    </div>
  );
}
function CapabilityList({
  values,
  en,
}: {
  values: Record<string, string>;
  en: boolean;
}) {
  return (
    <dl className="capability-list">
      {Object.entries(values).map(([key, value]) => (
        <div key={key}>
          <dt>{capabilitiesLabels[key]?.[en ? 1 : 0] || key}</dt>
          <dd>{stateLabels[value]?.[en ? 1 : 0] || value}</dd>
        </div>
      ))}
    </dl>
  );
}
function MoodleSection({
  moodle,
  error,
  en,
  retry,
}: {
  moodle: MoodleOverview;
  error: string;
  en: boolean;
  retry: () => Promise<void>;
}) {
  if (!moodle.enabled && !error) return null;
  const base = safeMoodleUrl(moodle.url, moodle.url);
  return (
    <section
      className="moodle-section"
      aria-label={en ? "Moodle learning" : "یادگیری در Moodle"}
    >
      <div className="section-heading">
        <div>
          <p className="eyebrow">CONNECTED LEARNING</p>
          <h2>{en ? "Your Moodle classroom" : "کلاس شما در Moodle"}</h2>
        </div>
        <Badge>{en ? "Live Moodle API" : "API زنده Moodle"}</Badge>
      </div>
      {error ? (
        <Card>
          <p>{error}</p>
          <Button variant="outline" onClick={() => void retry()}>
            {en ? "Retry Moodle connection" : "تلاش دوباره اتصال Moodle"}
          </Button>
        </Card>
      ) : (
        <>
          <p className="muted">
            {en
              ? "Read directly from Moodle. Progress remains separate from Academy; lesson completion is not assessment approval."
              : "مستقیماً از Moodle دریافت شده است. پیشرفت آن از آکادمی مستقل است؛ تکمیل درس به معنی قبولی نیست."}
          </p>
          {!moodle.courses?.length && (
            <p>
              {en
                ? "No enrolled Moodle courses."
                : "دوره ثبت‌نام‌شده‌ای در Moodle وجود ندارد."}
            </p>
          )}
          {moodle.courses?.map((c) => (
            <Card key={c.id} className="moodle-course">
              <div>
                <Badge tone="success">Moodle</Badge>
                <h3 dir="auto">Moodle · {c.title}</h3>
                {typeof c.progress === "number" && (
                  <Progress
                    value={Math.round(c.progress)}
                    label={
                      en ? "Moodle lesson completion" : "تکمیل درس‌ها در Moodle"
                    }
                  />
                )}
              </div>
              <div className="moodle-modules">
                {c.modules.map((m) => (
                  <div key={m.id}>
                    {m.completion == null ? (
                      <BookOpen
                        size={20}
                        aria-label={
                          en ? "No completion tracking" : "بدون پیگیری تکمیل"
                        }
                      />
                    ) : (
                      <CompletionIcon
                        en={en}
                        done={m.completion === 1 || m.completion === 2}
                      />
                    )}
                    {safeMoodleUrl(m.url, base) ? (
                      <a
                        href={safeMoodleUrl(m.url, base)}
                        target="_blank"
                        rel="noopener noreferrer"
                        dir="auto"
                      >
                        {m.title}
                        <ExternalLink size={14} aria-hidden="true" />
                      </a>
                    ) : (
                      <span dir="auto">{m.title}</span>
                    )}
                  </div>
                ))}
              </div>
              {safeMoodleUrl(c.url, base) && (
                <a
                  className="button-link"
                  href={safeMoodleUrl(c.url, base)}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {en ? "Open classroom ↗" : "ورود به کلاس ↗"}
                </a>
              )}
            </Card>
          ))}
        </>
      )}
    </section>
  );
}
createRoot(document.getElementById("root")!).render(<App />);

if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    void navigator.serviceWorker.register("/sw.js").catch(() => {
      /* Offline fallback is optional; online learning remains available. */
    });
  });
}
