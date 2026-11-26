import { useState } from "react";
import { Button, Card, Progress, PageHeading, Empty } from "./components/ui";
import { Objectives, Practice, AssessmentGuidance } from "./course-content";
import { api } from "./api";
import { completion, type Course, type Submission } from "./model";
type Act = (fn: () => Promise<unknown>) => Promise<void>;
export function LearningWorkspace({
  course,
  busy,
  act,
  back,
  en,
}: {
  course: Course | undefined;
  busy: boolean;
  act: Act;
  back: () => void;
  en: boolean;
}) {
  const [content, setContent] = useState("");
  if (!course)
    return (
      <Empty
        title={en ? "Choose your next course" : "دوره بعدی خود را انتخاب کنید"}
        action={
          <Button onClick={back}>
            {en ? "Browse courses" : "مشاهده دوره‌ها"}
          </Button>
        }
      >
        {en
          ? "Your learning space opens with a course."
          : "فضای یادگیری با انتخاب یک دوره آماده می‌شود."}
      </Empty>
    );
  return (
    <>
      <PageHeading
        eyebrow="LEARNING WORKSPACE"
        title={course.title}
        description={course.description}
        action={
          <Button variant="outline" onClick={back}>
            {en ? "Back to courses" : "بازگشت به دوره‌ها"}
          </Button>
        }
      />
      <div className="learning-layout">
        <Card className="reading-surface">
          <Objectives metadata={course.metadata} />
          {!course.enrolled ? (
            <Button
              disabled={busy}
              onClick={() => act(() => api(`/courses/${course.id}/enroll`, {}))}
            >
              {en ? "Enroll in course" : "ثبت‌نام در دوره"}
            </Button>
          ) : (
            <>
              {course.lessons.map((lesson, index) => (
                <section
                  className="lesson"
                  key={lesson.id}
                  id={`lesson-${lesson.id}`}
                >
                  <p className="eyebrow">
                    {en ? "LESSON" : "درس"} {index + 1}
                  </p>
                  <h2 dir="auto">{lesson.title}</h2>
                  <p className="text-content" dir="auto">
                    {lesson.content}
                  </p>
                  <Practice
                    metadata={lesson.metadata}
                    objectives={course.metadata?.objectives}
                  />
                  <Button
                    variant={
                      course.completed_lessons.includes(lesson.id)
                        ? "secondary"
                        : "default"
                    }
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
                      ? en
                        ? "Completed"
                        : "تکمیل شده"
                      : en
                        ? "Mark lesson complete"
                        : "ثبت تکمیل درس"}
                  </Button>
                </section>
              ))}
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  void act(async () => {
                    await api(`/courses/${course.id}/submissions`, { content });
                    setContent("");
                  });
                }}
              >
                <AssessmentGuidance metadata={course.metadata} />
                <h2>{en ? "Submit assignment" : "ارسال تکلیف"}</h2>
                <label htmlFor="submission">
                  {en
                    ? "Your response and practice evidence"
                    : "متن پاسخ و شواهد تمرین"}
                </label>
                <textarea
                  id="submission"
                  required
                  minLength={course.metadata?.assessment?.minCharacters ?? 20}
                  maxLength={
                    course.metadata?.assessment?.maxCharacters ?? 10000
                  }
                  value={content}
                  onChange={(e) => setContent(e.target.value)}
                  aria-describedby="submission-help"
                />
                <p id="submission-help" className="muted">
                  {course.completed_lessons.length < course.lessons.length
                    ? en
                      ? "Complete all lessons before submitting."
                      : "برای ارسال تکلیف ابتدا همه درس‌ها را تکمیل کنید."
                    : en
                      ? "Your reviewer will provide feedback. Drafts are kept only in this open page."
                      : "بازبین به شما بازخورد می‌دهد. پیش‌نویس فقط در همین صفحه باز نگه داشته می‌شود."}
                </p>
                <Button
                  disabled={
                    busy ||
                    content.trim().length <
                      (course.metadata?.assessment?.minCharacters ?? 20) ||
                    content.trim().length >
                      (course.metadata?.assessment?.maxCharacters ?? 10000) ||
                    course.completed_lessons.length < course.lessons.length
                  }
                >
                  {en ? "Send for review" : "ارسال برای بازبینی"}
                </Button>
              </form>
            </>
          )}
        </Card>
        <div className="lesson-outline">
          <Card>
            <h2>{en ? "Your progress" : "پیشرفت شما"}</h2>
            <Progress
              value={completion(course)}
              label={en ? "Lessons completed" : "تکمیل درس‌ها"}
            />
            <p className="muted">
              {en
                ? "Lesson completion does not mean assessment passed."
                : "تکمیل درس به معنی قبولی در ارزیابی نیست."}
            </p>
            <ol>
              {course.lessons.map((l) => (
                <li key={l.id}>
                  <a href={`#lesson-${l.id}`}>{l.title}</a>
                </li>
              ))}
            </ol>
          </Card>
        </div>
      </div>
    </>
  );
}
export function Submissions({
  items,
  courses,
  review,
  busy,
  act,
  en,
}: {
  items: Submission[];
  courses: Course[];
  review: boolean;
  busy: boolean;
  act: Act;
  en: boolean;
}) {
  const [feedback, setFeedback] = useState<Record<string, string>>({});
  return (
    <>
      {items.length === 0 && (
        <Empty title={en ? "No submissions yet" : "هنوز تکلیفی ثبت نشده"}>
          {en
            ? "Complete a course and submit your work to receive feedback."
            : "درس‌ها را تکمیل و تمرین خود را برای دریافت بازخورد ارسال کنید."}
        </Empty>
      )}
      {items.map((s) => (
        <Card key={s.id} className="submission-card">
          <h2 dir="auto">
            {courses.find((c) => c.id === s.course_id)?.title ||
              (en ? "Learning assignment" : "تکلیف یادگیری")}
          </h2>
          <p>
            {en ? "Status:" : "وضعیت:"} <strong>{s.status}</strong>
          </p>
          <p className="text-content" dir="auto">
            {s.content}
          </p>
          {s.feedback && (
            <div className="feedback">
              <h3>{en ? "Reviewer feedback" : "بازخورد"}</h3>
              <p dir="auto">{s.feedback}</p>
            </div>
          )}
          {review && (
            <>
              <AssessmentGuidance
                metadata={courses.find((c) => c.id === s.course_id)?.metadata}
              />
              <label htmlFor={"feedback-" + s.id}>
                {en ? "Reviewer feedback" : "بازخورد بازبین"}
              </label>
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
                {[
                  ["accepted", en ? "Accept assignment" : "پذیرش تکلیف"],
                  [
                    "revision_requested",
                    en ? "Request revision" : "درخواست اصلاح",
                  ],
                ].map(([decision, label]) => (
                  <Button
                    key={decision}
                    variant={decision === "accepted" ? "default" : "outline"}
                    disabled={busy || (feedback[s.id]?.trim().length || 0) < 3}
                    onClick={() =>
                      act(() =>
                        api(`/submissions/${s.id}/review`, {
                          decision,
                          expected_revision: s.revision,
                          feedback: feedback[s.id],
                        }),
                      )
                    }
                  >
                    {label}
                  </Button>
                ))}
              </div>
            </>
          )}
        </Card>
      ))}
    </>
  );
}
