# Learning knowledge system specification
Baseline: 18a580a. Owner explicitly authorized autonomous implementation and parallel agents.
All seven architecture documents were read; their text remains preserved.

## Design decision
Use Git-versioned UTF-8 JSON, Python 3.10+ and JSON Schema Draft 2020-12; deterministic
Markdown rendering and normalized substring search require no server or database.
SQLite/graph services would duplicate canonical storage and increase deployment work;
LMS-native authoring would violate portability. This choice is the implementation team's.
Spec Kit CLI was not installed; apply its specification/plan/task separation locally without
bootstrapping another project or changing branches. Reference: https://github.com/github/spec-kit

## Requirements
R1: Validate typed, bilingual, provenance-bearing immutable records and graph references.
R2: Search Persian/English and render human-readable outputs from the same records.
R3: Incrementally accumulate records without overwriting an existing ID/version; review is
an explicit new revision, not an unauthenticated human-approval service.
R4: Verify sources with locators and separate item-level licensing evidence; uncertain means
pending verification. Web existence does not imply scientific truth or reuse permission.
R5: Exercise PDCA source -> evidence -> card -> concept -> competency -> objective ->
curriculum -> content specification -> assessment, including a rubric.
R6: Offline Content Factory/Learning OS exchange validates version, payload digest,
dependencies, idempotency and conflict rejection; pending material is quarantined.
R7: Preserve prior architecture and main; no release, merge, real learner data or credentials.
R8: Independent review and reproducible positive/negative tests precede completion.

## Boundaries and mistake prevention
Wrong record kinds/unknown fields: strict schemas (control at import boundary).
Missing references/incomplete chain: typed graph checks (control at import boundary).
Skipped review/rights: delivery gate rejects (control), but local metadata is not trusted identity.
Tampering/retry conflict: digest + immutable revision uniqueness (control).
No network integration, authentication or learning effectiveness is claimed by local fixtures.
G5 owner acceptance remains external. Persian linguistic quality requires a human reviewer.
