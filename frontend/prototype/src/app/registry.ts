import { lazy } from "react";
export const modules = [
  {
    id: "dashboard",
    icon: "◫",
    name: ["داشبورد یادگیری", "Learning dashboard"],
    Component: lazy(() => import("../modules/dashboard")),
  },
  {
    id: "academy",
    icon: "▧",
    name: ["آکادمی", "Academy"],
    Component: lazy(() => import("../modules/academy")),
  },
  {
    id: "library",
    icon: "▤",
    name: ["کتابخانه دانش", "Knowledge library"],
    Component: lazy(() => import("../modules/library")),
  },
  {
    id: "tutor",
    icon: "✧",
    name: ["مربی هوشمند", "Mock tutor"],
    Component: lazy(() => import("../modules/tutor")),
  },
  {
    id: "competency",
    icon: "⌘",
    name: ["نقشه شایستگی", "Competency map"],
    Component: lazy(() => import("../modules/competency")),
  },
  {
    id: "lab",
    icon: "⚗",
    name: ["آزمایشگاه شبیه‌سازی", "Simulation lab"],
    Component: lazy(() => import("../modules/lab")),
  },
];
