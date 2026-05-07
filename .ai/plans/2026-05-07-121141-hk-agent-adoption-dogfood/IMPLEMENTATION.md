---
id: plan-implementation
title: Implementation Notes
description: >
  What changed in this slice.
---

# IMPLEMENTATION — hk-agent-adoption-dogfood

## Skill update

Added `Agent adoption snippet variant` to:

```text
.agent/skills/hk-pr-sized-dogfood/SKILL.md
```

The variant describes how to:

- create a temp repo;
- put `hk instructions --scope user` output in `AGENTS.md`;
- expose checkout-local `hk` through a logging PATH wrapper;
- run a fresh agent without mentioning HK or AGENTS.md;
- evaluate whether the snippet was followed.

Also normalized older placeholder text in the skill so the skill validator no longer rejects angle-bracket placeholders.

## Dogfood run

Created:

```text
/tmp/hk-agent-adoption-trial/repo
```

Ran `codex exec` with this prompt:

```text
Add a small Python utility function and tests for it. Do not commit. When done,
write /tmp/hk-agent-adoption-trial/worker-report.md summarizing what you changed
and what validation you ran.
```

The prompt intentionally did not mention HK or AGENTS.md.

## AGENTS.md review

Reviewed root `AGENTS.md` using context-engineering principles and wrote a short
follow-up assessment to:

```text
artifacts/agents-md-relevance-review.md
```
