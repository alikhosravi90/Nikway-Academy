# Design System

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

## Foundations
Responsive mobile-first shell; Persian RTL and English LTR. Use semantic CSS logical properties. Proposed fonts: system sans and Vazirmatn subject to license review.
## Tokens
Spacing: 4, 8, 12, 16, 24, 32 px. Radius: 4, 8, 12 px. Semantic colors: surface, text, muted, primary, focus, danger, success. Color values remain provisional until contrast testing. Typography: body 16px default, scalable headings. Reduced motion respected.
## Components
Navigation, resource card, filter, search, dialog, form, timeline, progress, rubric, discussion, workshop board, submission and notification.
## States
Default, hover, focus, disabled, loading, empty, error, success. Never rely on color alone. Accessible names and keyboard behavior required.
## Acceptance
WCAG 2.2 AA target; keyboard-only navigation, visible focus, screen-reader labels, 320 CSS px reflow, RTL visual regression. Tailwind/shadcn are implementation choices, not proof of compliance.
