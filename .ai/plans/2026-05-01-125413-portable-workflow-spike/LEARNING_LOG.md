---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-01 12:54

Started portable workflow spike. Initial direction: keep agent-scaffold's slice workflow contract, but add an attachable local/external state mode for shared repos where committing `.ai`, `.agent`, `.mise`, or `.gitignore` changes is not appropriate.

## 2026-05-01 12:59

Implemented a first pass as `agent-scaffold workflow` rather than changing generated-repo `.mise/tasks`. External mode stores state under a configurable state root keyed by repo identity; overlay mode stores state under `.ai-local/agent-scaffold/` and writes only `.git/info/exclude` in the target repo. The manual smoke against a cloned `dread` repo kept `git status --porcelain` empty in both modes.

## 2026-05-01 13:01

Kept `workflow sync-check` intentionally local-only for the spike. It validates required plan files, meaningful TODO/DECISIONS content, validation commands, and review content, but does not require artifact paths to be tracked in git. That differs from committed-plan `sync-check`, where tracked evidence is the point.

## 2026-05-01 13:20

Applied user feedback: moved the portable agent-facing command surface to Cyclopts as `agent-workflow`, loaded the agent-friendly CLI design skill, added `instructions` as the minimal `AGENTS.md` adoption path, and added help examples/JSON/dry-run coverage. Kept the existing `agent-scaffold init` Click CLI unchanged for now because the feedback targets the new portable workflow surface.

## 2026-05-01 13:42

Dogfooded the `.ai` plan by writing a real SPEC/IMPLEMENTATION for the profile DSL. Implemented profiles as read-only structured task-contract docs, not a runner: `agent-workflow checks --profile python --json` exposes named loops and command templates, but the agent still runs the command directly and records the result in `VALIDATION.md`.

## 2026-05-01 13:49

Removed private/company-specific profile examples from the public repo. The built-in profiles are now public stack-oriented examples: `generic`, `python`, `go`, and `rust`.

## 2026-05-01 14:08

TDD-refactored the remaining Click CLI surface to Cyclopts. Rewrote CLI unit tests to exercise installed console scripts through `uv run` instead of Click's `CliRunner`, removed source/test Click imports, and smoke-tested non-interactive `agent-scaffold init` in a copied scaffold. Also removed `--module`; target subdirectories now define state scope (`packages/api` -> `packages-api`).
