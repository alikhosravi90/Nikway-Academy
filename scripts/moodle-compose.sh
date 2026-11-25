#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
args=(-f infra/moodle/compose.yaml)
[[ ! -f infra/moodle/runtime/compose.auth.yaml ]] || args+=(-f infra/moodle/runtime/compose.auth.yaml)
exec docker compose "${args[@]}" "$@"
