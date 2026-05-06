---
id: plan-validation
title: Validation Evidence
description: >
  Commands run and what they proved.
---

# VALIDATION — hk-sync-exclude-literal-paths

## Focused code/test gates

```bash
uv run ruff check src/harness_toolkit/kit/local.py tests/unit/test_harness_kit_2.py README.md SPEC.md docs/portable-workflow.md
```

Result: passed.

```bash
uv run ruff format src/harness_toolkit/kit/local.py tests/unit/test_harness_kit_2.py
```

Result: passed; no changes on first run.

```bash
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result before reviewer-suggested coverage additions: `66 passed`.

```bash
uv run ruff check src/harness_toolkit/kit/local.py tests/unit/test_harness_kit_2.py README.md SPEC.md docs/portable-workflow.md docs/harness-kit-lifecycle-design.md
uv run ruff format src/harness_toolkit/kit/local.py tests/unit/test_harness_kit_2.py
uv run ty check src/harness_toolkit/kit/local.py tests/unit/test_harness_kit_2.py
uv run pytest tests/unit/test_harness_kit_2.py -q
```

Result after adding absolute/staged coverage and design-doc alignment: `68 passed`.

## Full gate

```bash
mise run check
```

Result: passed; `818 passed`.

## HK dogfood

Dogfood artifacts are under `artifacts/dogfood/`.

Key command sequence:

```bash
hk start sync-exclude-literal --plan 'Verify hk sync --exclude accepts explicit untracked literal local paths without a hardcoded allowlist.'
hk validate --why 'A direct git status proves the dogfood repo has one tracked edit plus three untracked local paths to exclude.' -- git status --short
hk sync --exclude dist --exclude .cache/tool --exclude src/scratch.py --reason 'Dogfood local-only generated output, tool cache, and scratch file intentionally excluded.'
hk sync --check
hk ready
hk handoff --write /tmp/.../handoff.md
```

Result:

- `artifacts/dogfood/sync-check.json`: `synced: true`, `message: synced`.
- `artifacts/dogfood/ready.json`: `ready: true`, `status: ready`.
- `artifacts/dogfood/handoff.md`: includes `## Sync exclusions` for `dist`, `.cache/tool`, and `src/scratch.py`.
- `artifacts/dogfood/evidence.jsonl`: captured exact validation command evidence.
- `artifacts/dogfood/hk-commands.jsonl`: complete HK invocation log.
