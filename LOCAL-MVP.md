# NIKWAY Academy local MVP

> Historical frozen baseline. For the separate patched content candidate, see [SECURE-CONTENT-MVP.md](SECURE-CONTENT-MVP.md). The six findings below describe the preserved baseline, not the new candidate.

Status: **PARTIAL — operational local MVP; release NO-GO**. This candidate runs locally with synthetic learners and persistent data. Six HIGH findings remain in the pinned Keycloak image; security acceptance, merge and release are blocked. This is not the complete target Academy platform.

## Open and sign in

Open **http://localhost:18401** on the installed host. API health: http://localhost:18400/api/health. Identity realm: http://localhost:18480/realms/academy. All published ports bind to loopback; PostgreSQL has no host port.

Generated credentials are in `infra/runtime/credentials.json` (private local file, mode 0600). Use `learner-a`, `learner-b` or `reviewer-a`; read their generated passwords locally. Never paste this file into GitHub. The two learners belong to separate synthetic tenants; reviewer-a belongs to tenant A. Authentication is real Keycloak authorization-code flow with PKCE S256. Browser tokens stay in memory.

Learners can sign in, enroll, complete ordered lessons, submit work, see progress and register for a workshop. The reviewer can review another learner's submitted work within the same tenant. Reviews enforce revision checks and prohibit self-review. Workshop registration enforces capacity and repeated requests are idempotent. The frontend is Persian and supports narrow screens.

## Install, start, stop and restart

Prerequisites: Linux Docker Engine with Compose v2/BuildKit, Python 3 and GnuPG; internet access for the initial pinned images and packages. The service memory limits total 2.25 GiB after migration, plus host/build overhead. Use a host with additional free capacity. These commands run from the repository root:

```sh
scripts/local-install.sh
scripts/local-start.sh
scripts/local-compose.sh ps
scripts/local-stop.sh
scripts/local-start.sh
scripts/local-restart.sh
```

Install generates private random local configuration and builds the images. Start waits for migrations, database, identity, API and UI readiness. Stop and restart preserve data. Existing generated configuration is preserved; incomplete configuration fails closed. Do not run `down -v`, prune volumes or overwrite configuration to resolve an error. Use `localhost`, consistently, for browser authentication.

For a clean reproduction, check out the reviewed candidate commit from [PR #14](https://github.com/alikhosravi90/Nikway-Academy/pull/14) and run install/start. Record the exact commit with `git rev-parse HEAD`. Default ports must be free. The existing installation is in the `integration` worktree; the publication branch is a sanitized snapshot and deliberately excludes intermediate private recovery history.

Persistent volume: `nikway-academy-local_academy-db-v2`, containing separate Academy and Keycloak databases. The previous Debian PostgreSQL volume is preserved. Never mount its physical files into Alpine PostgreSQL; the tested migration used encrypted logical dumps and table-by-table comparison. Once new writes occur, the old volume is a historical snapshot, not a current rollback target.

## Backup and restore verification

```sh
scripts/backup-local.sh academy
scripts/backup-local.sh keycloak
scripts/restore-local-test.sh infra/runtime/backups/academy-TIMESTAMP.dump.gpg
```

GnuPG prompts for a passphrase. Back up both databases. Keep the passphrase and private runtime configuration securely outside Git. For automated full-table verification, set `BACKUP_PASSPHRASE_FILE` to an absolute path to a private passphrase file, then run:

```sh
python3 scripts/restore-local-verify.py infra/runtime/backups/academy-TIMESTAMP.dump.gpg
python3 scripts/restore-local-verify.py infra/runtime/backups/keycloak-TIMESTAMP.dump.gpg
```

Verification restores each archive into a newly created disposable database, compares every table's sorted-row SHA256 and row count against the archive, and removes only that disposable database. It does not overwrite live data. The preserved-source-to-new-volume migration additionally exercised actual service startup and authentication. See [migration receipt](evidence/postgres-volume-migration.json), [final restore drill](evidence/final-recovery-drill.json) and [runtime instructions](infra/README.md). Scheduled backups, retention, RPO/RTO commitments and production disaster recovery are not established.

## Validation and traceability

Run the operational security tests against the running local services:

```sh
python3 scripts/validate_docs.py
python3 scripts/validate_missions.py --self-test
python3 -m unittest discover -s backend/tests -p test_integration.py -v
python3 scripts/validate_tool_kill_switch.py
```

The security integration suite briefly revokes and restores learner-a membership; avoid concurrent learner activity during that suite. The kill-switch test starts an isolated current-image API container on loopback port 18402, then removes only that test container. Frontend checks require Node/npm and Playwright Chromium:

```sh
cd frontend
npm ci
npx playwright install chromium
npm run test:e2e
```

The [final acceptance receipt](evidence/local-mvp-acceptance.json) and [release manifest](release-manifest.json) link exact evidence, image identities and measurement boundaries. Earlier evidence is preserved, including failures and subsequent corrections; old passing receipts are not proof of the final commit. [GitHub Actions](https://github.com/alikhosravi90/Nikway-Academy/actions) validates the candidate independently. No skipped browser test counts as a pass.

Measured final idle service memory was about 541 MiB. Fifty sequential authenticated course reads returned successfully with median 5.992 ms and p95 7.578 ms; this is a local latency sample, not a capacity or throughput benchmark. [Resource, lifecycle and latency receipt](evidence/final-lifecycle-performance.json).

The [machine-readable mission portfolio](missions/local-mvp/manifest.json) defines contracts, dependency scheduling, acceptance criteria and issue links for M01–M12 ([issues #2–#13](https://github.com/alikhosravi90/Nikway-Academy/issues)). Four concurrent workers covered sixteen logical roles. Independent validators tested implementation from another worker; logical role assignments do not imply sixteen simultaneously running agents. The environment supports four concurrent agent slots, so a higher limit was not claimed or introduced.

## Security and functional boundaries

Database membership is authoritative on every request. The API uses a non-owner role with forced row-level security; tenant parameters and token attributes cannot select a different tenant. The migration role is isolated from the API. Audit records are append-only to the application role. Tool execution is limited to authenticated, tenant-bound `learning.progress`, with a kill switch, audit trail, output bound and a serialized per-subject rate budget.

This tool endpoint is not an MCP server. LLM providers, AI tutor, external MCP, video conferencing, catalog authoring, multiple memberships per user, credentials issuance and production email are unavailable. The UI reports service availability; other limits are documented here. The recovered frontend prototype, with documented synthetic-name redactions, is not substituted for server functionality. No real learner data or paid provider requests were needed.

The selected API, frontend and hardened PostgreSQL images have no HIGH/CRITICAL findings in the recorded Trivy scan. Keycloak 26.8.2 retains six HIGH findings (including a Guava finding with a newer upstream fix); unsupported JAR surgery was not performed. A supported remediation or explicit reviewed exception, rescan and identity regression are required before release approval. Local HTTP/development identity settings are restricted to this local synthetic MVP. Repository licensing remains unselected; third-party tooling license inventory is recorded separately.
