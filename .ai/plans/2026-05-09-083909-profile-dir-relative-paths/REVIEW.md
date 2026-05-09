---
id: plan-review
title: Review Log
description: >
  External-enough review record for this slice. Capture the backend, rubrics,
  findings, and final disposition before handoff.
---

# Review — profile-dir-relative-paths

## Review Context

- Mode: external
- Backend: pi-subagents
- Reviewer: `reviewer` and `agent-friendly-cli` fresh-context subagents

## Rubrics

- core-quality
- agent-facing-cli

## Findings

- Initial `reviewer` blocker: `_matched_paths()` used `any(spec.match_file(candidate))` across repo-root and target-relative candidates, so negation in one coordinate system could be bypassed by a positive match in the other. Fixed by applying patterns sequentially across both candidates and adding mixed-coordinate negation regression tests.
- Initial `agent-friendly-cli` blocker: CLI help still over-taught `--profiles-dir`, and missing configured profile dirs could block `hk profile create`. Fixed by describing configured dirs as automatic, framing `--profiles-dir` as ad hoc, improving missing-dir errors, and making `profile create` avoid catalog loading.
- Re-review finding: both reviewers accepted the updated diff with no blockers.

## Disposition

- Accepted. Fresh-context reviewers confirmed config dir loading, target-relative path matching, help/errors, tests, and docs are aligned.
