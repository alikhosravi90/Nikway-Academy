# Isolated local Moodle

Moodle5.3.1 on official PHP8.4 Alpine/FPM with distro nginx and a fresh PostgreSQL17 volume. This project is `nikway-academy-moodle`; HTTP binds only127.0.0.1:18701. Existing Academy projects and volumes are not modified.

```sh
python3 scripts/moodle-init.py
scripts/moodle-compose.sh build
scripts/moodle-compose.sh up -d db moodle
python3 scripts/moodle-install.py
scripts/moodle-compose.sh up -d cron
```

Configuration and bootstrap credentials are private0600 files under ignored `infra/moodle/runtime` (directory0700). `credentials.json` is for the owner only; never commit or print it. App path `/var/www/moodle`, public webroot `/var/www/moodle/public`, CLI `/var/www/moodle/admin/cli`. The database application role owns the Moodle database but is not superuser, role creator, database creator, or RLS bypass.

Lifecycle: `scripts/moodle-compose.sh stop`, `start`, `restart`. Do not use `down -v` on persisted data. Generated config is preserved on subsequent init attempts. An optional ignored `compose.auth.yaml` is loaded for the bounded identity connection; identity setup has its own script.

Backup after imports/auth provisioning and while no tests are writing:

```sh
scripts/moodle-backup.sh
python3 scripts/moodle-restore-verify.py infra/moodle/runtime/backups/TIMESTAMP
```

Backup enables maintenance, pauses cron, encrypts PostgreSQL dump, persistent Moodle files (excluding regenerable caches/sessions), and config with AES256. The passphrase stays in ignored `backup_passphrase`; preserve it separately for recovery. Verification restores into a random disposable DB and compares every COPY table's canonical data, then drops it; restores encrypted data archive into a temporary directory and compares each file SHA256 without overwriting the live volume. This does not prove a full fresh-volume application restoration. There is no real email sending. Local bootstrap uses synthetic accounts/data only.

The pinned maintained `microsoft/moodle-auth_oidc`5.3.0 plugin is included; no Microsoft365 suite. Core Moodle is GPLv3or later and plugin retains its GPL notice. Base/source hashes are pinned; Alpine package repository resolution means build is reproducible in procedure, not bit-identical across future package changes. This is an isolated local evaluation, not a production deployment.
