# Data Architecture

**Document ID:** ARC-08  
**Document revision:** 0.2-draft  
**Review status:** Proposed  
**Owner role:** Architecture lead (assignment pending)  
**Dependencies:** [Architecture index](README.md) and [documentation standard](../../governance/documentation-standard.md).

Version: 0.2.0-draft | Target architecture proposed | Local prototype evidence appended; target not fully implemented or verified

## Logical schema

Tenant(id); Person(id); Membership(tenant_id,person_id,role); Resource(id,tenant_id); Revision(id,resource_id,locale); Offering(id,resource_id); Enrollment(id,offering_id,person_id,status); Activity(id,offering_id); Submission(id,activity_id,person_id,revision); Assessment(id,submission_id,rubric_version); Competency(id); Evidence(id,assessment_id,competency_id); ExternalMapping(system,external_id,canonical_id).

## Storage

PostgreSQL transactional source; object storage for media and artifacts; optional pgvector for authorized retrieval; LRS adapter for xAPI. External engines own native records. No direct cross-engine database writes.

## Controls

UUID identifiers, foreign keys, tenant-scoped unique constraints, UTC timestamps, revision history, transactional outbox, schema migrations. Minimize PII and define retention per category before launch.

## Recovery

Encrypted backups, restore drill, documented RPO/RTO targets pending owner approval. Offline drafts may queue; server validates on sync; conflicts surfaced rather than silently overwritten.

## Acceptance

Migration rollback, tenant isolation, duplicate-event handling, restore and deletion propagation tests.

## Phase 1–2 evidence update — 2026-11-25

### Implemented browser storage

Dexie schema v1 uses states and archive tables; the learning payload has version 2. On first initialization, valid nikway-demo-v1 localStorage data and its raw backup are migrated atomically. Existing IndexedDB state wins on later boots. The legacy key is never deleted or rewritten. Invalid input fails visibly; reset/import preserve a recovery copy. Transactions serialize concurrent changes. PostgreSQL, outbox, server sync, tenancy, encrypted backup and deletion propagation remain unimplemented.

[Implementation package and decision reconciliation](implementation/phase-1-2/README.md) · [Acceptance evidence](implementation/phase-1-2/ACCEPTANCE.md).

## Related architecture authority

[ARC-15 — specialized design](./data-contract-fabric.md) refines this document within its scope. Both remain proposed; unresolved conflicts require an ADR and review. Historical implementation evidence is not superseded by target design.
