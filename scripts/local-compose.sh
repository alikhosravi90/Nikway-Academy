#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f infra/runtime/.env ]] || { echo 'Run python3 scripts/local-init.py first.' >&2; exit 1; }
exec docker compose --env-file infra/runtime/.env -p nikway-academy-local "$@"
