---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-04-28

- User clarified that `mise` should stay as the ergonomic interface, but the
  prompt/workflow policy should probably live in a skill rather than scattered
  scripts and low-quality role prompts.
- Obsidian notes supported the split: skills are the interface/policy layer,
  while CLI/tool code owns deterministic git/path/file work once scripts start
  accumulating.
- For v1, the agreed runtime boundary is prompt rendering only. Users already
  have Codex/Claude sessions open, and provider-neutral generated repos should
  not launch a harness automatically.
- The generated-project E2E needs an initialized feature branch before `mise run
  plan -- <slug>` can work, because the plan task intentionally refuses
  branchless/default-branch work.
- Prompt templates should not include render timestamps. The timestamp made real
  prompt artifacts change on every re-render even when inputs were stable.
