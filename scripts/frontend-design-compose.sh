#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${ACADEMY_ENV_FILE:-../content-integration/infra/runtime/.env}"
[[ -f "$ENV_FILE" ]] || { echo 'Set ACADEMY_ENV_FILE to the existing candidate private environment.' >&2; exit 1; }
exec docker compose --env-file "$ENV_FILE" -f compose.frontend-design.yaml "$@"
