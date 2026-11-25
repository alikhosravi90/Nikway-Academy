# Information Architecture

**Document ID:** ARC-02  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Navigation
| Route | Contents | Primary task |
|---|---|---|
| / | Dashboard, recommendations | Resume |
| /academy | Courses, paths, lessons | Learn |
| /community | Groups, discussions, Q&A | Collaborate |
| /library | Articles, docs, video, podcasts, templates | Discover |
| /events | Meetings, webinars, workshops | Attend |
| /practice | Exercises, cases, projects | Apply |
| /challenges | Competitions, submissions, rankings | Compete |
| /assessment | Tests, self and peer reviews | Evaluate |
| /mentor | AI assistance | Reflect |
| /me | Progress, portfolio, credentials | Track |
## Metadata
Required: id, title, locale, type, owner, visibility, status, revision. Optional: industry, role, competency, difficulty, duration, prerequisites, license.
## Rules
One canonical ID per resource; localized slugs are aliases. Search respects permissions before returning snippets. Breadcrumbs reflect hierarchy, not browsing history. Published resources retain revision history.
## Acceptance
Test discovery of a workshop and related exercise from search, mobile navigation, RTL and LTR, and inaccessible content exclusion.

## Phase 1–2 evidence update — 2026-11-25

### Implemented navigation
Actual hash routes are /dashboard, /academy, /library, /tutor, /competency and /lab. Academy search/category filters, library search/bookmarks, related-resource links, breadcrumbs and Persian/English navigation are implemented. /mentor maps conceptually to /tutor and /practice to /lab; these are not route aliases. Community, events, challenges, assessment and permission-aware discovery remain unimplemented.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
