#!/usr/bin/env bash
set -euo pipefail

SCENARIO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HARNESS_TOOLKIT_ROOT="${HARNESS_TOOLKIT_ROOT:-$(git -C "$SCENARIO_DIR/../../../../.." rev-parse --show-toplevel)}"
ROOT="${1:-/tmp/hk-dogfood-status-freshness-no-profile}"
rm -rf "$ROOT"
mkdir -p "$ROOT/bin" "$ROOT/repo" "$ROOT/reports"

cat > "$ROOT/bin/hk" <<EOF
#!/usr/bin/env bash
set +e
ROOT="$ROOT"
HARNESS_TOOLKIT_ROOT="$HARNESS_TOOLKIT_ROOT"
LOG="\${HK_DOGFOOD_LOG:-\$ROOT/hk-commands.jsonl}"
START_NS=\$(date +%s%N)
python3 - "\$LOG" "\$PWD" "\$START_NS" "\$@" <<'PY'
import json, sys, time
log, cwd, start, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"start","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"argv":argv})+"\n")
PY
"\$HARNESS_TOOLKIT_ROOT/scripts/hk-dev" "\$@"
STATUS=\$?
END_NS=\$(date +%s%N)
python3 - "\$LOG" "\$PWD" "\$START_NS" "\$END_NS" "\$STATUS" "\$@" <<'PY'
import json, sys, time
log, cwd, start, end, status, *argv = sys.argv[1:]
with open(log, "a") as f:
    f.write(json.dumps({"event":"end","at":time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),"cwd":cwd,"start_ns":start,"end_ns":end,"status":int(status),"argv":argv})+"\n")
PY
exit "\$STATUS"
EOF
chmod +x "$ROOT/bin/hk"

cd "$ROOT/repo"
git init -q
git checkout -q -b dogfood-status-freshness
mkdir -p src tests
cat > src/example.py <<'PY'
def normalize_name(value: str) -> str:
    return value.strip().lower()
PY
cat > tests/test_example.py <<'PY'
from src.example import normalize_name


def test_normalize_name():
    assert normalize_name(" Alex ") == "alex"
PY
cat > pyproject.toml <<'TOML'
[project]
name = "hk-dogfood-status-freshness"
version = "0.1.0"
requires-python = ">=3.12"

[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
TOML
git add .
git -c user.name=Dogfood -c user.email=dogfood@example.com commit --no-verify -q -m 'chore: seed dogfood repo'

echo "$ROOT"
