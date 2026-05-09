---
id: plan-validation
title: Validation Log
description: >
  How changes were verified. Append entries after testing.
  Link to artifacts — don't store them here. See _example/ for a reference.
---

# Validation

## Commands

- `uv run pytest tests/unit/test_portable_workflow.py::test_user_harness_config_loads_profiles_dir tests/unit/test_portable_workflow.py::test_changed_path_rules_accept_target_relative_patterns tests/unit/test_portable_workflow.py::test_profile_applicability_uses_gitignore_style_patterns tests/unit/test_portable_workflow.py::test_profile_applicability_supports_gitignore_negation -q` — pass, 4 tests.
- `mise run check` — initial format-check failure for `tests/unit/test_portable_workflow.py`; fixed with `uv run ruff format`.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_profile_package_boundaries.py -q` — pass, 30 tests before review fixes.
- `uv run pytest tests/unit/test_portable_workflow.py::test_profile_applicability_negation_can_mix_root_and_target_relative_paths tests/unit/test_portable_workflow.py::test_user_harness_config_loads_profiles_dir tests/unit/test_portable_workflow.py::test_configured_profiles_dir_errors_are_actionable_but_create_still_works tests/unit/test_portable_workflow.py::test_configured_profiles_dirs_and_cli_profiles_dir_precedence tests/unit/test_portable_workflow.py::test_changed_path_rules_accept_target_relative_patterns -q` — pass, 5 tests after review fixes.
- `uv run ruff format src/harness_toolkit/kit/cli.py src/harness_toolkit/kit/profiles tests/unit/test_portable_workflow.py` — formatted two files.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_profile_package_boundaries.py -q` — pass, 33 tests after review fixes.
- `hk validate --target . --check fast-gate --why "Full repository quality gate after fixing review blockers for mixed-coordinate negation and agent-facing profile-dir help/errors." -- mise run check` — pass, 847 tests.
- `hk validate --target . --check focused-contract-tests --why "Contract marker suite covers docs/spec/task-contract behavior touched by profile catalog ergonomics docs." -- uv run pytest -m contract` — pass, 264 tests.
- `hk validate --target . --check hk-dev-dogfood --why "Dogfoods this checkout's hk CLI for profile resolution/check discovery after profile-dir help and matching changes." -- bash -lc '...'` — pass.
- `hk validate --target . --check handoff-sync-check --why "Plan artifact contract passes for this slice after using bullet-based findings/disposition." -- mise run sync-check -- --plan-dir .ai/plans/2026-05-09-083909-profile-dir-relative-paths` — pass.
- `hk validate --target . --check generated-stack-smoke --why "Template change is limited to the generated harness-kit-profile-authoring skill; validate the skill package structure instead of running full stack smoke." -- python3 .../quick_validate.py templates/.agent/skills/harness-kit-profile-authoring` — pass.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_profile_package_boundaries.py -q` — pass, 33 tests after final CLI help/error updates.
- `hk validate --target . --check fast-gate --why "Final full repository quality gate after plan metadata and review-driven fixes." -- mise run check` — pass, 847 tests.
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_profile_package_boundaries.py -q` — pass, 33 tests after addressing Codex review suggestions.
- `hk validate --target . --check fast-gate --why "Full quality gate after addressing Codex review docs/help/hint findings." -- mise run check` — pass, 847 tests.

## Evidence

- HK evidence: `ev_20260509_090828_400197` (`mise run check`, pass after review fixes).
- HK evidence: `ev_20260509_092405_697875` (`uv run pytest -m contract`, pass).
- HK evidence: `ev_20260509_092437_009108` (`scripts/hk-dev` dogfood, pass).
- HK evidence: `ev_20260509_092708_314894` (`mise run sync-check -- --plan-dir ...`, pass).
- HK evidence: `ev_20260509_092723_720074` (profile-authoring skill validation, pass).
- HK evidence: `ev_20260509_092819_344648` (final `mise run check`, pass).
- HK evidence: `ev_20260509_130345_144543` (`mise run check` after Codex review fixes, pass).
