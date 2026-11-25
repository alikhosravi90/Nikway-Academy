import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { useCatalog } from "../../data/catalog";
import { competencyLevel } from "../../domain/model";
import { Heading, Modal, Progress } from "../../components/shared";
import { CourseDialog } from "../../components/course";
import { Button } from "../../components/ui/button";
export default function Competency() {
  const { t, num } = useI18n(),
    { state } = useLearning(),
    { skills, courses } = useCatalog(),
    navigate = useNavigate();
  const [selected, setSelected] = useState<number | null>(null),
    [course, setCourse] = useState<number | null>(null);
  return (
    <>
      <Heading
        title={t("نقشه شایستگی", "Competency map")}
        subtitle={t(
          "فاصلهٔ امروز تا نقش فردا؛ با شواهد یادگیری و تمرین.",
          "From today’s skills to tomorrow’s role, with learning and practice evidence.",
        )}
      />
      <p className="notice">
        {t(
          "سطوح این نقشه فرضی هستند و ارزیابی معتبر حرفه‌ای محسوب نمی‌شوند. تکمیل دوره‌ها و تمرین روی نمونه اثر می‌گذارد.",
          "These levels are illustrative, not a professional assessment. Course and practice completion affect the sample.",
        )}
      </p>
      <div className="filters">
        <span className="tag">
          {t(
            "نقش هدف: مشاور تحول سازمانی",
            "Target role: Organizational transformation consultant",
          )}
        </span>
        <span className="muted">
          {t(
            "سطوح: آشنایی ← کاربرد ← تسلط ← راهبری",
            "Levels: Awareness → Application → Mastery → Leadership",
          )}
        </span>
      </div>
      <div className="grid skills">
        {skills.map((name, id) => {
          const level = competencyLevel(state, id);
          return (
            <button
              className="card skill"
              key={name}
              onClick={() => setSelected(id)}
            >
              <div className="flex">
                <h3>{name}</h3>
                <span className="tag">
                  {t("سطح", "Level")} {num(level)} / {num(4)}
                </span>
              </div>
              <Progress value={level * 25} label={name} />
              <div className="flex muted">
                <span>{t("هدف: سطح ۴", "Target: level 4")}</span>
                <span>
                  {t("شواهد و مسیر رشد ←", "Evidence and growth path →")}
                </span>
              </div>
            </button>
          );
        })}
      </div>
      {selected !== null && (
        <Modal
          open
          onClose={() => setSelected(null)}
          title={skills[selected]}
          description={t("شایستگی نمونه", "Sample competency")}
        >
          <p>
            {t("سطح فعلی", "Current level")}:{" "}
            {num(competencyLevel(state, selected))} / {num(4)}
          </p>
          <h3>{t("شواهد نمایشی", "Sample evidence")}</h3>
          <p>
            {selected < 3
              ? `${num(state.done[selected])} ${t("درس تکمیل‌شده در", "lessons completed in")} «${courses[selected].title}»`
              : t(
                  "سطح اولیهٔ فرضی؛ هنوز شاهدی ثبت نشده است.",
                  "Illustrative initial level; no evidence recorded yet.",
                )}
            {selected === 2 &&
              ` • ${num(state.sim)} ${t("تمرین تکمیل‌شده", "completed simulations")}`}
          </p>
          <h3>{t("گام پیشنهادی", "Suggested next step")}</h3>
          <p>
            {t(
              "یک مفهوم را بیاموزید، در سناریوی عملی به‌کار ببرید و نتیجه را بازبینی کنید.",
              "Learn a concept, apply it to a scenario, and reflect on the result.",
            )}
          </p>
          <Button
            onClick={() => {
              const id = selected;
              setSelected(null);
              if (id < 3) setCourse(id);
              else navigate("/academy");
            }}
          >
            {t("ورود به مسیر یادگیری", "Open learning path")}
          </Button>
        </Modal>
      )}
      <CourseDialog id={course} onClose={() => setCourse(null)} />
    </>
  );
}
