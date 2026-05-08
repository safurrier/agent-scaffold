---
id: plan-review
title: Review Log
description: >
  External-enough review record for this slice. Capture the backend, rubrics,
  findings, and final disposition before handoff.
---

# Review — hk-profile-applicability-reviews

## Review Context

- Mode: external
- Context: fresh-context subagents
- Backend: Pi subagent tool
- Reviewer: Pi fresh-context subagents (`reviewer` and `agent-friendly-cli`)
- Reviewers:
  - `reviewer`
  - `agent-friendly-cli`

## Rubrics

- core-quality
- readiness-policy
- shell-first-boundary
- agent-friendly-cli

## Findings

Initial blockers were found and fixed:

- Segment glob matching was too broad.
- Discovery-only custom profile suggestions could look lifecycle-enforced.
- Required suggestion output did not show `--check` / `--review` follow-ups.
- Named review prompt hardcoded the backend in its copyable record command.

Non-blocking findings fixed opportunistically:

- Profile check/review names are now unique shell-safe identifiers.
- `prompt_file_text` no longer appears in normal checks/profile JSON.
- Agent adoption docs now show generic vs named review flows as alternatives.

Details: `artifacts/review-summary.md`.

## Disposition

- Accepted after fixes.
- No known blocking review findings remain.
