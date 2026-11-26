# Independent frontend validation

Real local preview `http://localhost:18901`, real Keycloak learner login and backend reads. No identity/API mocks and no coursework mutation in this suite.

- Final combined run:13/13 browser tests passed in31.1 seconds on the rebuilt image. Six design tests remain read-only; four existing learning/tenant regressions create synthetic fixtures; three new draft/drawer regressions assert behavior without server writes.
- Ten required learner surfaces: automated axe WCAG2 A/AA, 2.1 AA and 2.2 AA tags, zero reported violations.
- All six combinations of jade/ink/paper and light/dark: profile and dashboard audited.
- RTL mobile320/390: no horizontal overflow, reduced-motion and opaque glass preferences verified.
- LTR/English: document language/direction and preference persistence verified.
- Mobile menu:24 successive Tab presses remain inside dialog; Escape closes and restores focus to trigger.
- PWA: public-only cache allowlist; disconnected navigation serves public fallback. No API/identity/token/submission cache or sensitive web-storage entries found.
- Desktop1440/mobile390/320 screenshot review: legible stacked course cards and real Moodle module completion display; screenshot files retained outside Git.
- Manual fresh-load first Tab reaches visible skip-to-content link with focus outline.

Regression defects independently found and fixed by implementer: theme-transition intermediate color contrast (ratios1.2/1.24); mobile Escape focus restoration attempted while trigger's parent remained inert. Final suite passed without relaxing assertions or adding arbitrary settling waits.

Baseline18501 had serious color-contrast violations at desktop1280 and mobile390/320. New automated evidence improves that measured baseline, but does not constitute complete WCAG2.2AA certification. Screen-reader usability, assistive technology combinations, non-Chromium browsers, user testing and sustained-load performance remain unverified.

Performance receipt is a single local browser navigation sample, not a benchmark or capacity result. Browser console receipt covers post-login page errors only.

Follow-up regressions verified: unsent assignment draft survives navigation and stays scoped to course; unsent reviewer feedback survives navigation and stays scoped to submission; open mobile drawer clears modal/inert state on desktop resize and remains usable after returning to mobile. Draft tests verify zero API write requests. Draft retention is in-memory for the open authenticated application, not persistence across reload.
