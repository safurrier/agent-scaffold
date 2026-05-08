---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-cli-help-idempotency-polish

## Commands

```bash
scripts/hk-dev --help >/tmp/hk-root-help-polish.txt
scripts/hk-dev start --help >/tmp/hk-start-help-polish.txt
python3 - <<'PY'
from pathlib import Path
root=Path('/tmp/hk-root-help-polish.txt').read_text()
start=Path('/tmp/hk-start-help-polish.txt').read_text()
assert '1. Primary lifecycle' in root
assert '4. Advanced/local state' in root
assert root.index('1. Primary lifecycle') < root.index('4. Advanced/local state')
assert 'hk start my-slice' in start
assert 'resumes it instead of creating duplicate retry' in start
print('help smoke passed')
PY
```

Result: passed. Confirms grouped root help and retry guidance in `hk start --help`.

```bash
# Generate all changed command helps and check for wrapped example continuations.
# Full command list omitted here for brevity; output was written to /tmp/hk-help-all.txt.
python3 - <<'PY'
from pathlib import Path
bad=[]
for i,line in enumerate(Path('/tmp/hk-help-all.txt').read_text().splitlines(),1):
    stripped=line.strip()
    if line.startswith(' ') and stripped.startswith(('--', 'tests/', './', '/')):
        bad.append((i,stripped))
assert not bad, bad[:20]
print('help example wrapping smoke passed')
PY
```

Result: passed. Confirms the shortened examples do not emit obvious wrapped command continuation lines in captured help output.

```bash
uv run ruff check src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/local.py tests/unit/test_portable_workflow.py
```

Result: passed.

```bash
uv run pytest tests/unit/test_portable_workflow.py -q
```

Result: passed, 21 tests.

```bash
mise run check
```

Result: passed. Full gate completed with 834 tests passing.

```bash
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-help-idempotency-docs
```

Result: passed. MkDocs emitted its existing Material/MkDocs compatibility warning and existing `docs/AGENTS.md` nav notice; strict build completed successfully.
