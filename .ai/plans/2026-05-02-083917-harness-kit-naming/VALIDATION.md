---
id: plan-validation
title: Harness Kit Naming Validation Log
description: >
  Validation notes for the naming implementation slice.
---

# Validation

## Commands

- `mise run plan -- harness-kit-naming`
  - Result: created `.ai/plans/2026-05-02-083917-harness-kit-naming`.
- `mise run plan-check -- .ai/plans/2026-05-02-083917-harness-kit-naming`
  - Result: failed; `plan-check` expects `--plan-dir`, not a positional plan path.
- `mise run plan-check -- --plan-dir .ai/plans/2026-05-02-083917-harness-kit-naming`
  - Result: passed; plan contract ready.
- `uv run pytest tests/unit/test_cli.py tests/unit/test_portable_workflow.py tests/contract/test_task_contract.py -q`
  - Result: passed during rename implementation; 176 tests.
- `uv run python -c 'import harness_toolkit; ... import agent_scaffold ...'`
  - Result: `harness_toolkit` imported and `agent_scaffold` was absent.
- `uv run hk instructions --profile python --json`
  - Result: passed and generated snippets using `hk`.
- `uv run harness-scaffold --version && uv run hk --version && uv run harness-kit --version`
  - Result: all preferred commands returned `0.1.0`.
- `uv run agent-scaffold --help` and `uv run agent-workflow --help`
  - Result: both returned non-zero, confirming legacy console scripts are not registered in the renamed package.
- `uv run pytest -m "contract or unit" -q`
  - Result: passed after source/package rename; 431 tests.

## Evidence

- `artifacts/naming-brief.md` records the naming summary and final product boundary.
- `docs/decisions/0007-harness-toolkit-naming.md` records the durable ADR.
- `pyproject.toml` declares only `harness-scaffold`, `harness-kit`, and `hk` console scripts.

- `mise run check`
  - Result: passed after final formatting; 703 tests.
- `mise run check`
  - Result: passed after package subtree split and `ProfileCatalog` refactor; 703 tests.
- `mise run check`
  - Result: passed after addressing Codex review findings and formatting; 717 tests.
- `uv run pytest tests/unit/test_portable_workflow.py::test_workflow_overlay_attach_works_with_linked_worktree -q`
  - Result: passed after sanitizing nested git subprocess environment for pre-commit hook compatibility.

- `mise run sync-check -- --plan-dir .ai/plans/2026-05-02-083917-harness-kit-naming`
  - Result: passed after making the naming plan contract complete.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-docs-workflow/scripts/docs_verify.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: passed during context-improve pass.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-ai-context-engineering-files/scripts/validate_frontmatter.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: initially failed on frontmatter index mismatches; passed after updating docs indexes.
- `python3 /Users/alex.furrier/.pi/agent/skills/alex-ai-ai-context-engineering-files/scripts/verify_references.py /Users/alex.furrier/git_repositories/agent-scaffold`
  - Result: initially failed on a placeholder-style module path in `docs/portable-workflow.md`; passed after wording the example as prose rather than a file reference.
- `uv run pytest tests/contract/test_task_contract.py tests/unit/test_portable_workflow.py -q`
  - Result: passed after context-improve doc fixes; 166 tests.
- `uv run ruff check src/harness_toolkit tests && uv run ty check src/harness_toolkit tests/unit/test_portable_workflow.py tests/unit/test_cli.py`
  - Result: passed after package subtree split and `ProfileCatalog` refactor.
- `uv run pytest tests/unit/test_cli.py tests/unit/test_portable_workflow.py tests/unit/test_templates_jinja.py tests/unit/test_golden_output.py tests/contract/test_task_contract.py -q`
  - Result: passed after package subtree split and `ProfileCatalog` refactor; 326 tests.
- `uv run ruff check src/harness_toolkit tests/unit/test_init_project.py tests/unit/test_golden_output.py tests/unit/test_portable_workflow.py && uv run ty check src/harness_toolkit tests/unit/test_portable_workflow.py tests/unit/test_cli.py && uv run pytest tests/unit/test_init_project.py tests/unit/test_golden_output.py tests/unit/test_portable_workflow.py tests/unit/test_cli.py tests/contract/test_task_contract.py -q`
  - Result: passed after addressing Codex review findings; 345 tests.
- `uv run ruff check src/harness_toolkit/kit/workflow.py tests/unit/test_portable_workflow.py && uv run ty check src/harness_toolkit/kit/workflow.py tests/unit/test_portable_workflow.py && uv run pytest tests/unit/test_portable_workflow.py::test_workflow_status_reports_missing_target_without_traceback tests/unit/test_portable_workflow.py::test_workflow_status_reports_file_target_without_traceback -q`
  - Result: passed after extending target validation to reject file paths before invoking git subprocesses.
- `uv run ruff check tests/e2e/test_harness_kit_rollout.py && uv run ty check tests/e2e/test_harness_kit_rollout.py && uv run pytest tests/e2e/test_harness_kit_rollout.py -q`
  - Result: passed after adding synthetic external/overlay rollout parity e2e coverage; 2 tests.
- `mise run check`
  - Result: passed after adding rollout parity e2e coverage; 720 tests.
- `mise run sync-check -- --plan-dir .ai/plans/2026-05-02-083917-harness-kit-naming && mise run sync-check`
  - Result: both passed after context-improve doc fixes.
