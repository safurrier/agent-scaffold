---
id: plan-review
title: Review Evidence
description: >
  External review notes for this slice.
---

# REVIEW — hk-session-artifacts-skill

## Review Context

- Mode: external
- Backend: pi-subagent
- Reviewer: reviewer builtin, fresh context

## Rubrics

- core-quality
- skill-usability
- transcript-safety

## Findings

- Initial reviewer blocker: plan evidence files were still placeholders when review ran, so dogfood evidence was not yet inspectable.
- Reviewer confirmed the skill clearly prefers exact transcript paths over latest-session heuristics.
- Reviewer confirmed the helper is discovery-only and does not attach artifacts.
- Reviewer confirmed candidate results carry confidence and cautionary reasons.
- Reviewer confirmed the reference document reinforces safe source-specific behavior.
- Suggestions:
  - make the generic attach example source-neutral instead of Pi-specific;
  - add a count/sanity check to the Pi recipe before `head -n 1` style selection;
  - mention newest-first helper output is only an inspection aid;
  - record validation for the helper.

## Disposition

- Filled plan validation/review/dogfood artifacts after the initial review placeholder blocker.
- Changed the generic attach example to use `$ARTIFACT_KIND` and `$LABEL`, plus a common-kind mapping.
- Added an explicit newest-first inspection warning.
- Added a count check to the Pi explicit-session-dir recipe.
- Recorded helper smoke validation and dogfood evidence in `artifacts/dogfood/`.
