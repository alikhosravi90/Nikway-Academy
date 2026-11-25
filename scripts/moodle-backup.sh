#!/usr/bin/env bash
# Consistent local snapshot: maintenance + stop cron, dump DB/data, encrypt streams.
set -euo pipefail
cd "$(dirname "$0")/.."
c=(scripts/moodle-compose.sh)
r=infra/moodle/runtime
out="$r/backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$out"; chmod 700 "$out"
pass="$r/backup_passphrase"
[[ -f "$pass" ]] || exit 1
"${c[@]}" exec -T -u www-data moodle php /var/www/moodle/admin/cli/maintenance.php --enable
"${c[@]}" stop cron
cleanup() { "${c[@]}" exec -T -u www-data moodle php /var/www/moodle/admin/cli/maintenance.php --disable; "${c[@]}" start cron; }
trap cleanup EXIT
"${c[@]}" exec -T db pg_dump -U moodle -d moodle -Fc | gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/moodle.dump.gpg"
"${c[@]}" exec -T moodle tar -C /var/moodledata --exclude=./cache --exclude=./localcache --exclude=./temp --exclude=./sessions -czf - . | gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/moodledata.tgz.gpg"
gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/config.php.gpg" "$r/config.php"
chmod 600 "$out"/*
printf 'Encrypted backup: %s\n' "$out"
