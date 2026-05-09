---
id: plan-decisions
title: Decision Notes
description: >
  Slice-local decision staging area. Capture what changed, why, and where the
  durable record lives before running sync-check.
---

# Decisions — profile-dir-relative-paths

## What Changed

- User config now supports `profiles_dir = "profiles"` and `profiles_dirs = ["profiles", "team-profiles"]`.
- Config-declared profile dirs are loaded automatically by default `hk profile` / `hk checks` commands.
- Catalog precedence is deterministic: built-ins → inline config profiles → config-declared profile dirs → explicit CLI `--profiles-dir`.
- Changed-path applicability rules now match both repo-root-relative changed paths and target-relative aliases for scoped targets.

## Why

- Keeping every profile embedded in `harness.toml` duplicates standalone profile files and makes managed user config noisy.
- Agents naturally write module profile patterns relative to the module target, e.g. `cap/**` for `--target discord_cap`; HK should accept that without losing explicit repo-root support.
- Matched paths still render repo-root-relative so evidence and review prompts remain aligned with Git output.

## Where Reflected

- `src/harness_toolkit/kit/profiles/config.py`
- `src/harness_toolkit/kit/profiles/loading.py`
- `src/harness_toolkit/kit/profiles/applicability.py`
- `tests/unit/test_portable_workflow.py`
- `README.md`
- `SPEC.md`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `templates/.agent/skills/harness-kit-profile-authoring/`

## Promotion

- Reflected in README/SPEC/docs and covered by focused tests.
