# Content Factory MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a local, versioned, tenant-isolated content factory producing a synthetic Persian PDCA learning package and evidence for all ten gates, without merge or release.

**Architecture:** Extend the approved content-factory branch in its existing isolated worktree. Use PostgreSQL with RLS, immutable revision JSON + content-addressed local objects, FastAPI and database-backed expiring local credentials. Reuse Academy's FastAPI/Pydantic/PostgreSQL dependency baseline and live OpenAPI for a read-only compatibility probe; no changes to the existing Academy runtime. A local consumer validates prepared manifests; it is explicitly not the running Learning OS.

**Tech Stack:** Python 3.12, FastAPI, Pydantic 2, psycopg 3, PostgreSQL 16, pytest/httpx, HTML/Markdown/JSON/ZIP.

**Spec:** architecture/content-factory/README.md and validation-gates.md, approved by the user in the current chat; Learning Engineering CONTRACT at d8d3347.

## Global Constraints

- No merge, GitHub Release, production publication, existing-service mutation or real learner data.
- Freeze original branch at c861651; implement on content-factory-mvp.
- A local candidate is not a published release; human quality/rights approval remains pending.
- Git + PostgreSQL + filesystem object adapter for MVP; S3, OIDC integration and standards certification are deferred with explicit gates.
- Prefer known local images and lock Python dependencies. Credentials remain in ignored .runtime with mode 0600.

## Review Focus

- Missing/forged tenant identity must fail at API and database boundaries.
- Stale/concurrent edits and revoked dependencies must never mutate pinned candidates.
- Unknown rights, missing provenance and bad quiz scoring must prevent preparation.
- Tampered/missing objects and hostile HTML must fail or escape safely.
- Replayed candidate requests and consumer events must preserve idempotency without hiding changed payloads.

## Task 1: Unified contract and immutable repository

Files: content_factory/cf/contracts.py, db.py, store.py, schema.sql; tests/test_repository.py; fixtures/pdca.json.
Interfaces: ComponentInput (Learning Engineering camelCase fields); Repository.create_revision(ctx, data, expected_revision), get_revision, review, withdraw, search; trusted Context from database.
- [ ] Write negative contract, stale edit, immutability, rights, tenant and object-integrity tests; run and observe missing behavior.
- [ ] Implement versioned components, content-addressed objects, dependency/source validation, expiring opaque tokens and RLS with least-privilege role.
- [ ] Run pytest tests/test_repository.py; expected all pass; commit.

## Task 2: PDCA production and reusable packages

Files: cf/pipeline.py, render.py; tests/test_pipeline.py.
Interfaces: Pipeline.plan/do/check/act; Repository.prepare(course_id, refs, idempotency_key); build_package(candidate) produces text.md, lesson.html, quiz.json, manifest.json, ZIP.
- [ ] Write failing tests for PDCA order, failed checks, scoring, two-course pinned reuse, withdrawal, idempotency and escaped/answer-free learner HTML.
- [ ] Implement persisted PDCA transitions, deterministic rendition generation, candidate manifests and outbox; no publication route.
- [ ] Run pytest tests/test_pipeline.py; expected all pass; commit.

## Task 3: Local API and Learning OS boundary

Files: cf/api.py, consumer.py, cli.py; scripts/local.py; tests/test_api.py, test_consumer.py.
Interfaces: /v1 components, reviews, pipelines, candidates, packages, events; server derives tenant/role from credential. Consumer verifies version/digests and current candidate/dependency status before every delivery.
- [ ] Write failing authorization, revocation, replay, outage and unsupported-schema tests.
- [ ] Implement API, local setup/run/demo commands and consumer adapter. Inspect running Academy health/OpenAPI read-only; report missing ingestion API honestly.
- [ ] Run full pytest; expected all pass; commit.

## Task 4: Recovery, ten gates and runnable handoff

Files: scripts/validate.py, tests/test_recovery.py, evidence/*, README.md, CONTRACT.md, REPORT.fa.md.
Interfaces: backup/restore to separate disposable DB + object root; gate report records PASS_LOCAL/PARTIAL/BLOCKED with evidence and remaining owner actions.
- [ ] Write restore/tamper tests, run failing then implement backup/reconciliation.
- [ ] Run full tests, real HTTP demo, recovery and live read-only probe; record exact results, hashes and runtime versions.
- [ ] Inspect generated Persian HTML and downloadable ZIP; obtain fresh code review and fix consequential findings with regression tests.
- [ ] Commit/push independent branch, verify remote/base and clean status. No merge/release. GO only for bounded local synthetic trial; broader GO requires open human/integration gates.
