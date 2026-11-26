# Frontend mission acceptance — 2026-11-26

**GO for local synthetic pilot review. PARTIAL for complete acceptance; NO-GO for production or a WCAG conformance claim.** Issue[#19](https://github.com/alikhosravi90/Nikway-Academy/issues/19). No merge or release authorized/performed.

## Implemented and verified

- Ten required screens plus workshops/reviewer workflow/UI kit. Search, filtering, course reading, enrolment, completion, submission, human review and preferences are functional against the existing server. AI Tutor deliberately shows unavailable status and non-AI reflection prompts. Administration respects roles; no new privileges.
- Three selectable token palettes (Focus Jade default, Studio Ink, Warm Paper), light/dark, RTL/LTR shell, Vazirmatn local fonts, bento composition, restrained navigation glass and opaque learning content. Explicit reduced-motion/transparency settings and OS preferences. Atomic Button/Badge/Progress/Card/Heading/search/course and responsive workspace patterns; Storybook build passes.
- Actual Moodle REST data through authenticated Academy membership and individual subject-bound tokens: learner/reviewer receive course6/five modules; tenantB disabled; anonymous401. No Moodle token in browser. Provider API is read-only and narrowly limited; unauthorized function denied. Progress is source-labeled and separate.
- Local application and Storybook build, typecheck,31 frontend unit tests,43 backend/content unit tests,5 role capability fixtures PASS.
- Four existing live browser regressions PASS: course delivery/submission/review/sign-out, forged/anonymous and tenant checks. Six independent real-login UI tests PASS: ten screens, light/dark×three palettes on profile/dashboard, RTL320/390, LTR preference persistence, keyboard trap/Escape, public-only offline fallback. Automated axe reports zero violations in these checks.
- Registry audit zero advisories; final API/web image package scans zero High/Critical with existing cached Trivy DB. Scans do not certify the full application or Moodle/plugin code.

Evidence: [verification](../../evidence/frontend-design/verification.json), [live API](../../evidence/frontend-design/api-live.json), [independent browser](../../evidence/frontend-design/design-playwright.json), [performance observations](../../evidence/frontend-design/browser-observations.json), [image scans](../../evidence/frontend-design/image-scan.json), [research](../../evidence/frontend-design/research.json).

## Findings corrected

Existing interface had measured contrast violations. New theme-transition interpolation briefly produced low-contrast button colors; semantic states and no color interpolation fix it. Mobile Escape initially attempted focus while the background was inert; post-render focus restoration now passes. Exact new preview logout redirect required a trailing slash; real logout regression now passes. Moodle reader-role capability drift now fails before assignment; overview response reads have size/course/module/elapsed-time bounds.

## Remaining gates and assumptions

Users are synthetic Academy learners/reviewers and the local device/Docker network is trusted. No comparative learner usability study or screen-reader/browser-matrix evaluation has been completed; low cognitive load is a design hypothesis supported by hierarchy and reduced choices, not a measured learning outcome. WCAG2.2AA remains a target, not certification. Course text stays in its authored language; only shell language switches.

No operational AI provider, offline learning, new project-management backend, grade synchronization or production identity hardening was invented. Existing Moodle plugin JWT-validation and HTTP limitations remain. Runtime Moodle binding checks userid/username; auth/idnumber is validated at provisioning. Seven-day tokens need explicit rotation. The elapsed budget cannot hard-cancel a slow-trickling upstream response. Cloud deployment requires HTTPS/identity configuration review; current loopback guards intentionally prevent accidental public use.

Existing baseline and candidate containers/data remain; only the new design API/web containers were introduced. Read-only Moodle service and exact preview login origin were configured. Regression tests added synthetic submissions/reviews to the existing candidate; original learning assets were not deleted. Installation/start/stop instructions: [operations](operations.md).
