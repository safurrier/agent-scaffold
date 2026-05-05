---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run ruff format src/harness_toolkit/kit/local.py src/harness_toolkit/kit/cli.py tests/unit/test_harness_kit_2.py`
  - Result: formatted changed Python files.
- `uv run ruff check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/cli.py tests/unit/test_harness_kit_2.py`
  - Result: passed.
- `uv run ty check src/harness_toolkit/kit/local.py src/harness_toolkit/kit/cli.py`
  - Result: passed.
- `uv run pytest tests/unit/test_harness_kit_2.py -q`
  - Result: passed, 42 tests.
- `uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_portable_workflow.py tests/e2e/test_harness_kit_rollout.py -q`
  - Result: passed, 65 tests after review dispatch hint updates.
- `mise run check`
  - Result: passed, 779 tests after Codex review command hint and post-review status guidance updates.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-05-105158-hk2-final-polish-dogfood`
  - Result: passed.

## Evidence

- Less-guided dogfood synthesis: `artifacts/less-guided-dogfood-v4-study.md`.
- Cross-run readout: `artifacts/hk2-dogfood-readout.md`.
- Review-default-on rerun: `artifacts/review-default-on-dogfood-v5-study.md`.
- Review dispatch hint smoke rerun: `artifacts/review-dispatch-hint-dogfood-v6-study.md`.
- Codex review tool smoke rerun: `artifacts/codex-review-tool-dogfood-v7-study.md`.
- Harness mechanism notes: `artifacts/review-harness-mechanisms.md`.
- Raw dogfood command logs and worker reports copied as reviewable top-level artifacts.
