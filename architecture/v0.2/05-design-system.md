# Design System

**Document ID:** ARC-05  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Learning and UX leads (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

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

## Phase 1–2 evidence update — 2026-11-25

### Implemented design subset
The original teal/green visual identity and licensed local Noto Sans Arabic font were preserved. Shared Card, Heading, Progress, CourseRow, CourseDialog and Modal components are implemented, with official shadcn/ui Button/Dialog sources. RTL/LTR, 320/390 px reflow, dialog Escape, labels and reduced-motion support were tested locally in Chromium. This is partial accessibility evidence, not a full WCAG audit or certification.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
