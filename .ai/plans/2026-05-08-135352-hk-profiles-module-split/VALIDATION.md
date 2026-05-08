---
id: plan-validation
title: Validation
description: >
  Commands run and evidence collected for this unit of work.
---

# Validation — hk-profiles-module-split

## Commands

- `uv run ruff format src/harness_toolkit/kit/profiles`
  - Result: formatted changed profile modules.
- `uv run ruff check src/harness_toolkit/kit/profiles tests/unit/test_portable_workflow.py tests/e2e/test_hk2_cli_parity.py`
  - Result: passed.
- `uv run pytest tests/unit/test_portable_workflow.py tests/e2e/test_hk2_cli_parity.py::test_profile_config_cli_parity -q`
  - Initial result: failed because `ProfileError` was no longer re-exported from `harness_toolkit.kit.profiles`.
  - Fix: re-export model types and compatibility helpers from `profiles/__init__.py`.
  - Final result: passed, 27 tests.
- `uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_portable_workflow.py tests/e2e/test_hk2_cli_parity.py::test_profile_config_cli_parity tests/unit/test_profile_package_boundaries.py -q`
  - Result: passed, 105 tests.
- `mise run check`
  - Result: passed, 842 tests.
