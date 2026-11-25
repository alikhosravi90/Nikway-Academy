import { useRef } from "react";
import { Link } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { simulate } from "../../domain/model";
import { Heading, Card } from "../../components/shared";
import { Button } from "../../components/ui/button";
export default function Lab() {
  const { t, num } = useI18n(),
    { act, pending, sessions, setSessions } = useLearning();
  const initial = useRef({
    step: 0,
    choice: null as number | null,
    attempt: crypto.randomUUID() as string,
  });
  const session =
    (sessions.lab as typeof initial.current | undefined) ?? initial.current;
  const { step, choice, attempt } = session;
  const patch = (p: Partial<typeof session>) =>
    setSessions((prev) => ({
      ...prev,
      lab: {
        ...((prev.lab as typeof session | undefined) ?? initial.current),
        ...p,
      },
    }));
  const setStep = (step: number) => patch({ step });
  const setChoice = (choice: number | null) => patch({ choice });
  const setAttempt = (attempt: string) => patch({ attempt });
  const result = choice === null ? null : simulate(choice);
  const retry = () => {
    setStep(1);
    setChoice(null);
    setAttempt(crypto.randomUUID());
  };
  return (
    <>
      <Heading
        title={t("آزمایشگاه شبیه‌سازی", "Simulation lab")}
        subtitle={t(
          "تصمیم بگیرید، پیامد را ببینید و دوباره امتحان کنید.",
          "Decide, explore the outcome, and try again.",
        )}
      />
      <div className="grid cols">
        <Card>
          {step === 0 ? (
            <>
              <h2>
                {t(
                  "گلوگاه تولید را پیدا کنید",
                  "Find the production bottleneck",
                )}
              </h2>
              <p>
                {t(
                  "مدیر کارخانه می‌خواهد خروجی خط را از ۶۰ به ۸۰ واحد در ساعت برساند. بودجه فقط برای بهبود یک مرحله کافی است. کدام تصمیم بیشترین اثر را دارد؟",
                  "The factory manager wants to increase output from 60 to 80 units per hour. There is budget to improve only one stage. Which decision has the greatest impact?",
                )}
              </p>
              <span className="tag">
                {t("۱ تصمیم • حدود ۳ دقیقه", "1 decision • about 3 minutes")}
              </span>
              <p>
                <Button onClick={() => setStep(1)}>
                  {t("شروع شبیه‌سازی", "Start simulation")}
                </Button>
              </p>
            </>
          ) : step === 1 ? (
            <>
              <div className="muted">
                {t(
                  "مرحلهٔ ۱ از ۲ • انتخاب اقدام",
                  "Step 1 of 2 • Choose an action",
                )}
              </div>
              <h2>
                {t(
                  "بودجه را به کدام مرحله اختصاص می‌دهید؟",
                  "Which stage should receive the budget?",
                )}
              </h2>
              <div className="lab-options">
                {[
                  t(
                    "افزایش ظرفیت آماده‌سازی به ۱۳۰",
                    "Increase preparation capacity to 130",
                  ),
                  t(
                    "افزایش ظرفیت مونتاژ به ۸۵",
                    "Increase assembly capacity to 85",
                  ),
                  t(
                    "افزایش ظرفیت بسته‌بندی به ۱۲۰",
                    "Increase packaging capacity to 120",
                  ),
                ].map((text, i) => (
                  <Button
                    key={i}
                    variant={choice === i ? "default" : "outline"}
                    aria-pressed={choice === i}
                    onClick={() => setChoice(i)}
                  >
                    {text} {t("واحد / ساعت", "units / hour")}
                  </Button>
                ))}
              </div>
              <Button
                disabled={choice === null || pending}
                onClick={async () => {
                  if (
                    choice !== null &&
                    (await act({ type: "attempt", attemptId: attempt, choice }))
                  )
                    setStep(2);
                }}
              >
                {t("اجرای تصمیم", "Run decision")}
              </Button>
            </>
          ) : (
            result && (
              <>
                <span className="tag">
                  {t("مرحلهٔ ۲ از ۲ • بازخورد", "Step 2 of 2 • Feedback")}
                </span>
                <h2>
                  {result.success
                    ? t(
                        "تصمیم مؤثر؛ گلوگاه بهبود یافت",
                        "Effective decision: bottleneck improved",
                      )
                    : t(
                        "ظرفیت اضافه شد، خروجی تغییری نکرد",
                        "Capacity increased, output did not",
                      )}
                </h2>
                <div className="grid grid-cols-2 gap-4 my-5">
                  <Card>
                    <strong>{num(result.capacity)}</strong>
                    <p className="muted">
                      {t("ظرفیت خط / ساعت", "Line capacity / hour")}
                    </p>
                  </Card>
                  <Card>
                    <strong data-testid="delivery">
                      {num(result.delivery)}
                    </strong>
                    <p className="muted">
                      {t(
                        "تحویل با سقف تقاضا / ساعت",
                        "Delivery capped by demand / hour",
                      )}
                    </p>
                  </Card>
                </div>
                <p>
                  {result.success
                    ? t(
                        "با بهبود مونتاژ، ظرفیت خط به کمترین ظرفیت جدید، یعنی ۸۵ می‌رسد. با تقاضای ۸۰، تحویل ۸۰ واحد است.",
                        "Improving assembly raises line capacity to 85. With demand of 80, delivery is 80 units.",
                      )
                    : t(
                        "مونتاژ همچنان فقط ۶۰ واحد در ساعت ظرفیت دارد. افزایش ظرفیت مراحل دیگر این محدودیت را برطرف نمی‌کند.",
                        "Assembly still has a capacity of 60 units per hour. Improving other stages does not remove this constraint.",
                      )}
                </p>
                <p className="muted">
                  {t(
                    "نتیجهٔ این تمرین در داشبورد و نقشهٔ شایستگی ثبت شد.",
                    "This attempt is recorded in your dashboard and competency map.",
                  )}
                </p>
                <div className="filters">
                  <Button onClick={retry}>
                    {t("آزمایش تصمیم دیگر", "Try another decision")}
                  </Button>
                  <Button asChild variant="outline">
                    <Link to="/dashboard">
                      {t("مشاهدهٔ داشبورد", "View dashboard")}
                    </Link>
                  </Button>
                </div>
              </>
            )
          )}
        </Card>
        <Card>
          <span className="tag">
            {t(
              "سناریوی عملیاتی • سطح مقدماتی",
              "Operations scenario • Beginner",
            )}
          </span>
          <h2 className="mt-4">{t("کارخانهٔ فردا", "Tomorrow’s factory")}</h2>
          <p>
            {t(
              "یک خط تولید فرضی با سه مرحله و تقاضای ۸۰ واحد در ساعت.",
              "A fictional three-stage line with demand of 80 units per hour.",
            )}
          </p>
          <div className="timeline">
            <p>
              {t(
                "آماده‌سازی: ۱۰۰ واحد / ساعت",
                "Preparation: 100 units / hour",
              )}
            </p>
            <p>{t("مونتاژ: ۶۰ واحد / ساعت", "Assembly: 60 units / hour")}</p>
            <p>
              {t("بسته‌بندی: ۹۰ واحد / ساعت", "Packaging: 90 units / hour")}
            </p>
          </div>
          <p className="muted">
            {t(
              "فرض ساده‌سازی: نبود خرابی، ضایعات و تغییر محصول.",
              "Simplified assumptions: no breakdowns, scrap or changeovers.",
            )}
          </p>
          <Link className="link" to="/competency">
            {t(
              "شایستگی مرتبط: حل مسئله ←",
              "Related competency: problem solving →",
            )}
          </Link>
        </Card>
      </div>
    </>
  );
}
