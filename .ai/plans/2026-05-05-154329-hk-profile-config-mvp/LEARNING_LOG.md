---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-05 — Scope questionnaire

- User wants a real profile/config MVP rather than deferring all config work.
- Decided on user-level config with inline profiles, XDG/env lookup, explicit longest-prefix target resolution, and `hk checks --target .` using resolved profiles when available.
- Repo-level `.harness/harness.toml`, executable review backend adapters, persistent sync ignores, and auto-running checks remain deferred.

## 2026-05-05 — Review guidance belongs in profiles too

- User pointed out that review backend instructions are analogous to check guidance and should live near the profile.
- Adjusted scope to include lightweight `[[profiles.<name>.reviews]]` guidance with backend label, rubric, dispatch hint, inline prompt, and optional prompt file.
- Multiple review entries are surfaced for agents to dispatch independently/in parallel when their harness supports it; HK still does not orchestrate review execution.

## 2026-05-05 — Dread/foreman profile config dogfood

- Temp clones of dread and foreman both resolved the configured profile through `hk profile resolve --target . --json`.
- `hk checks --target . --json` used the resolved profile without an explicit `--profile` flag.
- Workers selected the expected validation loops from profile checks: dread used focused formatting pytest + ruff; foreman used `cargo test --test cli_config` + `cargo fmt --check`.
- Both workers used profile review guidance (`codex review --uncommitted`) and recorded accepted `hk review add --backend codex` entries.
- Codex/Pi `.pi` monitor state still appeared after review; parent remediated with explicit `hk sync --exclude .pi --reason ...` and both repos reached `ready`.
