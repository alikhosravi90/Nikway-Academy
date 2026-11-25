# Domain Model

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

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
