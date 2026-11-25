# Information Architecture

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

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
