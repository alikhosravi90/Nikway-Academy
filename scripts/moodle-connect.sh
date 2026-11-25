#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test -f infra/moodle/runtime/config.php
test -f infra/runtime/.env
docker network inspect nikway-academy-content_default >/dev/null
target=infra/moodle/runtime/compose.auth.yaml
if [[ -f "$target" ]]; then
  cmp infra/moodle/compose.academy.yaml "$target"
else
  install -m 600 infra/moodle/compose.academy.yaml "$target"
fi
python3 infra/moodle/auth-keycloak.py --academy-runtime infra/runtime --output infra/moodle/runtime/auth.json
scripts/moodle-compose.sh up -d --no-build --wait moodle
python3 infra/moodle/auth-network.py
container=$(scripts/moodle-compose.sh ps -q moodle)
cleanup() { docker exec "$container" rm -f /tmp/nikway-auth.json >/dev/null; }
trap cleanup EXIT
docker cp infra/moodle/auth-configure.php "$container":/tmp/nikway-auth-configure.php
docker cp infra/moodle/runtime/auth.json "$container":/tmp/nikway-auth.json
docker exec "$container" php /tmp/nikway-auth-configure.php /tmp/nikway-auth.json
