import seed from "./catalog.json";
import { useI18n } from "../i18n/provider";
const enCourses = [
  {
    title: "Systems thinking in organizations",
    cat: "Management",
    desc: "From observing problems to discovering patterns and feedback loops",
    time: "2 hours",
    skill: "Systems thinking",
  },
  {
    title: "Designing digital transformation",
    cat: "Digital transformation",
    desc: "Turn organizational vision into an actionable roadmap",
    time: "3 hours",
    skill: "Digital transformation",
  },
  {
    title: "Lean problem solving",
    cat: "Operations",
    desc: "Find root causes, test hypotheses and keep learning",
    time: "90 minutes",
    skill: "Problem solving",
  },
];
const enResources = [
  {
    title: "A guide to feedback loops",
    kind: "Guide",
    skill: "Systems thinking",
    body: "Examine system behavior over time. Identify key variables and the direction of their influence. Then find reinforcing and balancing loops.",
  },
  {
    title: "Digital transformation canvas",
    kind: "Template",
    skill: "Digital transformation",
    body: "Four columns: current state, desired outcome, initiatives and success measures. Assign an owner and a testable hypothesis to every initiative.",
  },
  {
    title: "Case study: the production bottleneck",
    kind: "Case study",
    skill: "Problem solving",
    body: "In a hypothetical production line, increased work in progress has lengthened lead time. Capacity analysis shows packaging is the bottleneck.",
  },
  {
    title: "Stakeholder interview guide",
    kind: "Guide",
    skill: "Change leadership",
    body: "Ask about actual experiences and the most recent example of a problem. Separate observation from interpretation and record conflicting stakeholder needs.",
  },
];
export type Course = (typeof seed.courses)[number];
export type Resource = (typeof seed.resources)[number];
export function useCatalog() {
  const { locale } = useI18n();
  return locale === "fa"
    ? seed
    : {
        courses: seed.courses.map((c, i) => ({ ...c, ...enCourses[i] })),
        resources: seed.resources.map((r, i) => ({ ...r, ...enResources[i] })),
        skills: [
          "Systems thinking",
          "Digital transformation",
          "Problem solving",
          "Change leadership",
          "Data analysis",
          "Knowledge management",
        ],
      };
}
