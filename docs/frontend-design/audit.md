# Frontend design audit

Date: 2026-11-26. Baseline: `cd60f98`. Scope: read-only repository and primary-source review; implementation and runtime tests have separate evidence.

## Existing architecture and reusable assets

The operational application is React/Vite in `frontend/src/main.tsx`, with bearer-token API requests, Keycloak PKCE, tenant-authorized Academy learning mutations and a bounded Moodle launch. Preserve those actions and API authorization. `frontend/src/course-content.tsx` renders portable educational content. `frontend/src/operational.css` and `legacy.css` contain the existing teal identity. Existing Noto fonts remain available as fallback assets.

The preserved `frontend/prototype` contains shared Card, Heading, Progress, CourseRow, Modal and shadcn-derived Button/Dialog, a ten-module registry, RTL/i18n and design tokens. These are reusable patterns, not operational data: its Dexie repository, catalog fixtures and mock tutor must not enter the operational build. Port pure presentation selectively; preserve historical prototype files.

Architecture authority: `architecture/v0.2/05-design-system.md` and `adaptive-experience.md` are proposed targets. The implemented local subset does not certify the complete target. `docs/security-content-contract.md` pins adjacent Learning Engineering and Content Factory sources and documents incompatible wire schemas. Retain this boundary; do not present those services as connected.

GitHub read-only inventory (`gh repo list alikhosravi90 --limit 100`) found Nikway-Academy among names containing academy/learn/content. No separately named Learning Engineering/Content Factory repository was identified in that bounded inventory. Their pinned local crosswalk is evidence, not a fresh remote source audit. GitHub reports no repository-level license for Academy; no claim of public redistribution rights is made.

## Compatibility and licensing

Installed package manifests in the existing checkout were inspected; versions agree with the lockfile:

| Package | Version | License | Decision |
| --- | --- | --- | --- |
| React | 19.3.1 | MIT | Keep |
| Vite | 8.3.8 | MIT | Keep; Node ^20.19 or >=22.12 |
| TypeScript | 7.0.2 | Apache-2.0 | Keep |
| Tailwind CSS | 4.3.5 | MIT | Keep |
| Radix UI | 1.8.1 | MIT | Reuse existing primitives |
| Lucide React | 1.80.0 | ISC | Reuse icon system |
| vite-plugin-pwa | 2.0.0 | MIT | Existing dependency; no private-data cache |
| Vazirmatn | Font asset version to be pinned by implementation | SIL OFL 1.1 | Self-host with upstream license |

[Vazirmatn upstream license](https://github.com/rastikerdar/vazirmatn/blob/master/OFL.txt). No new Next.js server: migration would replace the validated static SPA deployment without a demonstrated requirement. Storybook is optional preferred tooling, not an accessibility gate; a local component gallery can document the UI kit without introducing an unverified toolchain dependency. Any later Storybook installation requires its actual peer-dependency/build verification.

## Primary-source benchmark

| Platform | Observed documented pattern | NIKWAY design inference |
| --- | --- | --- |
| Khan Academy | Dashboard separates assigned work and mastery; queue prioritizes due work | Put one next learning action before secondary metrics; keep completion separate from mastery |
| Coursera Guided Projects | A project presents instructor guidance beside a work area | Pair lesson guidance with the learner task on wide screens; stack on mobile |
| Moodle | My courses filters and sorts enrolled courses; activity-completion percentages are not course-completion proof | Filter the catalog; label the actual progress measure and source |

Sources reviewed: [Khan student dashboard](https://support.khanacademy.org/hc/en-us/articles/46935588089997-How-do-I-use-the-student-dashboard-in-Khan-Academy), [Coursera project example](https://www.coursera.org/projects/introduction-project-management), [Moodle course overview](https://docs.moodle.org/503/en/Course_overview). This is a documented-pattern benchmark, not a timed comparative usability study or pixel reproduction.

## Preserved boundaries

No fictional streaks, learner counts, certifications, AI replies or synchronized grades. Missing services get explicit unavailable states. A Moodle launch link alone is not verified Web Services integration. New API reads must be exercised against the installed instance and constrained by current authenticated tenant/subject. Server credentials never enter the browser. Production OIDC and grade/revocation synchronization risks from the Moodle baseline remain open unless separately evidenced as fixed.
