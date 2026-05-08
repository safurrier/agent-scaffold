---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about intended implementation approach.
---

# IMPLEMENTATION — hk2-dogfood-ux-fixes

## Implemented

### Repo-local dogfood skill

Added:

```text
.agent/skills/hk-pr-sized-dogfood/SKILL.md
```

The skill documents the reusable PR-sized dogfood replay process: temp snapshots,
minimal worker prompting, current HK wrapper, HK command logging, worker reports,
parent readiness/handoff capture, and synthesis checklist.

### Current HK dev shim

Added:

```text
scripts/hk-dev
.mise/tasks/hk-dev
```

The script uses:

```bash
uv --project "$PROJECT_ROOT" run hk "$@"
```

This preserves the caller cwd, unlike `uv --directory`, so `--target .` works in
temp dogfood repos.

### CLI discoverability

- Bare `hk evidence` now exits with a direct hint to `hk evidence list --target <repo> --json`.
- Root-level `hk sync-check` moved under `hk legacy sync-check`.
- Built-in profile handoff guidance now points to `hk sync && hk ready` instead
  of `hk sync-check`.
- `hk start` next-step output now shows the fuller lifecycle path and stronger
  optional context guidance.

### Readiness and handoff wording

- Failed validation evidence now renders as `attempted to validate` in handoffs.
- Passing evidence still renders as `validates`.
- Readiness sync failures now warn when common agent-local state such as `.pi/` is
  present in git status.

### Docs/context

Updated repo docs/spec/design surfaces to mention:

- `scripts/hk-dev` for current checkout dogfood;
- repo-local dogfood skill;
- legacy `sync-check` placement;
- failed validation wording expectations.

## Rerun

Reran three varied PR-sized dogfood trials after implementation. Synthesis:

```text
artifacts/pr-sized-dogfood-rerun.md
```

Key outcome: target confusion and legacy `sync-check` drift improved; evidence
wording fixed; `.pi` warning worked; lifecycle plan/decision completion remains
mixed and sync policy still needs a dedicated ignore/override design.
