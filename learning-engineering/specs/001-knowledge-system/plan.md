# Learning Engineering Implementation Plan

> For agentic workers: execute assigned independent tasks using TDD; parent integrates and a separate QA agent reviews.

**Goal:** Operational local accumulation and exchange with honest acceptance boundaries.
**Architecture:** File-backed canonical JSON and derived Markdown/search. No infrastructure.
**Tech Stack:** Python 3, jsonschema Draft 2020-12, unittest, Git.
**Spec:** [spec.md](spec.md).

## Global constraints
Only learning-engineering/ additions and append-only architecture changes; preserve main.
Never label machine checks as human approval or local round-trip as deployed interoperability.

## Tasks
- [x] Research: verify authoritative sources and separate rights in research/; unresolved pending.
- [x] Semantic/curriculum: semantics/ and records/ with bilingual definitions and PDCA alignment.
- [x] Knowledge: engine/knowledge.py, schemas/record.schema.json, tests/test_knowledge.py;
  test malformed shape, duplicate revisions, missing/wrong-kind references, prerequisite cycles,
  delivery pending-rights rejection and Persian normalization; observe red then green.
- [x] Integration: engine/exchange.py, schemas/package.schema.json, tests/test_exchange.py;
  build_package(records,id,revision), receive_package(package,store,context); test digest tamper,
  conflicting replay, unsupported contract, isolation, quarantine and atomic preservation.
- [x] CLI: validate/search/render/accumulate/export/import/pilot; use temporary test directories.
- [x] QA: independent hostile-input and provenance review; resolve findings and rerun suite.
- [x] Receipt: source/semantic/schema/pilot/owner gates, preserve baseline, commit and push only dedicated branch.

## Review focus
Fail closed on malformed nested JSON; exclude unknown media/tenant payload fields.
No delivered pending evidence; same revision cannot mutate; false metadata is not authentication.
Do not confuse PDCA with Deming's PDSA preference or synthetic pilot with learner results.
