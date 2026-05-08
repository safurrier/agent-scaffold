---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-agent-friendly-cli-polish

## Commands

```bash
scripts/hk-dev start demo --plan 'x' --profile python
```

Result: failed as intended with the new actionable error:

```text
Error: hk start does not use --profile. Profile flags are only for discovery commands such as `hk profile`, `hk checks`, and repo-scope `hk instructions`.
Try:
  hk profile resolve --target . --json
  hk checks --target . --json
  hk start --help
```

```bash
mise run fmt
```

Result: passed. Python formatting applied.

```bash
uv run pytest tests/unit/test_portable_workflow.py -q
```

Result: passed, 18 tests.

```bash
uv run ruff check src/harness_toolkit/kit/cli.py tests/unit/test_portable_workflow.py
```

Result: passed.

```bash
mise run check
```

Result: passed. Full gate completed with 831 tests passing.

```bash
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-cli-polish-docs
```

Result: passed. MkDocs emitted its existing Material/MkDocs compatibility warning and the existing `docs/AGENTS.md` nav notice; strict build completed successfully.

## Evidence

- `artifacts/agent-friendly-cli-audit.md`
