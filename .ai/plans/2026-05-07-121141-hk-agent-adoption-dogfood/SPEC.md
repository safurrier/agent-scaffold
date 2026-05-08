---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — hk-agent-adoption-dogfood

## Problem

We added a compact user-level Harness Kit AGENTS.md snippet, but we had not tested
whether a fresh agent would actually follow it when it is the only repo guidance.
We also needed a quick relevance review of the root `AGENTS.md` after the PR's
many product-direction additions.

## Requirements

### MUST

- Add a reusable dogfood variant to the existing HK dogfood skill.
- Run one realistic trial where the prompt does not mention HK or AGENTS.md.
- Use a temp repo and checkout-local `hk` wrapper, not an original source repo.
- Log every `hk` invocation.
- Summarize whether the agent followed the snippet.
- Review current root `AGENTS.md` relevance after the PR.

### SHOULD

- Identify HK UX sharp edges found in the trial.
- Keep the dogfood variant small enough to reuse later.

## Constraints

- Do not mutate source repos during dogfood.
- Do not add more public docs unless the trial shows a clear gap.
