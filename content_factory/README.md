# Content Factory — runnable local MVP

**GO: bounded local synthetic trial. NO-GO: production, real learner pilot, public publication or release.**

This implements the approved [architecture](../architecture/content-factory/README.md) on `content-factory-mvp`, based on `content-factory` at c861651. No merge or GitHub Release is part of this work.

## Run locally

Prerequisites: Docker, `uv`, and free loopback ports 18532 (dedicated PostgreSQL) and 18500 (API). Existing Academy services on 18400/18401/18480 are neither reconfigured nor stopped. Commands below run from this directory.

```bash
uv sync --frozen
.venv/bin/python scripts/local.py setup
.venv/bin/python scripts/local.py serve
```

In another terminal:

```bash
.venv/bin/python scripts/local.py test -q --junitxml=evidence/tests.xml
.venv/bin/python scripts/demo.py .runtime/demo
.venv/bin/python scripts/probe_learning_os.py
.venv/bin/python scripts/validate.py
```

Open http://127.0.0.1:18500/docs for the local API. The demo calls actual HTTP routes and saves text.md, lesson.html, quiz.json, manifest.json, a learner ZIP and an instructor ZIP. Open `.runtime/demo/lesson.html` in a browser. Quiz scoring is exercised by tests; the HTML is a readable self-assessment, not an interactive exam runner.

`setup` creates only container `nikway-content-factory-mvp-db`, with 256 MiB memory/1 CPU limits, and stores data under ignored `.runtime/pgdata`. It refuses an occupied container name, never deletes existing data, and retains an existing configuration. After a host restart use `docker start nikway-content-factory-mvp-db`, then `serve`. Stop this API with Ctrl+C; stop only its database with `docker stop nikway-content-factory-mvp-db`. Do not remove the data directory to restart.

Credentials are generated per installation, hashed in the database, expire after seven days and stay in `.runtime/config.json` (0600). The API process receives only the restricted database connection and object path; admin credentials are used only by setup/tests/operator recovery. Do not commit or share `.runtime`, tokens or backup contents. Swagger's Authorize control accepts one of the local tokens from that private file. Tokens have author/reviewer/consumer roles; they are for localhost testing, not production identity. Database.provision/revoke are operator-only helpers for credential renewal/revocation; no HTTP admin endpoint exists.

If an existing system `uv` cache is damaged, use an isolated cache, e.g. `UV_CACHE_DIR=.runtime/uv-cache uv sync --frozen --reinstall`; do not delete a shared cache.

## What works

- One strict camelCase [contract](CONTRACT.md) shared with the Learning Engineering proposal, plus generated JSON schema.
- PostgreSQL immutable revisions, separate lifecycle states, tenant RLS, expiring/revocable credentials, independent-reviewer checks, optimistic concurrency and immutable audit/outbox events.
- Digest-addressed tenant-separated filesystem object storage; metadata and state changes are transactional. A failed write can leave a harmless unreferenced object, reported without deletion.
- Persisted Plan → Do → Check → Act: objective, draft production, structural checks, reviewer-controlled local candidate. A failed check requires a new corrected plan. No automated factual validation or human review is claimed.
- Deterministic text/HTML/quiz/ZIP generation, separate instructor answers, exact rendition hashes and reusable pinned dependencies across two courses.
- Transitive withdrawal checks, durable consumer-event deduplication, failure-closed delivery, read-only live Academy probe and a separately identified local contract consumer.
- Tenant-scoped snapshot/restore into a fresh `cf_restore_` database, checksum verification, matching immutable objects, search rebuild from authoritative rows and orphan report. Tests create and drop only their own disposable recovery databases in this isolated cluster.

## Existing assets reused

- `content-factory` c861651: approved architecture, benchmarks and gate definitions, preserved unchanged.
- `learning-engineering` d8d3347: ownership and minimum object contract; normalized locally without changing that branch.
- `mission/local-mvp-release` 7be59d7: inspected backend API/auth/data patterns; reused FastAPI/Pydantic/psycopg technology/version family and an already cached PostgreSQL 16 image. No source files or migrations from that runtime were overwritten.
- Running Academy API: read-only `/api/health`, `/api/openapi.json`, unauthenticated `/api/courses`; no login, writes, new enrollments or production records.

## Limits and decisions

This MVP uses filesystem objects in place of S3 and local database-backed tokens in place of OIDC. There is no semantic search index, external competency resolver, background event transport, standard learning-package adapter or certified interoperability. PostgreSQL metadata search is authoritative; no index-rebuild service is needed for this profile.

Local review uses synthetic identities and notes. It proves workflow controls, not that a human approved content. The Persian PDCA fixture is original AI-assisted educational text informed by the [ASQ PDCA overview](https://asq.org/quality-resources/pdca-cycle), with invented numerical examples and internal-trial-only rights. External `permission_verified` records are structurally representable, but the current renderer uses a synthetic attribution footer; real external content rendering is not approved for this trial.

Candidate delivery is scoped by tenant and consumer credential; actual enrollment enforcement belongs to Learning OS and is not integrated. Offline ZIP copies cannot be revoked retroactively. No real learner data is stored. Learning OS currently lacks the required import/candidate API, so an end-to-end live integration is **not established**.

The suite emits one upstream Starlette/httpx deprecation warning; tests still pass. Recovery snapshot/object tamper rejection is implemented but those two negative paths were not separately exercised; missing-object detection and successful isolated restore were tested. Human pedagogy, accessibility certification, source conversation recovery and real corpus rights review remain open. See [GO/NO-GO report](REPORT.fa.md), [machine-readable gates](evidence/gates.json) and [review record](evidence/review.md).
