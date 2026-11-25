#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
python3 scripts/local-init.py
scripts/local-compose.sh up -d --build

python3 scripts/local-ready.py
