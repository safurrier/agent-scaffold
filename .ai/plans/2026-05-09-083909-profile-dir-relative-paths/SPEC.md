---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — profile-dir-relative-paths

## Problem

Managed user config should not need to duplicate every standalone profile inside
`harness.toml`, and profile authors should not have to convert every module-local
path to a Git repo-root path by hand.

## Requirements

### MUST

- `harness.toml` must support loading standalone profile TOML files from a configured directory.
- Configured profile directories must resolve relative to `harness.toml` unless absolute.
- Explicit CLI `--profiles-dir` must continue to work for ad hoc catalogs and override earlier sources.
- Profile applicability matching must accept both repo-root-relative and target-relative path rules.
- Matched paths must still be reported as repo-root-relative paths.
- Negated patterns must remove matches even when include and exclude rules use different coordinate systems.

### SHOULD

- CLI help should frame `--profiles-dir` as ad hoc once configured directories exist.
- Missing configured profile directories should produce actionable repair guidance.
- `hk profile create` should be usable while bootstrapping a new configured profile directory.
- Docs and profile-authoring skill references should describe the new path-rule semantics.

## Constraints

- HK remains shell-first; profile changes may suggest or require named evidence, but HK must not run profile validation commands automatically.
- Preserve existing repo-root-relative profile behavior and gitignore-style pattern semantics.
