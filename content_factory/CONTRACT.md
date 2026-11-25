# Unified Content Factory / Learning Engineering contract v1.0.0

The executable source of truth is `cf/contracts.py`; `contracts/component-input.schema.json` is generated from it. This is a local MVP profile, not CASE/QTI/Common Cartridge certification. Existing Learning Engineering files on its separate branch are not modified.

## Reconciliation

Upstream: `learning-engineering/CONTRACT.md` at d8d3347a708749f545eb3f2ac7e339db3f277b1f. All named fields are represented: id, semanticVersion, locale, type, title, learningOutcomeIds, competencyIds, prerequisiteIds, sourceEvidenceIds, license, accessibility, reviewStatus, checksum, mediaRefs, publishedAt and deprecatedAt. In this text-only profile `mediaRefs` is an empty output list, publication dates remain null, reviewStatus is `draft|approved_local|withdrawn`, and revisionId is additionally required for any reference. `approved_local` is a synthetic workflow decision and does not assert human approval or publication rights.

Learning Engineering owns outcome/competency vocabulary and curriculum meaning; Content Factory owns immutable authored revisions and renditions; Learning OS owns execution/access and learning events. Outcome/competency references are versioned strings. The MVP validates question-to-outcome consistency but does not resolve an authoritative external competency service. This remains a semantic gate.

The architecture's snake_case draft is normalized to Learning Engineering's camelCase wire names: component_id→id, language→locale, revision_id→revisionId, body_digest→checksum, review state→reviewStatus. schemaVersion is distinct from semanticVersion and revisionNumber. Unknown fields are rejected, including tenant/role assertions. The server derives context from a revocable expiring opaque local credential stored hashed in PostgreSQL; OIDC/Keycloak federation is not yet integrated.

prerequisiteIds and derivedFrom are exact local revision IDs; outcomes and competencies are versioned semantic IDs. Content is immutable once inserted. A new semantic version and expectedRevision are required to edit. Authors cannot approve. Approval is bound to the revision digest and an audit event; a different reviewer identity and resolved metadata are required. Service transactions use a restricted non-owner PostgreSQL role and forced tenant RLS.

Curriculum ranges may be used upstream during design; this MVP accepts only exact revision IDs in course candidates. A candidate pins its full dependency graph and rendition hashes. One component may be used in two courses without duplication. Withdrawal makes all dependent candidates undeliverable, including transitive derivations. No release or publication endpoint exists.

`POST /v1/components` accepts `{component, expectedRevision}`. Review and withdrawal accept a note. `POST /v1/candidates` accepts `{courseId, revisionIds, idempotencyKey}`; a repeated key with different content is rejected. Prepared candidates use schemaVersion 1.0.0 and status candidate_local. Events use eventId/type/tenant/payload; the local consumer checks the trusted tenant, current candidate status, digest and schema before durable deduplication. Delivery always rechecks current access and state; outages fail closed. Retry means resubmit the same event; there is no autonomous background publisher.

Packages contain text.md, lesson.html, quiz.json and manifest.json. Instructor packages include quiz answers; learner packages exclude answers/explanations. The package manifest binds file hashes to the server-side candidate. All generated HTML content is escaped. Packages are portable custom ZIPs, not SCORM/QTI/CC packages. Offline exports cannot be remotely revoked; withdrawal blocks subsequent server delivery.
