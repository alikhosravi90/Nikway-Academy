# Secure content-ready Local MVP implementation plan

Goal: preserve the established local baseline, investigate and remediate six identity-image findings, and prove a portable educational-content admission and learning cycle locally. No merge/release without final owner approval.

Architecture: existing FastAPI/PostgreSQL RLS/Keycloak/React stack. A standalone versioned JSON content package crosses the proposed Content Factory / Learning Engineering boundary. The offline producer is real executable tooling, not a claim that those external services exist. An authenticated reviewer imports immutable drafts, then explicitly publishes locally after digest/revision validation. The API derives tenant and actor; the package cannot supply authority. Published versions receive separate tenant-derived course IDs, preserving prior enrollments. Plain text is rendered without HTML execution.

Alternatives: unvalidated direct SQL insertion is rejected because it bypasses admission; a new CMS/orchestrator is unnecessary for this bounded test. A portable JSON envelope with a strict schema is selected as the smallest adapter; full external-contract coverage is documented separately. Identity remediation prefers a supported vendor update, then an isolated reproducible candidate and explicit alternatives comparison if the vendor does not provide a fix.

Tasks and ownership:
- [ ] Root: freeze baseline receipts/branch/archive, isolated integration branch; preserve existing runtime and volume.
- [ ] Infrastructure: official CVE root cause, reachability, supported remediation; isolated candidate scans/identity compatibility and alternatives when needed.
- [ ] Architect: reconcile existing proposed Content Factory/LE contracts; strict portable schema/validator/negative tests and original Persian three-lesson sample.
- [ ] Root: package draft/admission/publication/export, forced tenant RLS and immutable/versioned mappings; server-enforced assessment bounds; negative/idempotency/concurrency tests.
- [ ] Frontend: render metadata/practice/rubric as text and verify full imported-course journey.
- [ ] Validators: recheck security, performance, backup/restore, baseline preservation; compute progress by six requested deliverables with evidence, not elapsed time.
- [ ] Root: publish reviewable draft changes and report GO/NO-GO, remaining blockers; no merge/release.

Acceptance: tenant/auth checks fail closed; package schema/integrity/reference/rights validation; draft invisible to learners, explicit publish, version conflict rejection, identical replay, immutable existing progress; package export revalidates independently; imported course supports enrollment → lessons → submission → revision feedback → resubmission → accepted human review. Completion is not competency certification. Security GO requires verified remediation or approved exception (none granted), current scan, and regression/recovery evidence.
