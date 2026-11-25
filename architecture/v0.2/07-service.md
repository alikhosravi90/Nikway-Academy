# Service Blueprint

**Document ID:** ARC-07  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

| Stage | Frontstage | Backstage | Evidence |
|---|---|---|---|
| Discover | Search and preview | Catalog indexing | Resource view |
| Enroll | Confirm access | Eligibility and provisioning | Enrollment ID |
| Prepare | Reminder and materials | Scheduling and checks | Readiness record |
| Attend | Live workshop | Room provisioning and moderation | Attendance |
| Apply | Submit project | Storage and assignment | Submission |
| Review | Feedback | Rubric review and escalation | Assessment |
| Improve | Reflection and next goal | Progress aggregation | Action plan |
## Responsibilities
Product owner owns journey; facilitator owns workshop; assessor owns review; moderator owns community safety; support owns incidents; platform operator owns availability.
## Exceptions
Failed provisioning: retry and support escalation. Cancellation: notify and offer rescheduling. Disputed grade: independent human review. Recording: explicit policy and consent.
## Acceptance
Run happy path and cancellation, access failure, late submission and appeal scenarios. Service targets remain TBD after pilot.

## Phase 1–2 evidence update — 2026-11-25

### Local service slice
Frontstage covers learning, reading, tutoring mock and simulation. Backstage is browser-only: validated commands, IndexedDB transactions, local backup/import and offline asset caching. Failure states include corrupt legacy data and invalid backup files; reset requires confirmation. Provisioning, real enrollment, attendance, cancellation and human appeals remain proposed services.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
