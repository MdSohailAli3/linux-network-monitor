#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
PYTHON="$ROOT/.venv/bin/python"
if [[ ! -x "$PYTHON" ]]; then
  echo "Virtual environment not found. Run ./scripts/setup.sh first." >&2
  exit 2
fi
exec "$PYTHON" -m netwatch monitor --config config/targets.example.json --interval "${INTERVAL:-10}" --log "${LOG_FILE:-data/monitoring.csv}"
