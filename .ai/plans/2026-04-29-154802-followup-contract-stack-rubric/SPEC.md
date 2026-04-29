---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
  Optional — create only for complex or scoped work.
---

# Specification — followup-contract-stack-rubric

## Problem

Two post-merge follow-up issues are open:

- `scripts/plan_contract.py` is now a long mixed-responsibility helper module.
  It handles plan discovery, git inspection, markdown parsing, metadata parsing,
  artifact validation, and path safety in one file, which makes future contract
  changes harder to review.
- The first refactor split that helper under `scripts/`, but user review
  identified that as still awkward: the slice workflow should own its tiny
  implementation CLI instead of scattering capability across repo-local scripts.
- The Rust stack made the implicit future-stack bar visible. Python, Go, and Rust
  already have broad test parity, but the project does not yet document the
  acceptance rubric reviewers should apply before adding another stack.

## Requirements

### MUST

- Preserve all public mise task names and invocation patterns.
- Preserve current sync-contract behavior before adding any new policy.
- Keep generated repos dependency-light; do not add a YAML parser or new CLI
  framework for plan-contract checks.
- Move planning, slice prompt rendering, and handoff-check implementation into
  the `slice-workflow` skill-local CLI.
- Keep generated repos dependency-light: stdlib runtime code and uv-managed CLI
  execution only.
- Preserve `mise run ...` as the user-facing interface; do not expose a second
  workflow command surface as the normal path.
- Document where slice workflow implementation now lives.
- Add a stack acceptance rubric that distinguishes required capabilities,
  optional stack-specific extras, and allowed documented deviations.
- Align contract tests with the stack rubric so missing reviewer guidance is
  caught deterministically.
- Include the generated-project smoke matrix expectation in docs.

### SHOULD

- Keep `.mise/tasks/*-check` wrappers easy for agents to inspect.
- Favor behavior-focused tests over tests that do not reflect user behavior.
- Avoid making the stack rubric so strict that experimental stacks cannot land
  behind documented gaps.
- Keep documentation terse enough to be useful during review.

## Constraints

- Do not build a separate orchestrator.
- Do not introduce a second user-facing task runner.
- Do not use fuzzy prose-quality checks for CI.
- Do not refactor unrelated stack behavior while documenting the acceptance bar.
- Do not leave compatibility scripts behind once every caller is migrated to the
  skill-local CLI.
