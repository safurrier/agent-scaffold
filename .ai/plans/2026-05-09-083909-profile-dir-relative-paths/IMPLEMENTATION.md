---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
  Optional — create only when the approach isn't obvious.
---

# Implementation — profile-dir-relative-paths

## Approach

Make profile catalog ergonomics match how agents naturally author profiles:

1. Let `harness.toml` point at standalone profile files so user config can keep target bindings compact.
2. Treat changed-path applicability rules as accepting both Git repo-root paths and paths relative to the selected `--target`, while continuing to report matched paths in repo-root-relative form.
3. Preserve shell-first behavior: HK still suggests and enforces named evidence/review records; it does not execute profile checks.

## Steps

1. Extend `HarnessConfig` with normalized `profiles_dirs`.
2. Parse `profiles_dir = "..."` and `profiles_dirs = ["..."]` relative to `harness.toml`.
3. Load catalogs in this order: built-ins, inline config profiles, config-declared profile dirs, explicit CLI `--profiles-dir`.
4. Extend applicability matching to compare each changed path with a target-relative alias when the target is under the git root.
5. Add focused CLI tests for directory-backed profiles and target-relative changed-path rules.
6. Update README, SPEC, portable workflow docs, and profile-authoring skill references.
7. Validate with focused tests, full check, sync-check, and fresh-context review.
