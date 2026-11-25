# Content Factory and Hybrid Content Repository

Registration: 2026-11-25 · CF-01 · version 0.1.0 · **PROPOSED / NOT IMPLEMENTED**

Content Factory is the content-production capability (کارخانه تولید محتوا). The Hybrid Content Repository is the governed accumulation, discovery and reuse capability. Learning engineering defines learning objectives, curriculum, activities, assessments and evaluation; Learning OS delivers approved learning experiences and owns learner execution state. Content can be authored independently of a course or delivery platform, then assembled through explicit, versioned references.

## Evidence and scope

Source conversation: [توضیح مرحله‌ای توسعه](https://chatgpt.com/c/6b06c896-8db0-83eb-953a-1ed535d9ff00). Both available pages were read on 2026-11-25. Recoverable user messages name Content Factory, Learning Engineering, independent content authoring, accumulation, benchmarking and separate-branch registration. Assistant messages returned unresolved `chatgpt-content-reference` placeholders. **The original detailed architecture and benchmark list are UNKNOWN.** This registration combines those recoverable requirements with the current task's explicit scope and clearly proposed design below; it is not a verbatim reconstruction or evidence of prior approval.

Repository base: `learning-engineering` at `967044ecc5e63dc61f799568826723ad866970c4`; remote `main` had the same SHA when checked. `learning-engineering` contained the twelve draft architecture documents at that base, not a separately implemented learning-engineering service. Other architecture and MVP branches are not merged into this registration. Learning OS below is a logical integration boundary, not a verified running product/API.

Related baseline: [domain model](../04-domain.md), [learning experience](../06-learning-experience.md), [data architecture](../08-data.md), [integration architecture](../11-integration.md), [compliance](../12-compliance.md). This proposal extends their ownership, PostgreSQL, object-storage and adapter principles; it does not supersede them.

## Proposed component content model

| Entity | Responsibility and relationship |
|---|---|
| Source asset | Original document/media or lawful source pointer; immutable capture plus source rights and checksum. Ingestion does not grant reuse rights. |
| Content component | Stable tenant-scoped ID for a concept, explanation, worked example, case, exercise, assessment item, rubric, media segment or reflection prompt. Independently meaningful with declared context/prerequisites. |
| Component revision | Immutable authored body, metadata, source lineage and dependencies. Separate schema version from editorial version. |
| Assembly | Ordered references to exact revisions: lesson → module → course/pathway. Includes sequence, prerequisite and learning-outcome bindings. Avoid mandatory course ownership of a component. |
| Rendition | Generated HTML, PDF, video caption track or package, identified by source revision, build recipe/tool version and digest. Never canonical authored truth. |
| Release | Reviewed immutable assembly manifest and dependency lock with approval evidence. |
| Usage record | Reverse reference from assembly/release/channel to component revision for impact analysis. Learner activity belongs elsewhere. |

A reusable component must declare purpose, intended audience, prerequisites, outcomes and pedagogical role; arbitrary text chunks alone are not learning objects. Assessment answers/rubrics can require stricter access than learner-facing content. Rich text must have a portable structured representation; platform-native blocks are retained with an adapter and explicit portability limitations.

## Proposed metadata contract

Required for draft: `component_id`, trusted `tenant_id`, `revision_id`, `schema_version`, `type`, `title`, `language` (BCP 47), `body_ref`, `body_digest`, `creator_ref`, timestamps, `lifecycle_state`, `provenance[]`, `rights_status`. Drafts may contain explicit UNKNOWNs; release must reject unresolved required fields.

Required for release: description, audience/level, outcome IDs and their framework versions, prerequisites, educational role, duration estimate and basis, subjects/tags from versioned vocabularies, accessibility review (captions/alt text/reading order as applicable), rights holder, license or permission evidence, attribution, allowed uses, reviewer/approval receipt, dependency lock, source locators, source capture date and checksums where lawful copies exist. No guessed license; an accessible URL is not permission.

Conditional: assessment scoring/rubric version, difficulty evidence, media MIME/size/duration, localization `translation_of`, adapter/native IDs, AI-generation tool/model/version and human review record, expiry/embargo, retention class. Private prompts or personal data must not be copied into public provenance. Use protected evidence references when needed.

## Hybrid storage layers and authority

| Layer | Authoritative responsibility | Boundaries |
|---|---|---|
| Git | Architecture, schemas, templates, small textual sources and release/build manifests | Reviewable diffs; no large binaries, secrets or learner data. Git commit is not publication approval. |
| PostgreSQL | Canonical tenant-scoped IDs, metadata, lifecycle, permissions, approvals, dependency/usage mappings and outbox | Runtime registry authority; versioned import from Git rather than two unrestricted writers. |
| S3-compatible object store | Original permitted assets, immutable revision payloads, large media and derived artifacts | Digest-addressed/versioned objects, restricted buckets and short-lived authorized access; retention and backups required. |
| Search / optional pgvector | Rebuildable full-text/semantic projections | Never authority for rights, publication, tenancy or identity. Filter access before returning results. |
| Optional relationship projection | Outcome, prerequisite, derivation and reuse traversal | Begin with relational edges; a separate graph database needs measured justification. |
| External engines / LRS | Platform-native records and learner activity in their own contexts | Repository stores scoped mappings; no duplication of student histories in public Git. |

Proposed ingestion: quarantine → validate type/size and scan assets → record source and rights → deduplicate by digest within authorized scope → normalize components → review metadata/pedagogy/accessibility → approve → immutable release → adapters. Content storage uses staged objects, transactional metadata plus outbox, idempotent consumers and orphan reconciliation; do not assume a database/object-store atomic transaction. Index failure must not undo a valid authoritative release. Restore must recover matching metadata, manifests and objects before rebuilding indexes.

## Versioning, provenance and reuse

Use stable component IDs plus immutable revision IDs and content digests. Editorial semantic versions communicate breaking pedagogical/assessment changes (major), compatible additions (minor), and corrections (patch); schema and adapter versions are independent. Published manifests pin exact revisions, checksums and adapter versions; `latest` is only a discovery convenience. Optimistic concurrency with an expected revision rejects stale edits. Approval is bound to a digest; any change requires a new revision and review.

Lifecycle: draft → in_review → approved → published → deprecated/withdrawn. Only designated reviewers can approve; release authorization is separate from authoring. Withdrawal blocks new delivery and new reuse, records the reason, and triggers usage-impact handling. Historical records remain subject to retention/privacy obligations; course evidence is not silently rewritten.

Provenance follows entity/activity/agent concepts: original source → ingestion/transformation → component revision → translation/adaptation → assembly → rendition. Record source locator, capture date, digest, rights evidence, author/editor/reviewer identities, transformation tool/version and derivation edges. AI output is proposed content requiring verification; provenance is an audit trail, not proof of accuracy or permission.

Reuse modes: reference an exact revision; fork/adapt with `wasDerivedFrom`; translate with language and source revision; compose through an assembly. Check rights, tenant authorization, prerequisites and outcome fit at each reuse/release. Deduplication does not imply shared access. Updates produce impact reports and optional upgrade proposals; existing releases remain pinned until reviewed. If a source is revoked, notify affected owners and block new use while handling existing releases under an explicit policy.

## Interoperability with learning-engineering and Learning OS

Learning engineering owns outcome frameworks, curriculum design, assessment rationale and evaluation criteria. It requests components against versioned outcome IDs; Content Factory supplies reviewed components and evidence. Learning OS consumes approved release manifests and renditions, enforces enrollment/access and records activity. Aggregate evaluation feedback can request revision; it must not silently edit canonical content or export personal learner data into the repository.

Proposed API contracts (not existing endpoints): `GET /v1/components/{id}/revisions/{revision}`, `GET /v1/releases/{id}`, and restricted `POST /v1/assemblies/{id}/releases` with expected revision and idempotency key. Trusted authentication supplies tenant scope; client-provided tenant IDs never authorize access. Each response carries schema version, digest and lifecycle state; withdrawals must be checked at delivery time as well as import time.

Proposed events: `component.revision.approved`, `content.release.published`, `content.release.withdrawn`. Envelope: event ID, event/schema version, trusted tenant scope, aggregate ID/revision, occurred-at, correlation ID, payload reference and digest. Consumers deduplicate, retry with bounded backoff, isolate poison events, reconcile gaps and reject unsupported schemas. Store external native IDs together with engine instance and adapter version.

Candidate mappings: DCMI for descriptive metadata; PROV-O for provenance; CASE for outcome identifiers; QTI for assessment interchange; Common Cartridge for resource/assembly exchange; LTI 1.3 for tool launch rather than canonical content storage; xAPI via the baseline LRS adapter for learning activity rather than component truth. Select exact versions and supported subsets through contract tests; no conformance claim is made. H5P/Open edX are benchmark/adapter candidates, not selected dependencies. See [benchmarks](benchmarks.md).

## Implementation sequence (proposed)

1. Reconcile the original conversation and approve terminology/ownership.
2. Define schema and synthetic fixtures; validate one component, its source, an adaptation and two assemblies.
3. Prototype Git + PostgreSQL + object storage, review/release flow and deterministic manifests.
4. Prove pinned reuse, withdrawal, restore and tenant isolation; then add one adapter.
5. Pilot with learning engineering and Learning OS owners; evaluate quality, author effort and reuse before expanding services.

All operational acceptance remains open in [validation gates](validation-gates.md). No application code, service deployment, real corpus ingestion or publication is authorized by this design registration.

## Concurrent learning-engineering update reconciled

During final verification, remote `learning-engineering` advanced to `d8d3347a708749f545eb3f2ac7e339db3f277b1f` with five new proposal documents. This branch retains its original base `967044e`; no merge or history rewrite was performed. The new [Learning Engineering contract](https://github.com/alikhosravi90/Nikway-Academy/blob/d8d3347a708749f545eb3f2ac7e339db3f277b1f/learning-engineering/CONTRACT.md), [knowledge-base scope](https://github.com/alikhosravi90/Nikway-Academy/blob/d8d3347a708749f545eb3f2ac7e339db3f277b1f/learning-engineering/README.md) and [taxonomy](https://github.com/alikhosravi90/Nikway-Academy/blob/d8d3347a708749f545eb3f2ac7e339db3f277b1f/learning-engineering/TAXONOMY.md) were read. Ownership and independent authoring agree with this proposal.

Proposed boundary mapping: `id` → `component_id`; `semanticVersion` → editorial version; `locale` → `language`; `learningOutcomeIds` → versioned outcome references; `competencyIds` → versioned competency references; `prerequisiteIds` → prerequisite references; `sourceEvidenceIds` → protected provenance evidence IDs; `checksum` → `body_digest`; `mediaRefs` → versioned asset references; `reviewStatus` → review state within lifecycle. Preserve `type`, `title`, `license`, `accessibility`, `publishedAt` and optional `deprecatedAt`; assessment objects additionally carry outcome IDs, rubric ID/version, scoring specification and evidence requirements. A schema adapter must explicitly serialize these fields; naming similarity alone is not an implemented contract.

The upstream contract permits explicit versions or declared compatible ranges for curriculum references. Proposed resolution: allow ranges during curriculum design, then resolve and pin exact immutable revisions in release manifests. CF-G1 and CF-G6 must validate this mapping and range resolution with the learning-engineering owner before adoption. These external documents remain proposals, not tested integration evidence.
