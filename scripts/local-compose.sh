#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[[ -f infra/runtime/.env ]] || { echo 'Run python3 scripts/local-init.py first.' >&2; exit 1; }
args=(-f compose.yaml)
[[ ! -f infra/runtime/compose.network.yaml ]] || args+=(-f infra/runtime/compose.network.yaml)
exec docker compose --env-file infra/runtime/.env "${args[@]}" "$@"
