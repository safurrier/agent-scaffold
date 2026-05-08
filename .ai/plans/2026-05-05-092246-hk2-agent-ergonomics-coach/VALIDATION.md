---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run pytest tests/unit/test_harness_kit_2.py::test_cli_start_plan_and_context_seed_lifecycle_notes tests/unit/test_harness_kit_2.py::test_cli_plan_without_active_work_points_to_start_or_legacy_plan tests/unit/test_harness_kit_2.py::test_dangerously_skip_sync_satisfies_readiness_and_handoff tests/unit/test_harness_kit_2.py::test_status_coaches_next_actions -q`
  - Result: passed, 4 tests.
- `uv run ruff check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/cli.py tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py`
  - Result: passed after import formatting fix.
- `uv run ty check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/cli.py`
  - Result: passed.
- `uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q`
  - Result: passed, 60 tests after review fixes.
- `mise run check`
  - Result: passed, 774 tests after final review fixes.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-092246-hk2-agent-ergonomics-coach`
  - Result: passed.

## Evidence

- Targeted PR-sized rollout artifacts copied as top-level reviewable files in `artifacts/`.
- Rollout synthesis: `artifacts/pr-sized-dogfood-v3-study.md`.
