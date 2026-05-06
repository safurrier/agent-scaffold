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

### 2026-05-05 — Chunk 2 shared repo identity/state resolution

```bash
uv run ruff check --fix src/harness_toolkit/kit/local.py src/harness_toolkit/kit/workflow.py src/harness_toolkit/kit/state/repo.py tests/unit/test_repo_state_resolution.py
uv run ruff format src/harness_toolkit/kit/state/repo.py src/harness_toolkit/kit/workflow.py src/harness_toolkit/kit/local.py tests/unit/test_repo_state_resolution.py
uv run ruff check src/harness_toolkit/kit/state/repo.py src/harness_toolkit/kit/workflow.py src/harness_toolkit/kit/local.py tests/unit/test_repo_state_resolution.py
uv run ty check src/harness_toolkit/kit/state/repo.py src/harness_toolkit/kit/workflow.py src/harness_toolkit/kit/local.py tests/unit/test_repo_state_resolution.py
uv run pytest tests/unit/test_repo_state_resolution.py tests/unit/test_harness_kit_2.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `46 passed`.

```bash
uv run pytest tests/unit/test_repo_state_resolution.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `75 passed, 2 xfailed`.

### 2026-05-05 — Chunk 3 HK2 lifecycle application Module

```bash
uv run ruff check --fix src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/cli.py
uv run ruff format src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/cli.py
uv run ty check src/harness_toolkit/kit/app/lifecycle.py src/harness_toolkit/kit/cli.py
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_harness_kit_2.py -q
```

Result: `46 passed, 2 xfailed`.

```bash
uv run pytest tests/unit/test_repo_state_resolution.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `75 passed, 2 xfailed`.

### 2026-05-05 — Chunk 4 typed ledger/event seam

```bash
uv run ruff check --fix src/harness_toolkit/kit/ledger src/harness_toolkit/kit/local.py tests/unit/test_hk2_ledger_events.py
uv run ruff format src/harness_toolkit/kit/ledger src/harness_toolkit/kit/local.py tests/unit/test_hk2_ledger_events.py
uv run ty check src/harness_toolkit/kit/ledger src/harness_toolkit/kit/local.py tests/unit/test_hk2_ledger_events.py
uv run pytest tests/unit/test_hk2_ledger_events.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_harness_kit_2.py -q
```

Result: `46 passed`.

```bash
uv run pytest tests/unit/test_hk2_ledger_events.py tests/unit/test_repo_state_resolution.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `77 passed, 2 xfailed`.

```bash
mise run check
```

Result: `791 passed, 2 xfailed`.

### 2026-05-05 — Chunk 5 readiness policy Module

```bash
uv run ruff check --fix src/harness_toolkit/kit/readiness src/harness_toolkit/kit/local.py tests/unit/test_hk2_readiness_policy.py
uv run ruff format src/harness_toolkit/kit/readiness src/harness_toolkit/kit/local.py tests/unit/test_hk2_readiness_policy.py
uv run ty check src/harness_toolkit/kit/readiness src/harness_toolkit/kit/local.py tests/unit/test_hk2_readiness_policy.py
uv run pytest tests/unit/test_hk2_readiness_policy.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py -q
```

Result: `48 passed`.

```bash
uv run pytest tests/unit/test_hk2_readiness_policy.py tests/unit/test_hk2_ledger_events.py tests/unit/test_repo_state_resolution.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `79 passed, 2 xfailed`.

### 2026-05-05 — Chunk 6 command capture Adapters

```bash
uv run ruff check --fix src/harness_toolkit/kit/capture src/harness_toolkit/kit/local.py tests/unit/test_hk2_capture_adapters.py
uv run ruff format src/harness_toolkit/kit/capture src/harness_toolkit/kit/local.py tests/unit/test_hk2_capture_adapters.py
uv run ty check src/harness_toolkit/kit/capture src/harness_toolkit/kit/local.py tests/unit/test_hk2_capture_adapters.py
uv run pytest tests/unit/test_hk2_capture_adapters.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py -q
```

Result: `8 passed, 2 xfailed`.

```bash
uv run pytest tests/unit/test_hk2_capture_adapters.py tests/unit/test_hk2_readiness_policy.py tests/unit/test_hk2_ledger_events.py tests/unit/test_repo_state_resolution.py tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
```

Result: `83 passed, 2 xfailed`.

## Planned final gates

```bash
uv run pytest tests/unit/test_hk2_lifecycle_parity.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_rendering_parity.py -q
uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q
mise run check
mise run sync-check -- --plan-dir .ai/plans/2026-05-05-194606-hk2-architecture-parity-refactor
```

## Evidence

- Add artifact paths to `artifacts/manifest.yaml` as rollout reports are produced.
