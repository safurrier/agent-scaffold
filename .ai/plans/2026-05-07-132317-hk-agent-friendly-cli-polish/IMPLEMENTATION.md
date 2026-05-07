---
id: plan-implementation
title: Implementation Notes
description: >
  What changed and where.
---

# IMPLEMENTATION — hk-agent-friendly-cli-polish

## Changes

### Generated instructions and public docs

Updated the user-level and repo-scope generated snippets in:

- `src/harness_toolkit/kit/cli.py`

Updated matching public docs in:

- `docs/agent-adoption.md`
- `docs/portable-workflow.md`

The guidance now says profile flags are for discovery commands (`hk profile`, `hk checks`, repo-scope `hk instructions`) and should not be copied onto lifecycle commands such as `hk start`, `hk validate`, `hk status`, `hk ready`, or `hk handoff`.

### Actionable CLI error

Added a small argv preflight in `src/harness_toolkit/kit/cli.py` before Cyclopts dispatch:

- detects `--profile` and `--profiles-dir` on top-level lifecycle/other commands that do not accept those flags;
- exempts `hk profile`, `hk checks`, and `hk instructions`;
- ignores everything after a native-command `--` separator so `hk validate -- ... --profile ...` remains valid native-command syntax;
- prints repair steps:
  - `hk profile resolve --target . --json`
  - `hk checks --target . --json`
  - `hk <command> --help`

### Help examples

Added examples to:

- `hk ready --help`
- `hk review prompt --help`

### Tests

Added focused coverage in `tests/unit/test_portable_workflow.py` for:

- generated user/repo instructions include profile-flag warning;
- `hk start ... --profile python` exits with an actionable error and no traceback;
- native command profile flags after `hk validate --` are not intercepted by the preflight.

### Audit

Recorded the agent-friendly CLI audit at:

- `artifacts/agent-friendly-cli-audit.md`
