# ADR-002 — Minimum operational local MVP

Status: accepted for bounded local implementation | Date: 2026-11-25 | Independent reviewer: integrator_2 (root slot)

Retain React/Vite and reuse verified prototype source. Add FastAPI modular monolith, PostgreSQL with tenant RLS and Keycloak OIDC in isolated local Compose. Local installation is authorized; public deployment and spending are excluded.

Deliver a persisted learner/reviewer journey, seeded scheduled workshops with atomic capacity registration, and an authenticated bounded read-only tool endpoint. Videoconference engine, external model provider and MCP transport are optional and must advertise unavailable when absent. The HTTP tool endpoint alone is not MCP conformance.

Defer Moodle, Discourse, BBB, H5P, CMS/media engines, LRS, vector/RAG stack, Temporal, Redis, object storage and overlapping policy libraries until a scoped acceptance case requires them. No compliance or production-readiness claim.

M03 gates apply before implementation. Historical phase-1/2 evidence is preserved and cannot establish current source-SHA CI. ADR-001 remains the explicit frontend reconciliation; this decision documents bounded implementation scope, not full architecture acceptance.

Acceptance: source provenance, independent contract review, integrated journey, two-tenant negative API/DB tests, clean local installation and restore evidence.

Current bounded contracts: each identity has one membership; catalog/workshops are seeded, with no authoring API. Rubric version 1 is pinned in evidence; requested revisions create new immutable submissions. Multi-membership tenant selection, publishing lifecycle, facilitator authoring and linked revision chains are deferred.

Independent review disposition: root reviewed and accepted the minimum local scope on 2026-11-25 after architecture/security contract review. This does not accept M11/M12 or override the release NO-GO from outstanding image vulnerabilities.
