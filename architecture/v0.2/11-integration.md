# Integration Architecture

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

## Interfaces
| Engine | Contract | Ownership |
|---|---|---|
| Keycloak | OIDC | Identity |
| Moodle | Supported API/LTI where applicable | Course execution |
| BigBlueButton | Server-side meeting API | Live sessions |
| Discourse | API and supported SSO | Discussions |
| LRS | xAPI | Learning statements |
| Model gateway | Versioned model interface | Inference |
## API proposal
GET /v1/resources; POST /v1/enrollments; POST /v1/workshops; POST /v1/submissions; GET /v1/progress. Mutations require authorization and idempotency keys where retryable.
## Event envelope
event_id, event_type, schema_version, occurred_at, tenant_id, subject_id, correlation_id, payload. Events: enrollment.created, workshop.closed, submission.received, assessment.approved, competency.updated.
## Reliability
Transactional outbox, at-least-once delivery, consumer deduplication, bounded retries, dead-letter queue and reconciliation. Verify actual engine versions and licenses before integration.
## Acceptance
Contract tests, replay, timeout, duplicate delivery and unavailable-engine tests.
