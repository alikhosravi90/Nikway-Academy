#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
command -v docker >/dev/null
command -v python3 >/dev/null
command -v gpg >/dev/null
docker compose version >/dev/null
python3 scripts/local-init.py
scripts/local-compose.sh config --quiet
scripts/local-compose.sh build
