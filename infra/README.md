# Isolated local Academy runtime

Development and synthetic data only. Compose project `nikway-academy-local` owns its network and database volume. No existing services are reused. Host ports bind only to loopback: UI 18401, API 18400, Keycloak 18480. Use `http://localhost:18401` for browser sessions.

Prerequisites: Docker with Compose and BuildKit, Python 3, GnuPG. Run from repository root:

```sh
scripts/local-install.sh
scripts/local-start.sh
scripts/local-stop.sh
scripts/local-restart.sh
```

Install builds images; start creates only this project's resources. Stop preserves data; restart does not rerun initialization. Initial database scripts and realm import run only for a new database. Never remove its volume to change configuration. Existing generated configuration is preserved; partial configuration fails closed. `scripts/local-compose.sh ps` displays status without secrets. Do not publish `compose config` expanded output or `docker inspect` environments.

`infra/runtime/` is ignored. Generated `.env` and `credentials.json` have mode 0600, parent directory 0700. SQL and realm import files are 0644 to permit the containers' unprivileged users to read them, inside the private parent directory. Credentials must stay local. Browser test harnesses can consume `E2E_CREDENTIALS_FILE=<absolute path>/infra/runtime/credentials.json`; entries have username/password properties. Synthetic users: learner-a, learner-b, reviewer-a. Login uses authorization code with PKCE S256; password grants and registration are disabled. Tenant token claims are hints; backend membership authorization remains authoritative.

API receives only `DATABASE_URL` with non-owner/non-superuser/non-bypass role academy_app. One-shot `migrate` receives `MIGRATION_DATABASE_URL` with academy_owner; API waits for its successful completion. Keycloak has a separate database and role. PostgreSQL has no host port. PostgreSQL, Keycloak and Python base images are digest pinned; backend Dockerfile maintains its base pin. Resource caps total 2.75 GiB while migration runs, 2.25 GiB afterwards. Runtime resource measurements remain necessary.

## Encrypted Academy database recovery drill

```sh
scripts/backup-local.sh academy
scripts/backup-local.sh keycloak
scripts/restore-local-test.sh infra/runtime/backups/academy-TIMESTAMP.dump.gpg
```

GnuPG prompts for a passphrase. For automation, point `BACKUP_PASSPHRASE_FILE` at a private local file (absolute path), never a literal password in an argument. Backup streams a consistent custom-format `pg_dump` into AES256 GnuPG encryption. Restore decrypts directly into a newly created randomly named database, fails on restore errors, lists restored application tables, and drops only that disposable database on exit. It never overwrites `academy`. A successful restore proves dump restorability, not application-level equivalence; compare application counts/invariants separately. The optional database argument permits separate Academy and Keycloak backups. Run `scripts/restore-local-verify.py ENCRYPTED_BACKUP` with `BACKUP_PASSPHRASE_FILE` to compare every table's restored row count and sorted-row SHA256 against the encrypted archive; this does not require comparing a concurrently changing live database. Full disaster recovery still requires application and identity flow checks. Password-file retention, encryption key retention and backup lifecycle remain local operator responsibilities.

## Validation boundary

Compose syntax, shell syntax and generator idempotence can be checked without starting services. Image cache presence does not establish vulnerability status or license approval. No repository license is selected. Production TLS, operational backups, secret rotation, recovery objectives and deployment are outside this local runtime.

## Pinned security refresh and data-volume boundary

The selected PostgreSQL runtime is now built from pinned PostgreSQL 16 Alpine with `libxml2=2.13.9-r3` and `su-exec=0.3-r0`. The old Go-based gosu executable and alias are removed; the upstream entrypoint's single privilege-drop invocation uses `/sbin/su-exec` directly. Smoke validation must exercise initialization and shutdown/restart. Its TCP health check avoids marking the temporary socket-only initialization server ready.

`academy-db-v2` is a **new** named volume. Existing Debian database files must never be mounted into the Alpine runtime. The original `nikway-academy-local_academy-db` volume is retained; migrate application and identity databases by logical encrypted dump/restore, with per-table canonical digest comparison. Record the snapshot boundary and stop application writes before final handoff. Root coordinates service replacement only after candidate verification. Source-volume retention is not an automatic rollback plan once new writes occur.

Keycloak is pinned to 26.8.2. The measured security state is in `evidence/vulnerability-refresh.json`; do not interpret a functional local pass as release approval. The selected Keycloak image retains six HIGH findings, including Guava with an upstream fix version. Unsupported JAR replacement is not attempted. Release remains NO-GO until supported remediation or explicit reviewed exception, followed by rescan and identity regression tests.
