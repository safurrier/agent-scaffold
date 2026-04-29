---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `rg --files templates/.agent/skills/slice-workflow/cli/src -g '*.py' | xargs uv run python -m py_compile`
- `uv run pytest tests/unit/test_plan_contract.py -q`
- `uv run pytest tests/unit/test_plan_contract.py tests/contract/test_docs_contract.py tests/contract/test_task_contract.py -q`
- `uv run pytest tests/contract/test_task_contract.py tests/unit/test_plan_contract.py tests/unit/test_slice_workflow.py -q`
- `mise run slice-status -- --json`
- `uv run pytest tests/contract/test_task_contract.py tests/unit/test_plan_contract.py tests/unit/test_slice_workflow.py tests/contract/test_docs_contract.py -q`
- `mise run sync-check`
- `mise run check`
- `mise run verify`
- `uv run pytest -m "not slow"` (run by codex handoff review)
- `mise run sync-check -- --changed-plans HEAD~1...HEAD`
- `uv run pytest tests/unit/test_plan_contract.py::test_strip_plan_local_changes_uses_explicit_repo_root -q`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -q`
- `uv run pytest tests/unit/test_slice_workflow_cli.py tests/unit/test_plan_contract.py tests/unit/test_slice_workflow.py tests/contract/test_task_contract.py tests/contract/test_docs_contract.py -q`
- `mise run fmt`
- `mise run lint`
- `mise run typecheck`
- `mise run check`
- `codex exec --dangerously-bypass-approvals-and-sandbox --ephemeral -o .ai/plans/2026-04-29-154802-followup-contract-stack-rubric/artifacts/handoff-review/review.md ...`

## Evidence

- `artifacts/validation-summary.md`
- `artifacts/review-summary.md`
