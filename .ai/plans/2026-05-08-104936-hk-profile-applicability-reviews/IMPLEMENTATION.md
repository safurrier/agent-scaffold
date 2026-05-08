---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about the implementation approach and changed files.
---

# Implementation — hk-profile-applicability-reviews

## Implemented changes

- Extended profile dataclasses and TOML parsing with optional `applies_when` and `required_when` fields on checks and reviews.
- Added unique shell-safe validation for check/review names because these names are durable identifiers used by `--check`, `--review`, readiness, and dangerous-skip labels.
- Switched profile applicability matching to `pathspec` gitignore-style rules:
  - patterns match repo-root-relative changed paths;
  - `*.md` matches Markdown files at any depth;
  - `/*.md` anchors Markdown files to the repo root;
  - leading dots are preserved, so `github/**` does not match `.github/**`;
  - later negated patterns can remove matches.
- Added changed-path collection from the active work-start SHA plus current worktree/untracked changes.
- Extended `hk checks --changed` to render changed paths, suggested checks, suggested reviews, matched paths, required status, lifecycle enforcement status, and copyable follow-up commands.
- Added `hk validate --check NAME` and persisted `check_name` on evidence records.
- Added `hk review add --review NAME` and persisted `review_name` on review events/results.
- Added `hk review prompt REVIEW_NAME`, which resolves the named profile review, loads `prompt_file`, and renders it with live work context.
- Removed `prompt_file_text` from normal `hk checks --json` / `hk profile show --json` output. Prompt file content is rendered by named review prompts instead.
- Readiness now enforces `required_when` matches for the target's resolved user-config profile and accepts matching dangerous skips by `--label`.
- Summary/handoff rendering now labels validation evidence and reviews with their profile check/review names when present.
- Updated public docs and profile-authoring skill references with applicability and named review examples.

## Important boundary

`--profile` and `--profiles-dir` remain discovery-only. If an agent inspects a custom profile with those flags, `hk checks --changed` may show items as required by the inspected profile, but `enforced=false` unless that profile is also bound as the target's resolved user-config profile. Lifecycle commands still do not accept profile flags.
