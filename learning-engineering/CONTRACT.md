# Learning Engineering <-> Content Factory <-> Learning OS
Status: proposed, NOT implemented.

## Minimal object contract
Each learning object has stable id, semanticVersion, locale, type, title, learningOutcomeIds[], competencyIds[], prerequisiteIds[], sourceEvidenceIds[], license, accessibility, reviewStatus, checksum, mediaRefs[], publishedAt and deprecatedAt (optional).
Each assessment links outcomeIds, rubricId, scoring specification and evidence requirements.
A curriculum defines ordered program/course/module/lesson references; references bind explicit immutable versions or declared compatible ranges.

## Ownership
Learning Engineering owns competency/outcome definitions, curricula and assessment intent; Content Factory owns authored artifacts, media derivatives, quality control and licenses; Learning OS owns delivery, access control, enrollment and learning event capture.

## Acceptance
Validate JSON schema, referential integrity, localization, content provenance, licensing, accessibility, export/import, and no cross-tenant leaks. Content may be authored independently of the LMS. Version changes must not silently rewrite historical student results.


## Exchange outline supplement — proposed v0.1
This is a design outline, not an implemented API, JSON Schema or conformance certificate.
Semantic versions and package revisions are separate. Breaking field/meaning changes require
a new contract major version; readers reject unsupported major versions.

### Envelope and validation rules
A package contains contractVersion, packageId, packageRevision, producer, createdAt,
objects[], dependencyManifest and payloadDigest. Every object uses the original fields above.
id is stable; semanticVersion identifies immutable content; locale is an explicit language tag;
type uses a versioned controlled vocabulary; title is non-empty.
References resolve to exact ID/version pairs in the dependency manifest before acceptance.
Compatible ranges mentioned above must be resolved and recorded before import, never at replay time.
checksum specifies algorithm (proposed SHA-256) and digest of the exact UTF-8 payload bytes;
the manifest records media digests independently. Canonical serialization is TBD at G3.

license is structured: status, identifier (UNKNOWN allowed), evidenceRefs, attribution and
allowedUses. sourceEvidenceIds must resolve to evidence records with source locators.
accessibility records review state and findings; a populated field is not accessibility conformance.
reviewStatus follows [ACCUMULATION.md](ACCUMULATION.md); only approved objects with cleared
rights for the intended use may be accepted for delivery. Draft exchanges stay quarantined.
publishedAt is absent until publication; deprecatedAt is optional. This clarifies the original list:
publication dates must not be fabricated for drafts.

### Transaction lifecycle
1. Content Factory exports an immutable candidate and dependency/media manifests.
2. Consumer authenticates producer and checks authorized tenant/context at execution time;
   payload-supplied ownership or tenant IDs are not authority.
3. Validate contract version, digests, references, rights, review state and accessibility policy.
4. Return a receipt containing packageId/revision, digest, accepted/rejected/quarantined status,
   validation errors and timestamp. Acceptance is atomic; failures do not partially publish.
5. Same packageId/revision and digest is an idempotent replay. Same ID/revision with a different
   digest is a conflict and must be rejected.
6. Rollback selects an earlier approved immutable version; historical results retain original
   object, assessment, rubric and scoring versions. Deprecation never rewrites history.

Proposed errors: UNSUPPORTED_VERSION, DIGEST_MISMATCH, MISSING_REFERENCE,
REVISION_CONFLICT, RIGHTS_PENDING, REVIEW_PENDING, ACCESS_DENIED.
Learning OS emits separately governed events referencing exact content/outcome/assessment
versions. Learner identifiers and raw events are excluded from this public knowledge package.
Retention, consent and access policy for events require separate owner approval.

### Required G3 evidence (not executed)
Round-trip preserves IDs, versions, fa/en text and media digests; unresolved references fail;
tampering fails; pending rights quarantine; duplicate replay is idempotent; conflicting revision
fails; unsupported version fails; unauthorized cross-tenant import fails; rollback retains
historical scoring. Concrete schema, transport, authentication mechanism and executable fixtures
remain G3 deliverables, not promises of existing interoperability.
