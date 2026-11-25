# Domain Model

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Contexts and ownership
| Context | Aggregate | Invariant |
|---|---|---|
| Identity | Membership | Role scoped to tenant |
| Catalog | Resource | Published revision immutable |
| Learning | Enrollment | One active enrollment per offering/person |
| Events | Workshop | Capacity enforced atomically |
| Community | Discussion | Moderation state recorded |
| Practice | Submission | Revision and author retained |
| Assessment | Review | Rubric version fixed |
| Competency | Credential | Approved evidence required |
| Challenges | Competition | Scoring rules fixed before start |
| AI | AgentRun | Tool scope and trace recorded |
## Lifecycle
Enrollment: requested → active → completed/cancelled. Workshop: draft → scheduled → live → closed/cancelled. Submission: draft → submitted → reviewed → accepted/revision_requested.
## Relations
Person joins Organization via Membership; Offering references ResourceRevision; Enrollment links Person and Offering; Submission references Activity; Review references Submission and Rubric; Credential references approved Review.
## Acceptance
Reject invalid transitions, duplicate enrollment and overbooking; enforce ownership and tenant scope.

## Phase 1–2 evidence update — 2026-11-25

### Implemented learning aggregate
LearningState v2 contains done[3], saved[], sim and attemptIds[]. CompleteLesson uses a course ID and current lesson index; repeated completion is idempotent and skipped lessons are rejected. Bookmark toggles a validated resource ID. Simulation attempts use unique IDs to prevent repeated counting. Zod validates bounds. Tenant membership, enrollment, review and credential aggregates above are not implemented.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).
