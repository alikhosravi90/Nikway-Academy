#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
# Reuse the existing candidate identity/database and installed Moodle. No migrations.
for network in nikway-academy-content_default nikway-academy-moodle_private; do
  docker network inspect "$network" >/dev/null
done
scripts/frontend-design-compose.sh build
python3 scripts/moodle-webservice-setup.py
python3 scripts/frontend-design-connect.py
docker volume create nikway-academy-design-secrets >/dev/null
docker run --rm --pull never --network none --user 0 --entrypoint sh \
  -v "$PWD/infra/moodle/runtime/webservice-tokens.json:/source/tokens.json:ro" \
  -v nikway-academy-design-secrets:/target nikway-academy-design-api:local \
  -c 'cp /source/tokens.json /target/webservice-tokens.json && chown 10001:10001 /target/webservice-tokens.json && chmod 600 /target/webservice-tokens.json'
scripts/frontend-design-compose.sh up -d --no-build --pull never
printf '%s\n' 'Local preview: http://localhost:18901/ ; original Academy/Moodle services preserved.'
