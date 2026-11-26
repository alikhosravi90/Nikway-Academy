export type Objective = {
  id: string;
  description: string;
  bloom: string;
  evidence: string;
};
export type CourseMetadata = {
  objectives?: Objective[];
  assessment?: {
    mode: "human_review";
    prompt: string;
    minCharacters: number;
    maxCharacters: number;
    rubricId: string;
  };
  rubric?: {
    id: string;
    version: string;
    criteria: {
      id: string;
      description: string;
      objectiveIds: string[];
      maxScore: number;
      anchors: { score: number; description: string }[];
    }[];
    passScore: number;
    requiresHumanReview: true;
  };
};
export type LessonMetadata = {
  objectiveIds?: string[];
  practice?: { prompt: string; deliverable: string };
};

export function Objectives({
  metadata,
  en = false,
}: {
  metadata?: CourseMetadata;
  en?: boolean;
}) {
  if (!metadata?.objectives?.length) return null;
  return (
    <section
      className="learning-guidance"
      aria-label={en ? "Learning objectives" : "هدف‌های یادگیری"}
    >
      <h3 lang={en ? "en" : "fa"}>
        {en ? "Learning objectives" : "هدف‌های یادگیری"}
      </h3>
      <ul>
        {metadata.objectives.map((objective) => (
          <li key={objective.id}>
            <p dir="auto">{objective.description}</p>
            <p className="muted" dir="auto">
              <span lang={en ? "en" : "fa"}>
                {en ? "Learning evidence: " : "شواهد یادگیری: "}
              </span>
              {objective.evidence}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
export function Practice({
  metadata,
  objectives,
  en = false,
}: {
  metadata?: LessonMetadata;
  objectives?: Objective[];
  en?: boolean;
}) {
  if (!metadata) return null;
  const linked =
    objectives?.filter((o) => metadata.objectiveIds?.includes(o.id)) || [];
  return (
    <>
      {linked.length > 0 && (
        <p className="muted" dir="auto">
          <span lang={en ? "en" : "fa"}>
            {en ? "Lesson objective: " : "هدف این درس: "}
          </span>
          {linked.map((o) => o.description).join(en ? "; " : "؛ ")}
        </p>
      )}
      {metadata.practice && (
        <section
          className="learning-guidance"
          aria-label={en ? "Lesson practice" : "تمرین درس"}
        >
          <h4 lang={en ? "en" : "fa"}>
            {en ? "Lesson practice" : "تمرین درس"}
          </h4>
          <p className="text-content" dir="auto">
            {metadata.practice.prompt}
          </p>
          <h4 lang={en ? "en" : "fa"}>
            {en ? "Expected deliverable" : "خروجی مورد انتظار"}
          </h4>
          <p className="text-content" dir="auto">
            {metadata.practice.deliverable}
          </p>
        </section>
      )}
    </>
  );
}
export function AssessmentGuidance({
  metadata,
  en = false,
}: {
  metadata?: CourseMetadata;
  en?: boolean;
}) {
  if (!metadata?.assessment) return null;
  return (
    <section
      className="learning-guidance"
      aria-label={en ? "Assignment guidance" : "راهنمای تکلیف"}
    >
      <h3 lang={en ? "en" : "fa"}>
        {en ? "Assignment guidance" : "راهنمای تکلیف"}
      </h3>
      <p className="text-content" dir="auto">
        {metadata.assessment.prompt}
      </p>
      <p lang={en ? "en" : "fa"}>
        {en ? "Response length: " : "طول پاسخ: "}
        {metadata.assessment.minCharacters.toLocaleString(en ? "en" : "fa")}
        {en ? " to " : " تا "}
        {metadata.assessment.maxCharacters.toLocaleString(en ? "en" : "fa")}
        {en ? " characters" : " نویسه"}
      </p>
      {metadata.rubric && (
        <details>
          <summary lang={en ? "en" : "fa"}>
            {en ? "Human review criteria" : "معیارهای بازبینی انسانی"}
          </summary>
          <p className="muted" lang={en ? "en" : "fa"}>
            {en
              ? "These criteria guide reviewer feedback; this version does not record a numeric score."
              : "این معیارها راهنمای بازخورد بازبین هستند؛ در این نسخه نمره عددی ثبت نمی‌شود."}
          </p>
          {metadata.rubric.criteria.map((criterion) => (
            <section className="rubric-criterion" key={criterion.id}>
              <h4 dir="auto">{criterion.description}</h4>
              <ul>
                {criterion.anchors.map((anchor, index) => (
                  <li key={index} dir="auto">
                    {anchor.description}
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </details>
      )}
    </section>
  );
}
