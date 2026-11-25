import { useNavigate } from "react-router-dom";
import { useI18n } from "../i18n/provider";
import { useLearning } from "../app/provider";
import { useCatalog, type Course } from "../data/catalog";
import { completion } from "../domain/model";
import { Modal, Progress } from "./shared";
import { Button } from "./ui/button";
export function CourseRow({
  course: c,
  onOpen,
}: {
  course: Course;
  onOpen: () => void;
}) {
  const { state } = useLearning();
  const { num, t } = useI18n();
  return (
    <div className="course">
      <div className="thumb" aria-hidden>
        {c.icon}
      </div>
      <div className="course-info">
        <h3>{c.title}</h3>
        <div className="muted">
          {num(state.done[c.id])} {t("از", "of")} {num(c.lessons)}{" "}
          {t("درس", "lessons")} • {c.time}
        </div>
        <Progress value={completion(state, c.id, c.lessons)} label={c.title} />
      </div>
      <Button variant="outline" onClick={onOpen}>
        {t("ادامه ←", "Continue →")}
      </Button>
    </div>
  );
}
export function CourseDialog({
  id,
  onClose,
}: {
  id: number | null;
  onClose: () => void;
}) {
  const { courses } = useCatalog();
  const { state, act, pending, notice } = useLearning();
  const { t, num } = useI18n();
  const navigate = useNavigate();
  if (id === null) return null;
  const c = courses[id],
    done = state.done[id],
    complete = done >= c.lessons;
  const bodies = [
    t(
      "در یک سیستم، پیامد یک اقدام می‌تواند دوباره بر علت آن اثر بگذارد. برای مثال، تأخیر در تحویل ممکن است سفارش‌های اضطراری را افزایش دهد و این سفارش‌ها تأخیر بیشتری ایجاد کنند.",
      "The outcome of an action can feed back into its cause. Delivery delays can lead to emergency orders that create even more delays.",
    ),
    t(
      "ابتکارها را با توجه به ارزش مورد انتظار، امکان اجرا و وابستگی‌ها مقایسه کنید. ابتدا یک آزمایش کوچک طراحی کنید تا مهم‌ترین فرضیه روشن شود.",
      "Compare initiatives by expected value, feasibility and dependencies. Design a small experiment to test the most important assumption.",
    ),
    t(
      "پیش از پیشنهاد راه‌حل، جریان کار را مشاهده کنید. زمان انتظار، موجودی و ظرفیت هر مرحله را ثبت کنید و گلوگاه را از روی شواهد شناسایی کنید.",
      "Observe the workflow before proposing a solution. Record waiting time, inventory and stage capacity, then identify the bottleneck from evidence.",
    ),
  ];
  return (
    <Modal open onClose={onClose} title={c.title} description={c.desc}>
      <span className="tag">{c.skill}</span>
      <p className="notice">
        {t(
          "محتوای کوتاه نمونه؛ این بخش ویدئو یا دورهٔ واقعی نیست.",
          "Sample content only, not a full course or video.",
        )}
      </p>
      <h3>
        {complete
          ? t("مرور نهایی", "Final review")
          : `${t("درس", "Lesson")} ${num(done + 1)}: ${[t("حلقه‌های بازخورد", "Feedback loops"), t("اولویت‌بندی ابتکارها", "Prioritizing initiatives"), t("مشاهدهٔ فرایند", "Observing processes")][id]}`}
      </h3>
      <p>{bodies[id]}</p>
      <Progress value={completion(state, id, c.lessons)} label={c.title} />
      <p>
        {num(done)} {t("از", "of")} {num(c.lessons)}{" "}
        {t("درس تکمیل شده", "lessons completed")}
      </p>
      <div className="filters">
        {!complete ? (
          <Button
            disabled={pending}
            onClick={async () => {
              if (
                await act({ type: "complete", courseId: id, lessonIndex: done })
              ) {
                onClose();
                notice(
                  t(
                    "درس تکمیل شد و پیشرفت به‌روز شد",
                    "Lesson completed and progress updated",
                  ),
                );
              }
            }}
          >
            {t("تکمیل این درس ✓", "Complete lesson ✓")}
          </Button>
        ) : (
          <span className="tag">
            {t("دوره تکمیل شده ✓", "Course completed ✓")}
          </span>
        )}
        <Button
          variant="outline"
          onClick={() => {
            onClose();
            navigate(`/library?skill=${id}`);
          }}
        >
          {t("منابع مرتبط", "Related resources")}
        </Button>
        <Button
          variant="outline"
          onClick={() => {
            onClose();
            navigate("/lab");
          }}
        >
          {t("تمرین عملی", "Practice")}
        </Button>
      </div>
    </Modal>
  );
}
