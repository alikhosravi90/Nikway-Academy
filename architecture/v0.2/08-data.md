# Data Architecture

Version: 0.2.0-draft | Proposed architecture | Not implemented or verified

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
