# Pending validation gates

All gates are **OPEN / NOT RUN** as of 2026-11-25. Owners below are proposed roles, not assigned people. Documentation registration and Git checks do not close operational gates.

| Gate | Proposed owner | Required acceptance evidence |
|---|---|---|
| CF-G0 Source fidelity | Content architecture owner | Obtain complete original assistant responses; reconcile original benchmark/design decisions with this proposal and record differences and approval. |
| CF-G1 Model and pedagogy | Learning-engineering owner | Validate schema and synthetic examples; map outcomes/prerequisites; review explanation, assessment and adaptation; reject missing release metadata and broken references. |
| CF-G2 Rights and provenance | Content governance owner | Trace every release dependency to source and rights evidence; deny UNKNOWN/disallowed licenses; test protected provenance references and human review of AI-generated material. |
| CF-G3 Storage and recovery | Data/platform owner | Restore matching metadata/objects/manifests from backups, verify hashes, rebuild search, reconcile interrupted upload/outbox and prove no dangling published references. Agree RPO/RTO before testing. |
| CF-G4 Versioning and reuse | Content Factory owner | Reuse one revision in two assemblies, publish an update without changing pinned releases, reject stale edits, trace fork/translation lineage and identify all affected usages on withdrawal. |
| CF-G5 Access and privacy | Security owner | Deny cross-tenant read/write/search/export and asset access; reject forged tenant IDs, expired links and unauthorized approval; prove revocation and restricted assessment access. |
| CF-G6 Interoperability | Integration owner | Pin API/event and external standard versions; round-trip fixtures through selected adapter, compare IDs/outcomes/scoring/rights, report loss; test duplicates, retries, outage/replay and unsupported schemas. |
| CF-G7 Learning OS consumption | Learning OS owner | Consume approved pinned release, reject draft/withdrawn content, authorize each delivery, retain revision IDs in activity mappings and separate learner data from content. |
| CF-G8 Quality and accessibility | Editorial/accessibility owner | Human review of accuracy, attribution, language/RTL, captions, alt text, reading order and assessment quality with recorded findings and corrections. |
| CF-G9 Pilot and release decision | Academy owner | Evaluate synthetic trial and bounded learner pilot under separate approval; agree quality/reuse/effort thresholds before measurement, name accountable owners and record GO/NO-GO. |

Current outcome: **design registered; implementation and operational readiness NOT ESTABLISHED**. No merge, deployment, package publication, production data movement or conformity certification is part of this change.
