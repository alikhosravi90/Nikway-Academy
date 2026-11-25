# Portable learning package: bounded local profile

Status: implemented offline contract and original sample; local API admission is a separate integration gate. This is not a running Content Factory service, general interoperability certification, signature, content approval, or release authorization.

## Ownership and reconciliation

Read-only source review: Content Factory proposal `c861651`, `architecture/content-factory/README.md` (CF-01 v0.1.0, PROPOSED / NOT IMPLEMENTED), and Learning Engineering proposal `d8d3347a708749f545eb3f2ac7e339db3f277b1f`, `learning-engineering/CONTRACT.md`. Existing concurrent source work was not modified. The profile implements a small adapter to those proposals:

| Proposed concept | This profile | Remaining scope |
| --- | --- | --- |
| LE outcomes and assessment intent | course.objectives, objectiveIds, assessment, rubric | Competency/framework registries and curriculum graphs |
| CF assembly and immutable revision | packageId + version, ordered lessons, source course/lesson IDs | Reusable component registry, dependency lock and media renditions |
| semanticVersion / locale / checksum | version / course.language / integrity.digest | General export formats and standards conformance |
| Provenance and rights | Original offline-authoring provenance, empty sources, restricted local-review rights | Third-party rights clearance, ingestion and evidence registry |
| Accessibility | Plain Unicode text; RTL presentation is a separate UI responsibility | Audited accessibility metadata and media alternatives |
| Review and release | Package lifecycle is always draft; trusted local server separately records review/publication | CF review lifecycle, cryptographic attestations, withdrawal synchronization |
| Learning OS delivery | Local admission creates tenant-scoped course; exact package remains exportable | External service integration, event exchange and credential issuance |

The local profile does not claim completeness against the proposed minimum metadata: competency IDs, source-evidence IDs, accessibility declarations, publication timestamps and media references remain outside this version. `publishedAt` and reviewer authority must never be caller-controlled claims inside this draft package.

## Data and integrity

`contracts/content-package.schema.json` is JSON Schema 2020-12, version 1.0.0; all objects reject unknown fields. `content/validate_package.py` additionally checks reference coverage, unique IDs, ordered lessons, rubric anchors and bounds, assessment/rubric linkage, NFC Unicode, byte limits and checksum. Requires `jsonschema==4.26.0`. Package size is at most 128 KiB; 1–20 lessons, each at most 10,000 characters. Nesting beyond 20 levels, non-object roots, duplicate JSON keys and non-finite numbers are rejected before admission. Numeric values are bounded integers. NUL characters are rejected because PostgreSQL JSONB and text cannot store them.

`nikway-json-v1` means remove the top-level `integrity` member, serialize UTF-8 with sorted object keys, no whitespace separators, unescaped Unicode, and no NaN/Infinity, then SHA-256. Array order is significant. Strings must already be NFC; validators do not silently normalize authored content. Digest integrity detects changes; any caller can compute a new digest. It does not prove authorship, rights, approval, or trusted tenant identity. This algorithm is a documented local canonicalization, not a claim of RFC 8785 conformance.

`load_package(raw: bytes) -> dict` validates and raises `ValueError` on rejection. `validate_package(package) -> list[str]` returns contract errors. `compute_digest(package) -> str` supports an offline producer. Render every content field as text; this schema does not sanitize HTML for use with an HTML renderer.

## Admission contract agreed with API owner

Authenticated reviewer imports a draft through `POST /api/content-packages`. Tenant and actor come from trusted membership; no package field grants authority. `(tenant, packageId, version)` is immutable: identical replay is idempotent, conflicting digest is 409. Explicit publication uses `POST /api/content-packages/{id}/publish` with expected_digest and expected_revision; stale requests fail closed. Local course/lesson IDs are derived by the server from tenant and package/version identity, while exact source JSON is preserved for authorized export at `GET /api/courses/{id}/package`. A new package version creates a separate course; existing learning history must not be rewritten. Published content is immutable.

The course API retains lesson.content as a plain string and exposes objectives, practice, assessment, rubric, rights, provenance and version metadata. Assessment character limits must be enforced by the server. Rubric scores describe an authoring guide for human judgment; current feedback workflow does not calculate grades or issue credentials. Contract validity and local publication do not establish pedagogical efficacy.

## Original sample and independent offline checks

`content/examples/agent-engineering-basics.fa.json` contains three original Persian lessons, each with an applied practice task, three measurable objectives, a final evidence-based submission and a four-criterion human rubric. It was authored with OpenAI Codex assistance in this local pilot; no external text was copied. `createdAt` is the declared authoring date at UTC midnight, not a signed event timestamp. Rights identifier `LicenseRef-NIKWAY-Local-Review` permits this local review exercise only; broader redistribution requires an owner decision and is not granted by this profile. It does not change repository licensing.

The sample guides goal/contract design, trust boundaries, and evidence/revision review. Learners may submit an explicitly labelled test plan when no execution environment exists; neither the content nor validator fabricates successful test results. Reviewer feedback and a new submission support revision; automatic scoring is not claimed.

Run `python -m unittest content.test_validate_package -v` and `python -m content.validate_package content/examples/agent-engineering-basics.fa.json` with the pinned dependency. On 2026-11-25, 22 offline tests passed: original roundtrip, canonical key order, tampering, authority fields, unknown references, duplicate IDs/JSON keys, gaps, objective coverage, anchor completeness, scoring/character bounds, rubric linkage, false publication, third-party material, non-finite numbers, Unicode normalization and size. The committed invalid example has a recomputed valid digest but an unknown objective reference, proving checksum alone is insufficient. Live authorization, concurrency, publication and learning-journey acceptance require independent runtime tests against the actual API.

## Concurrent Content Factory implementation discovered after initial review

A subsequent read-only inventory found Content Factory commit `c979c74` on `content-factory-mvp`, adding `content_factory/cf/contracts.py` and a local repository implementation. Its Pydantic `ComponentInput` version 1.0.0 is a **different wire contract**: one component with `semanticVersion`, `locale`, competency and evidence identifiers, accessibility assertions, audience, duration, provenance and body sections/exercise/questions. Questions include answer keys. Our course package version 1.0.0 does not denote compatibility with that independently named schema version.

No actual conversion or service connection has been tested. The crosswalk above describes conceptual alignment with the pinned proposals, not successful interoperability with this newer implementation. A future adapter must explicitly map component revisions to course assemblies, obtain genuine competency/evidence/accessibility metadata, preserve provenance and rights, and separate learner-visible content from answer keys. Inventing missing metadata or copying assessment answers into learner lesson text is unacceptable. This implementation remains an independently validated offline course producer and local Learning OS admission profile; actual Content Factory export/import is deferred pending that contract reconciliation.
