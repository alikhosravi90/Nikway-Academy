import React, { useState, useEffect } from "react";
import { createRoot } from "react-dom/client";
import Keycloak from "keycloak-js";
import "./legacy.css";
import "./operational.css";
const auth = new Keycloak({
  url: import.meta.env.VITE_AUTH_URL || "http://localhost:18480",
  realm: "academy",
  clientId: "academy-web",
});
type Course = {
  id: string;
  title: string;
  description: string;
  lessons: { id: string; title: string; content: string; position: number }[];
  completed_lessons: string[];
  enrolled: boolean;
};
type Submission = {
  id: string;
  course_id?: string;
  content: string;
  status: string;
  feedback?: string;
  revision: number;
};
type Workshop = {
  id: string;
  title: string;
  description?: string;
  registered?: boolean;
  starts_at?: string;
};
async function api<T>(path: string, body?: unknown): Promise<T> {
  await auth.updateToken(30);
  const r = await fetch("/api" + path, {
    method: body === undefined ? "GET" : "POST",
    headers: {
      Authorization: `Bearer ${auth.token}`,
      ...(body === undefined ? {} : { "Content-Type": "application/json" }),
    },
    body: body === undefined ? undefined : JSON.stringify(body),
    cache: "no-store",
  });
  if (!r.ok) {
    let detail = "";
    try {
      const e = await r.json();
      detail =
        typeof e.detail === "string"
          ? e.detail
          : e.message || JSON.stringify(e.detail);
    } catch {}
    throw new Error(`${r.status}: ${detail || "درخواست انجام نشد"}`);
  }
  return r.status === 204 ? (undefined as T) : r.json();
}
function App() {
  const [ready, setReady] = useState(false),
    [error, setError] = useState(""),
    [busy, setBusy] = useState(false),
    [page, setPage] = useState("courses");
  const [me, setMe] = useState<{
      sub: string;
      tenant_id: string;
      role: string;
    } | null>(null),
    [courses, setCourses] = useState<Course[]>([]),
    [submissions, setSubmissions] = useState<Submission[]>([]),
    [workshops, setWorkshops] = useState<Workshop[]>([]),
    [capabilities, setCapabilities] = useState<Record<string, string>>({});
  const [selected, setSelected] = useState<string | null>(null),
    [content, setContent] = useState(""),
    [feedback, setFeedback] = useState<Record<string, string>>({}),
    [notice, setNotice] = useState("");
  const refresh = async () => {
    const identity = await api<typeof me>("/me");
    setMe(identity);
    const [c, p, w, cap] = await Promise.all([
      api<Course[]>("/courses"),
      api<{ submissions: Submission[] }>("/progress"),
      api<Workshop[]>("/workshops"),
      api<Record<string, string>>("/capabilities"),
    ]);
    setCourses(c);
    setWorkshops(w);
    setCapabilities(cap);
    setSubmissions(
      identity?.role === "reviewer" || identity?.role === "admin"
        ? await api<Submission[]>("/submissions")
        : p.submissions || [],
    );
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
      setNotice("با موفقیت ثبت شد");
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }
  const course = courses.find((c) => c.id === selected);
  const reviewer = me?.role === "reviewer" || me?.role === "admin";
  if (!ready)
    return (
      <main className="boot" aria-busy="true">
        در حال اتصال به آکادمی…
      </main>
    );
  if (!auth.authenticated)
    return (
      <main className="boot card">
        <h1>آکادمی نیک‌راه</h1>
        <p>فضای یادگیری، تمرین و بازخورد تیم شما</p>
        <p>برای مشاهده دوره‌ها با حساب آکادمی وارد شوید.</p>
        {error && <p role="alert">{error}</p>}
        <button
          onClick={() => auth.login({ redirectUri: window.location.origin })}
        >
          ورود به آکادمی
        </button>
      </main>
    );
  return (
    <>
      <a className="skip-link" href="#main">
        رفتن به محتوا
      </a>
      <aside>
        <h1 className="brand">
          نیک‌راه <small>ACADEMY</small>
        </h1>
        <p>یادگیری برای عمل</p>
        <nav aria-label="ناوبری اصلی">
          {[
            ["courses", "دوره‌ها"],
            ["progress", "پیشرفت و تکالیف"],
            ["workshops", "کارگاه‌ها"],
            ["services", "خدمات و مربی"],
            ...(reviewer ? [["review", "بازبینی تکالیف"]] : []),
          ].map(([id, label]) => (
            <button
              key={id}
              aria-current={page === id ? "page" : undefined}
              onClick={() => {
                setPage(id);
                setSelected(null);
              }}
            >
              {label}
            </button>
          ))}
        </nav>
        <div className="identity">
          <p>
            سازمان: <bdi dir="ltr">{me?.tenant_id}</bdi>
          </p>
          <p>نقش: {me?.role}</p>
          <button
            onClick={() => auth.logout({ redirectUri: window.location.origin })}
          >
            خروج
          </button>
        </div>
      </aside>
      <main id="main" className="content">
        <header>
          <span>آکادمی نیک‌راه · محیط محلی</span>
          <button disabled={busy} onClick={() => act(async () => {})}>
            تازه‌سازی
          </button>
        </header>
        <div className="workspace">
          {error && (
            <div role="alert" className="error-banner">
              {error}
            </div>
          )}
          {notice && <p role="status">{notice}</p>}
          {page === "courses" && (
            <>
              <section className="hero">
                <span className="eyebrow">مسیر رشد شما</span>
                <h1>از یادگیری تا تجربه</h1>
                <p>
                  دوره را انتخاب کنید، درس‌ها را بخوانید و تمرین خود را برای
                  بازبینی ارسال کنید.
                </p>
              </section>
              {course ? (
                <article className="card">
                  <button onClick={() => setSelected(null)}>
                    بازگشت به دوره‌ها
                  </button>
                  <h2 dir="auto">{course.title}</h2>
                  <p dir="auto">{course.description}</p>
                  {!course.enrolled ? (
                    <button
                      disabled={busy}
                      onClick={() =>
                        act(() => api(`/courses/${course.id}/enroll`, {}))
                      }
                    >
                      ثبت‌نام در دوره
                    </button>
                  ) : (
                    <>
                      {course.lessons.map((lesson, index) => (
                        <section className="lesson" key={lesson.id}>
                          <h3 dir="auto">{lesson.title}</h3>
                          <p className="text-content" dir="auto">
                            {lesson.content}
                          </p>
                          <button
                            disabled={
                              busy ||
                              course.completed_lessons.includes(lesson.id) ||
                              index > course.completed_lessons.length
                            }
                            onClick={() =>
                              act(() =>
                                api(
                                  `/courses/${course.id}/lessons/${lesson.id}/complete`,
                                  {},
                                ),
                              )
                            }
                          >
                            {course.completed_lessons.includes(lesson.id)
                              ? "تکمیل شده"
                              : "ثبت تکمیل درس"}
                          </button>
                        </section>
                      ))}
                      <form
                        onSubmit={(e) => {
                          e.preventDefault();
                          void act(async () => {
                            await api(`/courses/${course.id}/submissions`, {
                              content,
                            });
                            setContent("");
                          });
                        }}
                      >
                        <h3>ارسال تکلیف</h3>
                        <label htmlFor="submission">
                          متن پاسخ و شواهد تمرین
                        </label>
                        <textarea
                          id="submission"
                          required
                          minLength={20}
                          maxLength={10000}
                          value={content}
                          onChange={(e) => setContent(e.target.value)}
                        />
                        {course.completed_lessons.length <
                          course.lessons.length && (
                          <p>
                            برای ارسال تکلیف ابتدا همه درس‌ها را تکمیل کنید.
                          </p>
                        )}
                        <button
                          disabled={
                            busy ||
                            content.trim().length < 20 ||
                            course.completed_lessons.length <
                              course.lessons.length
                          }
                        >
                          ارسال برای بازبینی
                        </button>
                      </form>
                    </>
                  )}
                </article>
              ) : (
                <div className="course-grid">
                  {courses.map((c) => (
                    <article className="card" key={c.id}>
                      <span className="tag">
                        {c.enrolled ? "ثبت‌نام شده" : "دوره آموزشی"}
                      </span>
                      <h2 dir="auto">{c.title}</h2>
                      <p dir="auto">{c.description}</p>
                      <p>
                        {c.completed_lessons?.length || 0} از {c.lessons.length}{" "}
                        درس
                      </p>
                      <button onClick={() => setSelected(c.id)}>
                        مشاهده دوره
                      </button>
                    </article>
                  ))}
                  {!courses.length && (
                    <p>هنوز دوره‌ای برای سازمان شما در دسترس نیست.</p>
                  )}
                </div>
              )}
            </>
          )}
          {(page === "progress" || page === "review") && (
            <>
              <h1>
                {page === "review" ? "بازبینی تکالیف" : "پیشرفت و تکالیف"}
              </h1>
              {page === "progress" && (
                <p>
                  پیشرفت ثبت‌شده:{" "}
                  {courses.reduce(
                    (n, c) => n + (c.completed_lessons?.length || 0),
                    0,
                  )}{" "}
                  درس تکمیل شده
                </p>
              )}
              {submissions.length === 0 && <p>تکلیفی برای نمایش وجود ندارد.</p>}
              {submissions.map((s) => (
                <article className="card" key={s.id}>
                  <p>
                    وضعیت: <strong>{s.status}</strong>
                  </p>
                  <p className="text-content" dir="auto">
                    {s.content}
                  </p>
                  {s.feedback && <p>بازخورد: {s.feedback}</p>}
                  {page === "review" && reviewer && (
                    <>
                      <label htmlFor={"feedback-" + s.id}>بازخورد بازبین</label>
                      <textarea
                        id={"feedback-" + s.id}
                        minLength={3}
                        maxLength={2000}
                        value={feedback[s.id] || ""}
                        onChange={(e) =>
                          setFeedback({ ...feedback, [s.id]: e.target.value })
                        }
                      />
                      <div className="actions">
                        <button
                          disabled={
                            busy || (feedback[s.id]?.trim().length || 0) < 3
                          }
                          onClick={() =>
                            act(() =>
                              api(`/submissions/${s.id}/review`, {
                                decision: "accepted",
                                expected_revision: s.revision,
                                feedback: feedback[s.id],
                              }),
                            )
                          }
                        >
                          پذیرش تکلیف
                        </button>
                        <button
                          disabled={
                            busy || (feedback[s.id]?.trim().length || 0) < 3
                          }
                          onClick={() =>
                            act(() =>
                              api(`/submissions/${s.id}/review`, {
                                decision: "revision_requested",
                                expected_revision: s.revision,
                                feedback: feedback[s.id],
                              }),
                            )
                          }
                        >
                          درخواست اصلاح
                        </button>
                      </div>
                    </>
                  )}
                </article>
              ))}
            </>
          )}
          {page === "workshops" && (
            <>
              <h1>کارگاه‌ها</h1>
              {workshops.length === 0 && <p>کارگاهی برنامه‌ریزی نشده است.</p>}
              {workshops.map((w) => (
                <article className="card" key={w.id}>
                  <h2>{w.title}</h2>
                  <p>{w.description}</p>
                  {w.starts_at && <p>{w.starts_at}</p>}
                  <button
                    disabled={busy || w.registered}
                    onClick={() =>
                      act(() => api(`/workshops/${w.id}/register`, {}))
                    }
                  >
                    {w.registered ? "ثبت‌نام شده" : "ثبت‌نام در کارگاه"}
                  </button>
                </article>
              ))}
            </>
          )}
          {page === "services" && (
            <>
              <h1>خدمات و مربی</h1>
              <article className="card">
                <h2>وضعیت اتصال خدمات</h2>
                <p>
                  این محیط مربی پاسخ‌گوی ساختگی ندارد. قابلیت‌های متصل‌نشده در
                  دسترس نیستند.
                </p>
                <dl>
                  {Object.entries(capabilities).map(([key, value]) => (
                    <div className="capability" key={key}>
                      <dt>
                        {{
                          authentication: "ورود به حساب",
                          learning: "یادگیری",
                          workshops: "کارگاه‌ها",
                          videoconferencing: "جلسه آنلاین",
                          ai_provider: "مربی هوشمند",
                          mcp: "اتصال ابزارهای بیرونی",
                          tools: "ابزارهای یادگیری",
                          credentials: "گواهی یادگیری",
                        }[key] || key}
                      </dt>
                      <dd>
                        {{
                          operational: "فعال",
                          registration_only:
                            "فقط ثبت‌نام؛ جلسه آنلاین متصل نیست",
                          not_integrated: "متصل نشده",
                          disabled: "غیرفعال",
                          read_only_progress: "مشاهده پیشرفت",
                          not_issued: "صادر نمی‌شود",
                        }[value] || value}
                      </dd>
                    </div>
                  ))}
                </dl>
              </article>
            </>
          )}
        </div>
        <footer>
          اطلاعات یادگیری از سرور سازمان شما دریافت می‌شود. برای ثبت تغییرات
          اتصال لازم است.
        </footer>
      </main>
    </>
  );
}
document.documentElement.lang = "fa";
document.documentElement.dir = "rtl";
createRoot(document.getElementById("root")!).render(<App />);
