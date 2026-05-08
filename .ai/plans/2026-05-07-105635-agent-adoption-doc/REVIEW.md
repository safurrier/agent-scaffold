---
id: plan-review
title: Review Evidence
description: >
  Review notes for this slice.
---

# REVIEW — agent-adoption-doc

## Review Context

- Mode: external
- Reviewer: Codex CLI fresh-context review
- Backend: codex exec
- Scope: docs and `hk instructions` output changes

## Rubrics

- core-quality
- docs-clarity

## Findings

- Blocking finding: after changing the default `hk instructions` scope to user-level output, `hk instructions --profile python --json` would have silently ignored `--profile` unless callers also passed `--scope repo`.
- Non-blocking finding: the user-level snippet correctly starts with `hk profile resolve --target . --json` and does not force `--profile generic`.
- Final finding after fix: Codex reported no blocking findings.

## Disposition

- Fixed compatibility by making `--profile` or `--profiles-dir` imply `--scope repo` when `--scope` is omitted.
- Added a regression test for `hk instructions --profile python --json`.
- Added a guard that rejects explicit `--scope user --profile python`.
- Final Codex rereview reported no blocking findings and confirmed the user-level snippet does not force generic profiles.

## Evidence

- `artifacts/codex-review.md`
- `artifacts/codex-final-review.md`
