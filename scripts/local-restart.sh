#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
scripts/local-compose.sh restart postgres keycloak api frontend
python3 scripts/local-ready.py
