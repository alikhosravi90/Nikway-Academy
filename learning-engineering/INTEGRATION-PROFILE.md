# Offline contract profile 0.1.0

This executable profile implements a bounded subset of CONTRACT.md; its architecture text is
preserved as historical intent. Transport/authentication and authored media delivery are not implemented.

| Outline concept | Executable mapping |
|---|---|
| stable id / semanticVersion | record `id` / `version` |
| locale, title | required `title.fa/en`, `summary.fa/en`; one bilingual record |
| learningOutcomeIds | `LearningObjective` references in `data.objectiveRefs` |
| competencyIds | objective `data.competencyRefs` |
| prerequisites | typed `prerequisiteOf` relations; cycles rejected |
| sourceEvidenceIds | `provenance.evidenceRefs` to exact Evidence versions |
| license/review | `rights` and `review`; independent metadata checks, no trusted identity |
| accessibility | ContentSpecification `data.accessibility` design notes; not test results |
| mediaRefs/checksum | no media assets in this profile; whole package SHA-256 only |
| publishedAt | absent: package is never published by local fixture |
| createdAt | omitted in v0.1.0 deterministic draft exchange; not a publication event |

Package: contractVersion, packageId, packageRevision, producer, objects, dependencyManifest,
payloadDigest. Schema URN `urn:nikway:learning-engineering:record:0.1.0` resolves to bundled
record.schema.json via a local registry; no network resolution. All objects also pass graph validation.
The manifest lists every exact object revision; no implicit latest-version lookup.

Digest input is every envelope field except payloadDigest, serialized using Python JSON with
sorted keys, UTF-8, ensure_ascii=False, separators=(comma, colon), allow_nan=False, no trailing
newline. This is a Python-local serialization profile, **not RFC 8785** and not demonstrated
cross-language canonicalization. Other implementations must match these bytes and run fixtures
before interoperability can be claimed. Wire JSON may be indented; digest is recomputed canonically.

Import is a serialized local transaction. It validates historical package digests and recomputes
receipts instead of trusting stored approval claims. Record ID/version content is immutable even
across differently named packages. Historical versions remain available; no student results exist.
No HTTP endpoint, production access control, tenant separation, media verification or external
Content Factory/Learning OS test is claimed. Adding them requires separate implementation and tests.
