# Secure content Local MVP candidate

This is a separate local candidate on `mission/secure-content-mvp`, based on frozen commit `7be59d794a7e73cdb32b7fd222f63473e83d815c`. No merge or release is authorized. The original baseline remains on port18401 and its database is preserved. Final evidence and decision are recorded in `evidence/security-content/acceptance.json` and `secure-content-manifest.json`.

## Use the installed candidate

Open **http://localhost:18501**. API: `http://localhost:18600`; Keycloak: `http://localhost:18580`. These ports bind only to loopback. Read the generated synthetic account credentials locally from `infra/runtime/credentials.json` (0600): learner-a and reviewer-a share tenant A; learner-b is tenant B. Do not upload that file. Use `localhost` consistently for PKCE redirects.

The Persian sample **مبانی مهندسی عامل: از هدف تا شواهد** has three lessons, practices, objectives, a final submission, and a human rubric. Sign in as learner-a, enroll, complete lessons in order, and submit evidence. Sign in as reviewer-a to request revision or accept. Human feedback is operational; automatic grading, certification and pedagogical efficacy are not claimed.

## Portable content boundary

An offline producer creates a package under [the strict schema](contracts/content-package.schema.json). It does not need Academy, a tenant identifier, credentials or a running Content Factory. The [bridge contract](contracts/learning-content-bridge.json) defines trusted local admission and the [contract notes](docs/security-content-contract.md) document provenance, rights, semantic validation and remaining mappings.

```sh
# Use the pinned backend environment (uv sync --project backend --group dev).
backend/.venv/bin/python -m content.validate_package content/examples/agent-engineering-basics.fa.json
backend/.venv/bin/python scripts/content-local.py import content/examples/agent-engineering-basics.fa.json
# Explicit local publication, authenticated as generated reviewer-a:
backend/.venv/bin/python scripts/content-local.py import content/examples/agent-engineering-basics.fa.json --publish
backend/.venv/bin/python scripts/content-local.py export COURSE_UUID /private/new-export.json
```

Publication is tenant-local. Immutable package/version identities, digest/revision preconditions, membership checks and forced RLS prevent draft disclosure and conflicting overwrite. Export preserves the source JSON exactly; imports of another version preserve prior learning history. A digest proves integrity only. Original sample rights cover local review only.

The independently developed Content Factory `ComponentInput@c979c74` is a different contract. No running producer service or conversion is claimed. An actual adapter needs explicit competency/evidence/accessibility/rights mappings and separation of assessment answer keys. This is a remaining integration gate, not permission to fabricate metadata. No general SCORM, xAPI or Common Cartridge conformance is claimed.

## Reproduce and operate

Prerequisites: Docker Engine/Compose v2 with BuildKit, Python3, GnuPG, internet for initial pinned artifacts, and adequate build memory. The measured bounded source build used2CPU/3GiB; runtime limits total2.25GiB plus transient migration and host overhead. Start from a clean checkout of this candidate. Choose free loopback ports/project before first initialization if retaining another installation:

```sh
ACADEMY_PROJECT=nikway-academy-content ACADEMY_UI_PORT=18501 ACADEMY_API_PORT=18600 ACADEMY_IDP_PORT=18580 python3 scripts/local-init.py
scripts/local-install.sh
scripts/local-start.sh
scripts/local-stop.sh
scripts/local-start.sh
scripts/local-restart.sh
```

Generated configuration is retained across runs. Default ports for a fresh isolated host are18401/18400/18480. On this workstation only, an ignored Compose network override uses a verified free subnet because default Docker pools were exhausted; no existing network was pruned. The installed candidate volume is `nikway-academy-content_academy-db-v2`. Never run `down -v`, reset configuration or attach an old physical database volume to a different distribution.

Both databases require backups. Set `BACKUP_PASSPHRASE_FILE` to a private0600 passphrase file outside Git, then:

```sh
scripts/backup-local.sh academy
scripts/backup-local.sh keycloak
python3 scripts/restore-local-verify.py infra/runtime/backups/academy-TIMESTAMP.dump.gpg
python3 scripts/restore-local-verify.py infra/runtime/backups/keycloak-TIMESTAMP.dump.gpg
```

The verifier restores into disposable databases and compares every table's row count and canonical row hash. It never overwrites the live databases. Protect backups, passphrase and generated runtime configuration together. Scheduled retention and production RPO/RTO are outside this local MVP.

## Identity remediation and ownership

The preserved official Keycloak image still has six High findings. The new candidate rebuilds exact Keycloak26.8.2 source with fixed Guava33.7.2-jre and a pinned maintained Temurin21 Alpine runtime, removing the vulnerable SQLite dependency chain. The full candidate image scans0High/0Critical without suppressions or removal of scanner metadata. See [root causes and alternatives](evidence/security-content/identity-root-cause.md), [source recipe](infra/identity/Dockerfile.keycloak-source) and [build evidence](evidence/security-content/source-build.json).

This is a **locally maintained derivative**, not a vendor-issued supported patch. Maven compilation skipped upstream tests; Academy unit, real PostgreSQL/OIDC/security/content/browser and recovery checks are separate evidence. Local development mode and loopback HTTP are deliberate local boundaries, not production settings. A zero High/Critical scan is time- and scanner-database-specific, not absence of every vulnerability. Ongoing update ownership and final user approval remain required before merge/release.

Dex was operationally benchmarked but had28High findings and incompatible subject/audience contracts; anonymous access to the evaluated Chainguard image was unavailable. Neither was silently substituted. No spending, public deployment, identity migration or external service connection occurred.
