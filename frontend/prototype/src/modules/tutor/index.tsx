import { useState, useRef, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { services } from "../../app/services";
import { Heading, Card } from "../../components/shared";
import { Button } from "../../components/ui/button";
export default function Tutor() {
  const { t, locale } = useI18n(),
    { messages, setMessages, setError } = useLearning();
  const [params] = useSearchParams();
  const [prompt, setPrompt] = useState(params.get("topic") ?? ""),
    [pending, setPending] = useState(false);
  const log = useRef<HTMLDivElement>(null);
  useEffect(() => {
    log.current?.scrollTo(0, log.current.scrollHeight);
  }, [messages]);
  async function ask(value: string) {
    if (!value.trim() || pending) return;
    setPending(true);
    setMessages((m) => [...m, { role: "user", text: value.trim() }]);
    setPrompt("");
    try {
      const reply = await services.tutor.reply(value, locale);
      setMessages((m) => [...m, { role: "assistant", text: reply }]);
    } catch {
      setError(
        t(
          "پاسخ مربی آماده نشد؛ پرسش باید بین ۱ تا ۶۰۰ نویسه باشد.",
          "Tutor reply failed. Use between 1 and 600 characters.",
        ),
      );
    } finally {
      setPending(false);
    }
  }
  return (
    <>
      <Heading
        title={t("مربی هوشمند شما", "Your learning tutor")}
        subtitle={t(
          "برای فهم عمیق‌تر، سؤال بپرسید و با مثال پیش بروید.",
          "Ask questions and explore examples for deeper understanding.",
        )}
      />
      <div className="grid cols">
        <Card>
          <span className="tag">✧ {t("مربی نیک‌وی", "NIKWAY tutor")}</span>
          <p className="notice">
            {t(
              "این مربی نمایشی است؛ پاسخ‌ها از پیش نوشته شده‌اند و به هوش مصنوعی یا اینترنت متصل نیستند.",
              "This is a mock tutor. Responses are prewritten; no AI model or internet connection is used.",
            )}
          </p>
          <div
            className="chat"
            role="log"
            aria-live="polite"
            aria-label={t("گفت‌وگو با مربی", "Tutor conversation")}
            ref={log}
          >
            <div className="bubble">
              {t(
                "سلام! من مربی نمایشی نیک‌وی هستم. امروز کدام مفهوم را با هم مرور کنیم؟",
                "Hello! I am the NIKWAY mock tutor. What shall we explore today?",
              )}
            </div>
            {messages.map((m, i) => (
              <div
                key={i}
                className={`bubble ${m.role === "user" ? "user" : ""}`}
              >
                {m.text}
              </div>
            ))}
          </div>
          <div className="filters">
            <Button
              variant="outline"
              onClick={() =>
                ask(t("تفکر سیستمی چیست؟", "What is systems thinking?"))
              }
            >
              {t("تفکر سیستمی چیست؟", "What is systems thinking?")}
            </Button>
            <Button
              variant="outline"
              onClick={() =>
                ask(
                  t(
                    "برای تحول دیجیتال از کجا شروع کنم؟",
                    "Where should digital transformation start?",
                  ),
                )
              }
            >
              {t("از کجا شروع کنم؟", "Where should I start?")}
            </Button>
          </div>
          <form
            className="chat-form"
            onSubmit={(e) => {
              e.preventDefault();
              void ask(prompt);
            }}
          >
            <input
              aria-label={t("پیام به مربی", "Message to tutor")}
              placeholder={t("پرسش خود را بنویسید…", "Write your question…")}
              value={prompt}
              maxLength={600}
              required
              onChange={(e) => setPrompt(e.target.value)}
            />
            <Button disabled={pending || !prompt.trim()} type="submit">
              {t("ارسال", "Send")}
            </Button>
          </form>
        </Card>
        <Card>
          <h2>
            {t(
              "یک همراه در مسیر یادگیری",
              "A companion for your learning journey",
            )}
          </h2>
          <p className="muted">
            {t("موضوعات قابل آزمایش در این نمونه:", "Try these sample topics:")}
          </p>
          <div className="timeline">
            <p>{t("تفکر سیستمی و بازخورد", "Systems thinking and feedback")}</p>
            <p>
              {t("نقشهٔ راه تحول دیجیتال", "Digital transformation roadmaps")}
            </p>
            <p>
              {t("حل مسئله و گلوگاه تولید", "Problem solving and bottlenecks")}
            </p>
          </div>
          <Button asChild variant="outline">
            <Link to="/library">
              {t("مرور منابع دانش", "Explore resources")}
            </Link>
          </Button>
        </Card>
      </div>
    </>
  );
}
