---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — agent-adoption-doc

## Commands

```bash
scripts/hk-dev instructions --help
scripts/hk-dev instructions
scripts/hk-dev instructions --scope repo --profile python
```

Result: passed. Confirmed the default user-level snippet, scoped repo snippet,
and updated help examples render as expected.

```bash
scripts/hk-dev instructions --json | python -m json.tool
scripts/hk-dev instructions --scope repo --profile python --json | python -m json.tool
scripts/hk-dev instructions --profile python --json | python -m json.tool
scripts/hk-dev instructions --scope user --profile python
```

Result: passed. Confirmed JSON output includes `scope=user` for default output,
`scope=repo` plus `profile=python` for repo output, legacy `--profile python`
compatibility implies repo scope, and explicit `--scope user --profile python`
exits 1 with a clear error.

```bash
uv run ruff check src/harness_toolkit/kit/cli.py tests/unit/test_portable_workflow.py
```

Result: passed.

```bash
uv run pytest tests/unit/test_portable_workflow.py -q
```

Result: passed, 15 tests.

```bash
uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-agent-adoption-docs
```

Result: passed. External MkDocs/Material compatibility warning only.

```bash
mise run fmt
mise run check
```

Result: formatting applied to `src/harness_toolkit/kit/cli.py` and `tests/unit/test_portable_workflow.py`; full check passed with 828 tests.

```bash
env -i PATH=/tmp/hk-no-path HOME=/tmp /bin/bash --noprofile --norc -c 'hk --version'
```

Result: exited 127 with `hk: command not found`, matching the new doc's missing-
`hk` branch. Transcript: `artifacts/missing-hk-dogfood.log`.

```bash
codex exec --sandbox read-only --skip-git-repo-check "Review the staged diff ..."
codex exec --sandbox read-only --skip-git-repo-check "Re-review the staged diff ..."
```

Result: initial review found the `--profile` compatibility blocker; final review
reported no blocking findings after the fix. Evidence: `artifacts/codex-review.md`
and `artifacts/codex-final-review.md`.
