#!/usr/bin/env bash
# Encrypt a consistent Academy database dump; passphrase is prompted by GnuPG.
set -euo pipefail
gpg_args=()
if [[ -n "${BACKUP_PASSPHRASE_FILE:-}" ]]; then
  [[ -r "$BACKUP_PASSPHRASE_FILE" ]] || { echo 'Passphrase file is unreadable.' >&2; exit 1; }
  gpg_args=(--batch --pinentry-mode loopback --passphrase-file "$BACKUP_PASSPHRASE_FILE")
fi
cd "$(dirname "$0")/.."
database="${1:-academy}"
[[ "$database" == academy || "$database" == keycloak ]] || { echo 'Only academy/keycloak are supported.' >&2; exit 1; }
umask 077
mkdir -p infra/runtime/backups
output="infra/runtime/backups/${database}-$(date -u +%Y%m%dT%H%M%SZ).dump.gpg"
temporary="${output}.partial"
trap 'test ! -f "$temporary" || unlink "$temporary"' EXIT
scripts/local-compose.sh exec -T postgres pg_dump -U postgres -d "$database" -Fc | gpg "${gpg_args[@]}" --symmetric --cipher-algo AES256 --output "$temporary"
mv "$temporary" "$output"
printf '%s\n' "$output"
