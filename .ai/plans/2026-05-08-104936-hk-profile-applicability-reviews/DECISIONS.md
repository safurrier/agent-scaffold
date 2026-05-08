---
id: plan-decisions
title: Decisions
description: >
  Decision log for this unit of work. Capture tradeoffs and rationale.
---

# Decisions — hk-profile-applicability-reviews

## What Changed

- Added profile path applicability fields for checks/reviews.
- Added changed-path suggestions and named check/review evidence binding.
- Added named review prompt rendering from profile prompt files.
- Added readiness enforcement for required items from the target's resolved user-config profile.

## Why

- Repo-specific checks and reviews are useful only when agents can tell when they apply.
- This slice lets profiles suggest or require the right checks/reviews for changed paths while keeping HK shell-first and leaving execution/dispatch to the agent.

## Where Reflected

- `src/harness_toolkit/kit/profiles/models.py`
- `src/harness_toolkit/kit/profiles/__init__.py`
- `src/harness_toolkit/kit/cli.py`
- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/readiness/policy.py`
- `src/harness_toolkit/kit/rendering/review_prompt.py`
- `README.md`
- `SPEC.md`
- `docs/portable-workflow.md`
- `docs/agent-adoption.md`
- `templates/.agent/skills/harness-kit-profile-authoring/references/profile-mining.md`
- `templates/.agent/skills/harness-kit-profile-authoring/references/examples.md`

## 2026-05-08 — Use plain checks/reviews product language

- Decision: Keep public/product wording as checks and reviews; do not introduce a new “confidence builders” term.
- Rationale: Checks and reviews are already understandable and fit the existing profile model.

## 2026-05-08 — Keep suggestions advisory but make required matches readiness-affecting

- Decision: `applies_when` suggests; `required_when` affects readiness when the profile is the target's resolved user-config profile.
- Rationale: Initial adopters can start with generic advisory menus, while mature repos can encode required domain checks/reviews for specific changed paths.

## 2026-05-08 — Bind evidence/reviews explicitly by name

- Decision: Add `hk validate --check NAME` and `hk review add --review NAME` instead of inferring from command text or reviewer names.
- Rationale: Explicit binding is easier to audit and avoids brittle heuristics.

## 2026-05-08 — Review instructions should be file-backed

- Decision: Prefer profile `prompt_file` for substantive review instructions; named review prompts render the file plus live work context.
- Rationale: TOML stays small, prompts can be reviewed/versioned as normal text, and HK remains a renderer rather than a runner.

## 2026-05-08 — Keep profile flags discovery-only

- Decision: `--profile` / `--profiles-dir` can inspect suggestions, but lifecycle enforcement uses the target's resolved user-config profile.
- Rationale: This preserves the previous lifecycle boundary: profile flags guide discovery and do not become hidden lifecycle state.
