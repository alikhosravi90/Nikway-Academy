# Integration Architecture

**Document ID:** ARC-11  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

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

## Phase 1–2 evidence update — 2026-11-25

### Implemented ports, no external engines

LearningPort exposes initialize/read/dispatch/exportBackup/importBackup; TutorPort exposes reply. Adapter selection is centralized in app/services.ts. HashRouter, relative asset base and service-worker precache were exercised from a nested static-server path, including offline reload. No HTTP API, OIDC provider, LMS/LRS, media engine or model gateway is connected. Interoperability contract/replay tests for those engines remain pending.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).

## Related architecture authority

[ARC-18 — specialized design](./integration-fabric.md) refines this document within its scope. Both remain proposed; unresolved conflicts require an ADR and review. Historical implementation evidence is not superseded by target design.
