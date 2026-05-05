---
id: plan-validation
title: Validation Evidence
description: >
  Commands and evidence for this unit of work.
---

# Validation — hk-profile-config-mvp

## Focused local validation

- `uv run ruff format src/harness_toolkit/kit/profiles.py src/harness_toolkit/kit/cli.py tests/unit/test_portable_workflow.py`
  - Result: passed.
- `uv run ruff check src/harness_toolkit/kit/profiles.py src/harness_toolkit/kit/cli.py tests/unit/test_portable_workflow.py`
  - Result: passed.
- `uv run ty check src/harness_toolkit/kit/profiles.py src/harness_toolkit/kit/cli.py tests/unit/test_portable_workflow.py`
  - Result: passed.
- `uv run pytest tests/unit/test_portable_workflow.py::test_user_harness_config_resolves_inline_profile_and_checks tests/unit/test_portable_workflow.py::test_user_harness_config_uses_longest_target_prefix tests/unit/test_portable_workflow.py::test_workflow_profiles_and_checks_are_discoverable_without_execution tests/unit/test_portable_workflow.py::test_workflow_instructions_prints_minimal_agents_snippet -q`
  - Result: passed, 4 tests.

## Dogfood

- Temp clone dogfood: `artifacts/profile-config-dogfood-study.md`.
- Raw HK commands: `artifacts/dogfood-hk-commands.log`.
- Config used: `artifacts/dogfood-profile-config.md`.
- Worker reports and handoffs copied as reviewable top-level artifacts.

## Full validation

- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_harness_kit_2.py -q`
  - Result: passed, 65 tests.
- `mise run check`
  - Result: passed, 781 tests.

## Plan sync-check

- `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-154329-hk-profile-config-mvp`
  - Result: passed.
