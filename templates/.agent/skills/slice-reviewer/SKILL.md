---
name: slice-reviewer
description: >
  Perform external-enough review for the active slice. Loads review rubrics from
  docs/reference/review-rubrics/ and writes a persistent REVIEW.md artifact.
allowed-tools: Read, Edit, Glob, Grep, Bash
---

Use this skill before handoff or push.

## Review standard

Same-agent self-grading does not count when `review_mode: external_required`.
Acceptable backends include:

- a harness-specific external review skill
- a same-harness subagent
- a manual external reviewer

## Workflow

1. Read the active plan's `META.yaml` and load the rubric files named there
2. Review the slice against those rubrics
3. Write or update `REVIEW.md` with:
   - review mode
   - backend used
   - reviewer identity
   - rubrics applied
   - findings
   - disposition
4. Update `META.yaml` `review_backend` to match the review artifact

## Rule

Persist the review inside the plan directory. Do not rely on temp-dir-only review artifacts.
