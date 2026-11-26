import type { CourseMetadata, LessonMetadata } from "./course-content";
export type Course = {
  id: string;
  title: string;
  description: string;
  metadata?: CourseMetadata;
  lessons: {
    id: string;
    title: string;
    content: string;
    position: number;
    metadata?: LessonMetadata;
  }[];
  completed_lessons: string[];
  enrolled: boolean;
};
export type Submission = {
  id: string;
  course_id?: string;
  content: string;
  status: string;
  feedback?: string;
  revision: number;
};
export type Workshop = {
  id: string;
  title: string;
  description?: string;
  registered?: boolean;
  starts_at?: string;
};
export type Identity = { sub: string; tenant_id: string; role: string };
export type MoodleOverview = {
  enabled: boolean;
  source?: string;
  url?: string;
  progress_sync?: boolean;
  courses?: {
    id: number;
    title: string;
    url: string;
    progress: number | null;
    modules: {
      id: number;
      title: string;
      type: string;
      url: string;
      completion: number | null;
    }[];
  }[];
};
export type PageId =
  | "dashboard"
  | "courses"
  | "workspace"
  | "path"
  | "services"
  | "progress"
  | "projects"
  | "library"
  | "profile"
  | "admin"
  | "workshops"
  | "review"
  | "kit";
export type Preferences = {
  locale: "fa" | "en";
  theme: "light" | "dark";
  variant: "jade" | "ink" | "paper";
  solid: boolean;
  quiet: boolean;
};
export const defaultPreferences: Preferences = {
  locale: "fa",
  theme: "light",
  variant: "jade",
  solid: false,
  quiet: false,
};
export function readPreferences(): Preferences {
  try {
    const p = JSON.parse(localStorage.getItem("nikway-preferences") || "{}");
    return {
      locale: p.locale === "en" ? "en" : "fa",
      theme: p.theme === "dark" ? "dark" : "light",
      variant: ["ink", "paper"].includes(p.variant) ? p.variant : "jade",
      solid: p.solid === true,
      quiet: p.quiet === true,
    };
  } catch {
    return defaultPreferences;
  }
}
export function completion(c: Course) {
  return c.lessons.length
    ? Math.round(
        (c.completed_lessons.filter((id) => c.lessons.some((l) => l.id === id))
          .length /
          c.lessons.length) *
          100,
      )
    : 0;
}
export function safeMoodleUrl(
  value: string | undefined,
  base: string | undefined,
) {
  try {
    if (!value || !base) return undefined;
    const u = new URL(value),
      b = new URL(base);
    return u.origin === b.origin &&
      u.protocol === "http:" &&
      u.hostname === "localhost" &&
      !u.username &&
      !u.password
      ? u.href
      : undefined;
  } catch {
    return undefined;
  }
}
