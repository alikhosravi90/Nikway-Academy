#!/usr/bin/env bash
# Restore only into a newly generated disposable database. Never overwrite academy.
set -euo pipefail
gpg_args=()
if [[ -n "${BACKUP_PASSPHRASE_FILE:-}" ]]; then
  [[ -r "$BACKUP_PASSPHRASE_FILE" ]] || { echo 'Passphrase file is unreadable.' >&2; exit 1; }
  gpg_args=(--batch --pinentry-mode loopback --passphrase-file "$BACKUP_PASSPHRASE_FILE")
fi
cd "$(dirname "$0")/.."
[[ $# == 1 && -f "$1" ]] || { echo 'Usage: scripts/restore-local-test.sh ENCRYPTED_BACKUP' >&2; exit 1; }
db="academy_restore_$(date +%s)_${RANDOM}"
cleanup() { scripts/local-compose.sh exec -T postgres dropdb -U postgres --if-exists "$db" >/dev/null; }
trap cleanup EXIT
scripts/local-compose.sh exec -T postgres createdb -U postgres "$db"
gpg "${gpg_args[@]}" --decrypt "$1" | scripts/local-compose.sh exec -T postgres pg_restore -U postgres --exit-on-error -d "$db"
scripts/local-compose.sh exec -T postgres psql -U postgres -d "$db" -v ON_ERROR_STOP=1 -c "SELECT schemaname, tablename FROM pg_tables WHERE schemaname NOT IN ('pg_catalog', 'information_schema') ORDER BY 1, 2;"
echo 'PASS: encrypted backup restored into disposable database; cleanup follows.'
