#!/usr/bin/env bash
set -euo pipefail

ROOT="${1:-/tmp/hk-dogfood-status-freshness-profile-label-authority}"
OUT="$ROOT/reports/collection.md"

{
  echo "# Dogfood collection: status-freshness-profile-label-authority"
  echo
  echo "## HK commands"
  if [[ -f "$ROOT/hk-commands.jsonl" ]]; then
    python3 - "$ROOT/hk-commands.jsonl" <<'PY'
import json, sys
with open(sys.argv[1]) as f:
    for line in f:
        event = json.loads(line)
        if event.get("event") == "end":
            print(f"- `hk {' '.join(event.get('argv', []))}` -> {event.get('status')}")
PY
  else
    echo "missing hk-commands.jsonl"
  fi
  echo
  echo "## Git status"
  git -C "$ROOT/repo" status --short || true
  echo
  echo "## Git diff stat"
  git -C "$ROOT/repo" diff --stat || true
  echo
  echo "## Worker report"
  if [[ -f "$ROOT/reports/worker-report.md" ]]; then
    cat "$ROOT/reports/worker-report.md"
  else
    echo "missing worker report"
  fi
} > "$OUT"

echo "$OUT"
