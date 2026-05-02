---
id: plan-learning-log
title: Harness Kit Naming Learning Log
description: >
  Dev diary for naming brainstorm and persistence.
---

# Learning Log

## 2026-05-02

- User wanted to brainstorm a better name for the portable CLI currently named
  `agent-workflow`.
- Initial names like `agent-loop`, `agent-plan`, and `agent-slice` were useful
  but did not capture the user's framing of **harness engineering**.
- `agent-harness` / `harness` sounded promising, but the user pointed out that
  this conflicts with the existing meaning of harnesses like Claude Code, Codex,
  Pi, and Cursor.
- `harness-eng-toolkit` was clear but too long as a daily command. This led to a
  split: use **Harness Engineering Toolkit** as the umbrella, with **hk** as the
  short command.
- The product boundary that resonated:

  ```text
  Harness Engineering Toolkit
  ├── harness-kit / hk
  └── harness-scaffold
  ```

- User asked to persist the idea as a plan slice rather than implement it now.
