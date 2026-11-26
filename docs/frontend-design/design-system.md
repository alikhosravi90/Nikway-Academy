# NIKWAY Academy design system

Status: implementation specification for the local functional prototype; accessibility conformance requires evidence, not this document alone.

## Principles

Learning before navigation; one primary next action per region; progressive disclosure; source-labeled progress; visible recovery from failure; consistent terminology; user-controlled appearance. Adaptation means responsive layout, explicit preferences and real task state, not an unverified cognitive diagnostic model.

## Semantic tokens

Use CSS custom properties as a single semantic layer. All three palettes provide canvas, surface, elevated surface, text, muted text, border, primary, primary text, focus, success, warning and danger. Components consume roles rather than raw palette values. Keep content surfaces opaque in every palette. Dark mode is a complete role mapping, not an inversion filter.

Spacing scale: 4, 8, 12, 16, 24, 32, 48 px. Typography: locally hosted Vazirmatn, system sans-serif fallback; reading content 16 px (15 px on mobile), interface chrome 15 px (14 px on mobile), line-height about 1.75 for Persian reading, readable measure about 70 characters. Type remains zoomable. Radius distinguishes small controls from cards without creating excessive ornament. Use a single restrained navigation shadow; content hierarchy comes from spacing, headings and borders.

## Atomic component library and UI kit

| Level     | Components                                                                                  | Required states                                                |
| --------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Atoms     | Button, Icon, Input, Label, Badge, Heading, Progress                                        | Default, hover, focus, disabled; non-color status              |
| Molecules | Search/filter field, course summary, status message, preference control                     | Empty, loading, error, success where relevant                  |
| Organisms | Navigation, next-action panel, course grid, lesson reader, assessment form, rubric feedback | Keyboard traversal, retry, pending mutation, permission denied |
| Templates | Learning overview, collection, split workspace, settings/admin                              | 320 px reflow and desktop composition; RTL/LTR                 |

Lucide supplies consistent stroke icons. Decorative icons are hidden from assistive technology; icon-only controls need localized accessible names. Directional arrows mirror with writing direction; media controls and brand marks do not. Native buttons and links retain their semantics; no clickable card div without an accessible control.

## UX pattern library and ten screens

| Screen            | Main purpose                                          | Operational boundary                                     |
| ----------------- | ----------------------------------------------------- | -------------------------------------------------------- |
| Dashboard         | Resume learning; concise real progress                | No fabricated analytics                                  |
| Catalog           | Search/filter available courses and select            | Respect tenant-visible results                           |
| Workspace         | Read content and perform the next action              | Preserve network-backed submissions                      |
| Learning path     | Explain sequence and completion                       | Label completion, never imply competency mastery         |
| AI tutor          | Explain service state and access available capability | No simulated tutor conversation                          |
| Assessment        | Submit work and inspect rubric/feedback               | Confirm pending/success/failure; no duplicate submission |
| Projects          | Find practical tasks and workshops                    | Distinguish available tasks from external services       |
| Knowledge library | Browse/search actual lesson resources                 | No invented external corpus                              |
| Profile           | Identity and display preferences                      | Display is not an authorization control                  |
| Administration    | Role-appropriate operational controls                 | Backend permissions remain authoritative                 |

Empty states explain what is missing and provide a valid next action. Errors preserve entered work, give a human-readable message and support retry. Disabled operations explain why. External Moodle transitions are named clearly; Academy and Moodle progress must not be conflated. Confirmation is reserved for destructive or consequential actions.

## Motion, transparency and responsive behavior

Use short opacity/color transitions (approximately 120–180 ms) only when useful. Honor `prefers-reduced-motion` and an explicit reduce-motion preference; remove transforms and smooth scrolling. Honor `prefers-reduced-transparency` with an explicit solid-surface fallback for browsers without support. Avoid glass over dense learning text.

Use logical margin/padding/inset, document `dir` and localized labels. Isolate code, URLs and identifiers with appropriate LTR direction. Mobile navigation stays keyboard reachable; desktop sidebar order matches DOM reading order. No fixed overlay may hide focused controls. At 320 CSS px and 200% zoom, content should reflow without page-level horizontal scrolling; code/table regions can scroll locally with clear labels.

## Accessibility and validation contract

Target [WCAG 2.2 AA](https://www.w3.org/TR/WCAG22/): body text contrast at least 4.5:1, large text 3:1, essential controls/boundaries 3:1; visible focus, semantic landmarks, skip link, labeled fields and status announcements. Target controls at least 44 px where practical; AA target-size minimum is 24 CSS px subject to its specified exceptions. Provide keyboard alternatives to dragging and retain focus after dialogs/actions.

Validate all three palettes in light/dark, RTL/LTR, mobile/desktop and reduced effects. Automated accessibility checks complement keyboard, zoom, screen-reader and visual review; none alone establish full conformance. Capture tested routes, viewport, browser, API data source and limitations. Build and existing auth/tenant/content regressions must pass. Never cache authentication tokens, private API responses or submissions in the PWA. Offline capability must be described exactly as implemented.
