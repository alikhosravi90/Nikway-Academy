import type { ReactNode } from "react";
import {
  ArrowUpLeft,
  BookOpen,
  CircleCheck,
  CircleDashed,
  ArrowUpRight,
} from "lucide-react";
import { Button } from "./button";
import { completion, type Course } from "../model";
export { Button };
export function Card({
  children,
  className = "",
  ...props
}: React.ComponentProps<"article">) {
  return (
    <article className={`card ${className}`} {...props}>
      {children}
    </article>
  );
}
export function Badge({
  children,
  tone = "neutral",
}: {
  children: ReactNode;
  tone?: "neutral" | "success" | "warning";
}) {
  return <span className={`badge badge-${tone}`}>{children}</span>;
}
export function Progress({ value, label }: { value: number; label: string }) {
  return (
    <div className="progress-block">
      <div className="progress-label">
        <span>{label}</span>
        <bdi>{value}%</bdi>
      </div>
      <progress
        max={100}
        value={Math.min(100, Math.max(0, value))}
        aria-label={label}
      />
    </div>
  );
}
export function Empty({
  title,
  children,
  action,
}: {
  title: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <CircleDashed size={32} aria-hidden="true" />
      <h2>{title}</h2>
      <p>{children}</p>
      {action}
    </div>
  );
}
export function PageHeading({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="page-heading">
      <div>
        {eyebrow && <p className="eyebrow">{eyebrow}</p>}
        <h1 tabIndex={-1}>{title}</h1>
        {description && <p className="muted">{description}</p>}
      </div>
      {action}
    </div>
  );
}
export function CourseCard({
  course,
  onOpen,
  en = false,
}: {
  course: Course;
  onOpen: () => void;
  en?: boolean;
}) {
  return (
    <Card className="course-card">
      <div className="card-topline">
        <span className="icon-tile">
          <BookOpen size={24} aria-hidden="true" />
        </span>
        <Badge tone={course.enrolled ? "success" : "neutral"}>
          {course.enrolled
            ? en
              ? "Enrolled"
              : "ثبت‌نام شده"
            : en
              ? "Academy course"
              : "دوره آموزشی"}
        </Badge>
      </div>
      <h2 dir="auto">{course.title}</h2>
      <p dir="auto">{course.description}</p>
      <Progress
        value={completion(course)}
        label={
          en
            ? `${course.completed_lessons.length} of ${course.lessons.length} lessons`
            : `${course.completed_lessons.length} از ${course.lessons.length} درس`
        }
      />
      <Button variant="outline" onClick={onOpen}>
        {en ? "View course" : "مشاهده دوره"}
        {en ? (
          <ArrowUpRight aria-hidden="true" />
        ) : (
          <ArrowUpLeft aria-hidden="true" />
        )}
      </Button>
    </Card>
  );
}
export function CompletionIcon({ done }: { done: boolean }) {
  return done ? (
    <CircleCheck aria-label="تکمیل شده" className="success" size={20} />
  ) : (
    <CircleDashed aria-label="تکمیل نشده" size={20} />
  );
}
