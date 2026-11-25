import { useState } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import { useI18n } from "../../i18n/provider";
import { useLearning } from "../../app/provider";
import { useCatalog } from "../../data/catalog";
import { Heading, Card, Modal } from "../../components/shared";
import { Button } from "../../components/ui/button";
export default function Library() {
  const { t } = useI18n(),
    { state, act, pending } = useLearning(),
    { resources, skills } = useCatalog();
  const [params, setParams] = useSearchParams(),
    navigate = useNavigate();
  const [query, setQuery] = useState(""),
    [savedOnly, setSavedOnly] = useState(false),
    [selected, setSelected] = useState<number | null>(null);
  const skill = params.get("skill"),
    skillName = skill !== null ? skills[Number(skill)] : null;
  const filtered = resources.filter(
    (r) =>
      (!skillName || r.skill === skillName) &&
      (!savedOnly || state.saved.includes(r.id)) &&
      [r.title, r.kind, r.skill, r.body].join(" ").includes(query.trim()),
  );
  const resource = resources.find((r) => r.id === selected);
  return (
    <>
      <Heading
        title={t("کتابخانه دانش", "Knowledge library")}
        subtitle={t(
          "از یک ایده تا یک ابزار کاربردی؛ دانش را در کار به‌کار بگیرید.",
          "From ideas to practical tools. Put knowledge to work.",
        )}
      />
      <div className="filters">
        <input
          aria-label={t("جست‌وجوی منابع", "Search resources")}
          placeholder={t("جست‌وجو در منابع…", "Search resources…")}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <Button
          variant={savedOnly ? "default" : "outline"}
          aria-pressed={savedOnly}
          onClick={() => setSavedOnly(!savedOnly)}
        >
          {t("نشان‌شده‌ها", "Bookmarks")}
        </Button>
        {skillName && (
          <Button variant="secondary" onClick={() => setParams({})}>
            {skillName} ×
          </Button>
        )}
      </div>
      <div className="grid cards">
        {filtered.map((r) => (
          <Card key={r.id} data-testid="resource-card">
            <div className="cover" aria-hidden>
              {["▤", "▦", "◈", "☷"][r.id]}
            </div>
            <span className="tag">{r.kind}</span>
            <h3>{r.title}</h3>
            <p className="muted">
              {r.skill} • {t("محتوای تألیفی نمونه", "Sample authored content")}
            </p>
            <div className="flex">
              <Button onClick={() => setSelected(r.id)}>
                {t("مطالعه", "Read")}
              </Button>
              <Button
                variant="outline"
                disabled={pending}
                aria-pressed={state.saved.includes(r.id)}
                aria-label={
                  (state.saved.includes(r.id)
                    ? t("حذف نشان ", "Remove bookmark ")
                    : t("نشان کردن ", "Bookmark ")) + r.title
                }
                onClick={() => act({ type: "bookmark", resourceId: r.id })}
              >
                {state.saved.includes(r.id)
                  ? t("نشان‌شده ✓", "Saved ✓")
                  : t("نشان کردن ♧", "Bookmark ♧")}
              </Button>
            </div>
          </Card>
        ))}
      </div>
      {!filtered.length && (
        <p className="empty" role="status">
          {t("منبعی با این شرایط پیدا نشد.", "No matching resources found.")}
        </p>
      )}
      {resource && (
        <Modal
          open
          onClose={() => setSelected(null)}
          title={resource.title}
          description={`${resource.kind} • ${t("نمونه", "Sample")}`}
        >
          <p>{resource.body}</p>
          <h3>{t("تمرین کوتاه", "Quick exercise")}</h3>
          <p>
            {t(
              "یک مسئله از سازمان فرضی انتخاب کنید و این چارچوب را روی آن به‌کار ببرید. چه داده‌ای برای بررسی فرضیه نیاز دارید؟",
              "Choose a problem from a fictional organization and apply this framework. What data would you need to test the hypothesis?",
            )}
          </p>
          <Button
            onClick={() =>
              navigate(`/tutor?topic=${encodeURIComponent(resource.skill)}`)
            }
          >
            {t(
              "گفت‌وگو با مربی دربارهٔ این موضوع",
              "Discuss this topic with the tutor",
            )}
          </Button>
        </Modal>
      )}
    </>
  );
}
