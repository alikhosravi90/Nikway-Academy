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

export function Objectives({ metadata }: { metadata?: CourseMetadata }) {
  if (!metadata?.objectives?.length) return null;
  return (
    <section className="learning-guidance" aria-label="هدف‌های یادگیری">
      <h3>هدف‌های یادگیری</h3>
      <ul>
        {metadata.objectives.map((objective) => (
          <li key={objective.id}>
            <p dir="auto">{objective.description}</p>
            <p className="muted" dir="auto">
              شواهد یادگیری: {objective.evidence}
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
}: {
  metadata?: LessonMetadata;
  objectives?: Objective[];
}) {
  if (!metadata) return null;
  const linked =
    objectives?.filter((o) => metadata.objectiveIds?.includes(o.id)) || [];
  return (
    <>
      {linked.length > 0 && (
        <p className="muted" dir="auto">
          هدف این درس: {linked.map((o) => o.description).join("؛ ")}
        </p>
      )}
      {metadata.practice && (
        <section className="learning-guidance" aria-label="تمرین درس">
          <h4>تمرین درس</h4>
          <p className="text-content" dir="auto">
            {metadata.practice.prompt}
          </p>
          <h4>خروجی مورد انتظار</h4>
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
}: {
  metadata?: CourseMetadata;
}) {
  if (!metadata?.assessment) return null;
  return (
    <section className="learning-guidance" aria-label="راهنمای تکلیف">
      <h3>راهنمای تکلیف</h3>
      <p className="text-content" dir="auto">
        {metadata.assessment.prompt}
      </p>
      <p>
        طول پاسخ: {metadata.assessment.minCharacters.toLocaleString("fa")} تا{" "}
        {metadata.assessment.maxCharacters.toLocaleString("fa")} نویسه
      </p>
      {metadata.rubric && (
        <details>
          <summary>معیارهای بازبینی انسانی</summary>
          <p className="muted">
            این معیارها راهنمای بازخورد بازبین هستند؛ در این نسخه نمره عددی ثبت
            نمی‌شود.
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
