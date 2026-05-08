---
id: plan-validation
title: Validation
description: >
  Commands run and evidence collected for this unit of work.
---

# Validation — hk-profile-applicability-reviews

## Commands

- `uv run pytest tests/unit/test_portable_workflow.py -q`
  - Result: passed, 24 tests.
- `uv run pytest tests/unit/test_harness_kit_2.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_portable_workflow.py tests/e2e/test_hk2_cli_parity.py::test_profile_config_cli_parity -q`
  - Result: passed, 102 tests.
- `uv run ruff check src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/local.py src/harness_toolkit/kit/profiles tests/unit/test_portable_workflow.py src/harness_toolkit/kit/readiness/policy.py src/harness_toolkit/kit/rendering/review_prompt.py src/harness_toolkit/kit/ledger/models.py src/harness_toolkit/kit/ledger/store.py`
  - Result: passed.
- `mise run check`
  - Result: passed, 840 tests.
- `uv run mkdocs build --strict --site-dir /tmp/harness-toolkit-profile-applicability-docs`
  - Result: passed with existing MkDocs Material warning and existing `docs/AGENTS.md` nav notice.

## Dogfood

Synthetic repo: `/tmp/hk-profile-applicability-dogfood/repo`.

Covered:

- user config profile with `applies_when` / `required_when` for a CLI check and agent-friendly CLI review;
- `hk checks --changed --json` suggesting required check/review for `src/demo/cli.py`;
- `hk review prompt agent-friendly-cli-review` rendering prompt-file content plus live changed paths;
- `hk ready --json` failing before named check/review evidence;
- `hk validate --check cli-unit-tests ...` and `hk review add --review agent-friendly-cli-review ...` satisfying required items;
- final `hk ready --json` passing and `hk summary` showing named check/review labels.

Artifact: `artifacts/profile-applicability-dogfood.log`.
