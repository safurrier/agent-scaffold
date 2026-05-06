---
id: plan-validation
title: Validation Log
description: >
  Validation evidence for the HK2 architecture parity refactor.
---

# Validation

## Commands

### 2026-05-05 — Chunk 1 parity baseline

```bash
uv run ruff format tests/support/hk2_repo.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py
uv run ruff check tests/support/hk2_repo.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py
uv run ty check tests/support/hk2_repo.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py -q
```

Result: `6 passed, 2 xfailed`. The two xfails are the planned Chunk 8 legacy-removal assertions.

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `73 passed, 2 xfailed`.

## Planned final gates

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py -q
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
mise run check
mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor
```

## Evidence

- Add artifact paths to `artifacts/manifest.yaml` as rollout reports are produced.
