#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PORT="${PORT:-47261}"
cd "$ROOT/output"
echo "Serving $ROOT/output on http://127.0.0.1:${PORT}/bardolino-trip-guide.html"
exec python3 -m http.server "$PORT" --bind 127.0.0.1
