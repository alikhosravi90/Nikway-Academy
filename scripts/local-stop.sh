#!/usr/bin/env bash
set -euo pipefail
exec "$(dirname "$0")/local-compose.sh" stop
