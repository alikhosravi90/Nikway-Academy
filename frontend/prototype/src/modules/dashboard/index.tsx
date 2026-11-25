import { useState } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { useCatalog } from "../../data/catalog";
import { Heading, Card } from "../../components/shared";
import { CourseRow, CourseDialog } from "../../components/course";
import { Button } from "../../components/ui/button";
export default function Dashboard() {
  const { t, num } = useI18n(),
    { state } = useLearning(),
    { courses } = useCatalog();
  const [selected, setSelected] = useState<number | null>(null);
  return (
    <>
      <Heading
        title={t("سلام یادگیرنده آزمایشی، خوش آمدید 👋", "Welcome back, Synthetic Learner 👋")}
        subtitle={t(
          "مسیر رشد شما، از یادگیری تا تجربه و اثرگذاری.",
          "Your path from learning to practice and impact.",
        )}
      />
      <section className="hero">
        <div>
          <span className="tag">
            {t("مسیر یادگیری پیشنهادی شما", "Your recommended learning path")}
          </span>
          <h2 className="mt-4">
            {t(
              "دانش را به توانمندی تبدیل کنید.",
              "Turn knowledge into capability.",
            )}
          </h2>
          <p>
            {t(
              "مسیر «مشاور تحول سازمانی» را ادامه دهید؛ بیاموزید، در محیطی امن تمرین کنید و پیشرفت خود را ببینید.",
              "Continue the Organizational Transformation Consultant path. Learn, practice in a safe environment and see your progress.",
            )}
          </p>
          <Button className="hero-cta" onClick={() => setSelected(0)}>
            {t("ادامهٔ مسیر یادگیری ←", "Continue learning →")}
          </Button>
        </div>
        <div className="hero-art" aria-hidden>
          <div className="orbit" />
          <div className="orbit" />
          <div className="core">▧</div>
          <div className="star">✧</div>
        </div>
      </section>
      <div className="grid stats">
        {[
          ["▧", num(3), t("دوره در مسیر شما", "Courses in your path")],
          [
            "◷",
            num(state.done.reduce((a, b) => a + b, 0) * 15) +
              " " +
              t("دقیقه", "min"),
            t("زمان یادگیری نمونه", "Sample learning time"),
          ],
          ["⌘", num(6), t("شایستگی در حال رشد", "Growing competencies")],
          ["⚗", num(state.sim), t("تمرین تکمیل‌شده", "Completed simulations")],
        ].map((x, i) => (
          <Card className="stat" key={i}>
            <span className="stat-icon" aria-hidden>
              {x[0]}
            </span>
            <div>
              <strong data-testid={i === 3 ? "simulation-count" : undefined}>
                {x[1]}
              </strong>
              <span className="muted">{x[2]}</span>
            </div>
          </Card>
        ))}
      </div>
      <div className="grid cols">
        <Card>
          <div className="section-head">
            <h2>{t("یادگیری را ادامه دهید", "Continue learning")}</h2>
            <Link className="link" to="/academy">
              {t("مشاهدهٔ آکادمی ←", "View academy →")}
            </Link>
          </div>
          {courses.slice(0, 2).map((c) => (
            <CourseRow key={c.id} course={c} onOpen={() => setSelected(c.id)} />
          ))}
        </Card>
        <Card>
          <h2>{t("گام بعدی شما", "Your next step")}</h2>
          <div className="timeline">
            <p>
              <strong>
                {t("یک مفهوم تازه یاد بگیرید", "Learn a new concept")}
              </strong>
              <br />
              <span className="muted">
                {t("درس بعدی: حلقه‌های بازخورد", "Next: feedback loops")}
              </span>
            </p>
            <p>
              <strong>
                {t("دانش خود را به چالش بکشید", "Challenge your knowledge")}
              </strong>
              <br />
              <Link className="link" to="/lab">
                {t(
                  "ورود به شبیه‌سازی گلوگاه تولید ←",
                  "Try the bottleneck simulation →",
                )}
              </Link>
            </p>
            <p>
              <strong>
                {t("با مربی خود گفت‌وگو کنید", "Talk to your tutor")}
              </strong>
              <br />
              <Link className="link" to="/tutor">
                {t("مرور نکته‌های کلیدی ←", "Review key concepts →")}
              </Link>
            </p>
          </div>
        </Card>
        <Card>
          <h2>{t("رشد با تمرین، نه فقط تماشا", "Grow through practice")}</h2>
          <p className="muted">
            {t(
              "هر دوره به یک شایستگی و یک تجربهٔ عملی متصل است. فاصلهٔ خود تا سطح هدف را در نقشهٔ شایستگی ببینید.",
              "Every course connects to a competency and practical experience. Explore the gap to your target level.",
            )}
          </p>
          <Button asChild variant="outline">
            <Link to="/competency">
              {t("کاوش نقشهٔ شایستگی ←", "Explore competencies →")}
            </Link>
          </Button>
        </Card>
        <Card>
          <div className="flex">
            <h2>{t("ریتم یادگیری این هفته", "This week’s learning rhythm")}</h2>
            <span className="tag">{t("نمونه", "Sample")}</span>
          </div>
          <div
            className="week"
            role="img"
            aria-label={t(
              "نمودار نمایشی فعالیت هفتگی",
              "Illustrative weekly activity chart",
            )}
          >
            {[30, 55, 40, 80, 100, 20, 60].map((h, i) => (
              <i key={i} style={{ height: `${h}%` }} />
            ))}
          </div>
          <div className="muted text-center">
            {t(
              "شنبه تا جمعه • فعالیت‌های فرضی",
              "Saturday to Friday • illustrative activity",
            )}
          </div>
        </Card>
      </div>
      <CourseDialog id={selected} onClose={() => setSelected(null)} />
    </>
  );
}
