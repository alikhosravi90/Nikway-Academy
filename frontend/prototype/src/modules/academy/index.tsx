import { useState } from "react";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { useCatalog } from "../../data/catalog";
import { completion } from "../../domain/model";
import { Heading, Card, Progress } from "../../components/shared";
import { CourseDialog } from "../../components/course";
import { Button } from "../../components/ui/button";
export default function Academy() {
  const { t, num } = useI18n(),
    { state } = useLearning(),
    { courses } = useCatalog();
  const [query, setQuery] = useState(""),
    [category, setCategory] = useState<number | null>(null),
    [selected, setSelected] = useState<number | null>(null);
  const filtered = courses.filter(
    (c) =>
      (category === null || category === c.id) &&
      c.title.includes(query.trim()),
  );
  return (
    <>
      <Heading
        title={t("آکادمی نیک‌وی", "NIKWAY Academy")}
        subtitle={t(
          "مسیرهای یادگیری متصل به مسائل واقعی سازمان.",
          "Learning paths connected to real organizational challenges.",
        )}
      />
      <div className="filters">
        <input
          aria-label={t("جست‌وجوی دوره", "Search courses")}
          placeholder={t("جست‌وجوی دوره…", "Search courses…")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button
          variant={category === null ? "default" : "outline"}
          aria-pressed={category === null}
          onClick={() => setCategory(null)}
        >
          {t("همه", "All")}
        </Button>
        {courses.map((c) => (
          <Button
            key={c.id}
            variant={category === c.id ? "default" : "outline"}
            aria-pressed={category === c.id}
            onClick={() => setCategory(c.id)}
          >
            {c.cat}
          </Button>
        ))}
      </div>
      <div className="grid cards">
        {filtered.map((c) => (
          <Card key={c.id} data-testid="course-card">
            <div className="cover" aria-hidden>
              {c.icon}
            </div>
            <span className="tag">{c.cat}</span>
            <h3>{c.title}</h3>
            <p className="muted">{c.desc}</p>
            <div className="muted">
              {num(c.lessons)} {t("درس", "lessons")} • {c.time}
            </div>
            <Progress
              label={c.title}
              value={completion(state, c.id, c.lessons)}
            />
            <div className="flex">
              <span className="small">
                {num(completion(state, c.id, c.lessons))}%{" "}
                {t("پیشرفت", "complete")}
              </span>
              <Button onClick={() => setSelected(c.id)}>
                {t("ورود به دوره", "Open course")}
              </Button>
            </div>
          </Card>
        ))}
      </div>
      {!filtered.length && (
        <p className="empty" role="status">
          {t("دوره‌ای پیدا نشد", "No courses found")}
        </p>
      )}
      <CourseDialog id={selected} onClose={() => setSelected(null)} />
    </>
  );
}
