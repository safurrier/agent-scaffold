---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run ruff format scripts/plan_contract.py .mise/tasks/plan-check .mise/tasks/spec-check .mise/tasks/evidence-check .mise/tasks/review-check .mise/tasks/sync-check tests/unit/test_plan_contract.py tests/contract/test_task_contract.py tests/e2e/test_rust.py tests/e2e/test_python.py tests/e2e/test_go.py` - passed
- `uv run ruff check scripts/plan_contract.py .mise/tasks/plan-check .mise/tasks/spec-check .mise/tasks/evidence-check .mise/tasks/review-check .mise/tasks/sync-check tests/unit/test_plan_contract.py tests/contract/test_task_contract.py tests/e2e/test_rust.py tests/e2e/test_python.py tests/e2e/test_go.py` - passed
- `uv run pytest tests/unit/test_plan_contract.py tests/contract/test_task_contract.py tests/contract/test_docs_contract.py -q` - passed, 239 tests
- `uv run pytest tests/e2e/test_rust.py::TestRustAppsHappyPath::test_sync_check_passes_after_setup -q` - passed, 1 test
- `uv run pytest tests/unit/test_golden_output.py::TestPythonSingleGolden::test_ci_workflow_content tests/unit/test_golden_output.py::TestGoSingleGolden::test_ci_workflow_content tests/unit/test_golden_output.py::TestRustSingleGolden::test_ci_workflow_content tests/e2e/test_python.py::TestPythonSingleHappyPath::test_ci_workflow_is_two_tier tests/e2e/test_go.py::TestGoSingleHappyPath::test_ci_workflow_is_two_tier tests/e2e/test_rust.py::TestRustSingleHappyPath::test_ci_workflow_is_two_tier -q` - passed, 6 tests
- `mise run sync-check -- --plan-dir .ai/plans/2026-04-12-120521-deterministic-slice-contract` - passed
- `mise run sync-check -- --plan-dir .ai/plans/2026-04-28-121022-slice-workflow-interface` - passed
- `mise run check` - passed, 649 tests
- `uv run pytest tests/unit/test_plan_contract.py tests/contract/test_task_contract.py tests/contract/test_docs_contract.py -q` - passed after review fixes, 242 tests
- `uv run pytest tests/e2e/test_rust.py::TestRustAppsHappyPath::test_sync_check_passes_after_setup -q` - passed after review fixes, 1 test
- `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral ...` - completed handoff review pass, findings summarized in `artifacts/review-summary.md`
- `mise run sync-check -- --changed-plans main` - passed, validated all three changed plans and printed non-plan branch paths
- final `mise run check` - passed, 652 tests

## Evidence

- `artifacts/validation-summary.md` summarizes focused validation for this slice.
- `artifacts/review-summary.md` summarizes the external handoff review and follow-up fixes.
