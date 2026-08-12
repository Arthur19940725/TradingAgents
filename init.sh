#!/usr/bin/env bash
set -euo pipefail

printf '%s\n' '=== TradingAgents verification ==='

if command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  printf '%s\n' 'Python was not found. Install Python 3.10-3.13 and the dev dependencies.' >&2
  exit 1
fi

"$PYTHON" -c 'import sys; assert sys.version_info >= (3, 10), f"TradingAgents requires Python 3.10 or newer; found {sys.version.split()[0]}"'
"$PYTHON" -m pytest -q
"$PYTHON" -m ruff check .

printf '%s\n' '=== Verification complete ==='
printf '%s\n' 'Next steps: read feature_list.json and progress.md, then work on one ready feature.'
