#!/usr/bin/env bash
# Consistent local snapshot: maintenance + stop cron, dump DB/data, encrypt streams.
set -euo pipefail
cd "$(dirname "$0")/.."
c=(scripts/moodle-compose.sh)
r=infra/moodle/runtime
out="$r/backups/$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "$r/backups"
mkdir "$out"; chmod 700 "$out"
pass="$r/backup_passphrase"
[[ -f "$pass" ]] || exit 1
umask 077
state=$(mktemp "$r/maintenance-state.XXXXXX")
state_php='define("CLI_SCRIPT",true);require "/var/www/moodle/config.php"; $f=$CFG->dataroot."/climaintenance.html"; if($argv[1]==="capture"){echo json_encode(["enabled"=>get_config("","maintenance_enabled"),"later"=>get_config("","maintenance_later"),"file"=>is_file($f)?base64_encode(file_get_contents($f)):null]);}else{$s=json_decode(stream_get_contents(STDIN),true,512,JSON_THROW_ON_ERROR);foreach(["enabled"=>"maintenance_enabled","later"=>"maintenance_later"] as $k=>$name){if($s[$k]===false){unset_config($name,null,true);}else{set_config($name,$s[$k],null,true);}}if($s["file"]!==null){file_put_contents($f,base64_decode($s["file"]));}elseif(is_file($f)){unlink($f);}}'
"${c[@]}" exec -T -u www-data moodle php -r "$state_php" capture > "$state"
cron_running=$("${c[@]}" ps --status running -q cron)
cleanup() {
 local result=$?
 trap - EXIT
 set +e
 "${c[@]}" exec -T -u www-data moodle php -r "$state_php" restore < "$state" || result=1
 if [[ -n "$cron_running" ]]; then "${c[@]}" start cron || result=1; fi
 rm -f "$state"
 exit "$result"
}
# Register before the first maintenance/cron mutation, including partial failures.
trap cleanup EXIT
"${c[@]}" exec -T -u www-data moodle php /var/www/moodle/admin/cli/maintenance.php --enable
"${c[@]}" stop cron
"${c[@]}" exec -T db pg_dump -U moodle -d moodle -Fc | gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/moodle.dump.gpg"
"${c[@]}" exec -T moodle tar -C /var/moodledata --exclude=./cache --exclude=./localcache --exclude=./temp --exclude=./sessions -czf - . | gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/moodledata.tgz.gpg"
gpg --batch --yes --pinentry-mode loopback --passphrase-file "$pass" --symmetric --cipher-algo AES256 -o "$out/config.php.gpg" "$r/config.php"
(cd "$out" && sha256sum moodle.dump.gpg moodledata.tgz.gpg config.php.gpg > SHA256SUMS)
printf 'complete\n' > "$out/COMPLETE"
chmod 600 "$out"/*
printf 'Encrypted backup: %s\n' "$out"
