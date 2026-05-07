# Fresh-Context Review Summary

Reviewer: builtin `reviewer` subagent, fresh context
Date: 2026-05-07

## Initial review

No blocking findings.

Notes:

- CLI preflight correctly keeps profile flags scoped to discovery commands instead of adding no-op lifecycle options.
- Native command args after `hk validate --` are not intercepted; the test covers `validate --why ... -- tool --profile ci`.
- Generated user-level and repo-scope instruction snippets clearly warn agents not to carry profile flags into lifecycle commands.
- Public docs were updated consistently.
- Focused tests cover instructions and the actionable preflight error.

## Re-review after narrowing preflight to known commands

No blocking findings.

Notes:

- `_PROFILE_FORBIDDEN_COMMANDS` prevents the friendly profile error from masking unknown commands.
- Unknown commands with `--profile` fall through to Cyclopts' normal unknown-command error.
- Discovery commands remain exempt: `hk profile`, `hk checks`, and `hk instructions`.
- Native command arguments after `hk validate --` remain preserved.
- The reviewer noted the command list is manually maintained and future top-level lifecycle additions should update it if they should receive the same actionable preflight.
