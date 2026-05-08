# Subagent Rollout Summary

## Fresh-context code review

Reviewer ran focused parity tests and `git diff --check`. No HK2 lifecycle/profile/spec/rendering/capture/readiness behavior regressions were found in focused tests.

Initial blockers:

1. Profile seam was only split at models; built-ins/config/resolution/presentation were still too concentrated.
2. Final gate/rollout evidence was not yet recorded.

Follow-up action taken after review:

- Added `profiles/builtins.py` for built-in profile definitions.
- Added `profiles/resolution.py` for target-to-profile resolution.
- Kept `profiles/__init__.py` as the catalog/facade and preserved existing imports.
- Re-ran focused profile/HK2 tests successfully.
- Final gates and rollout evidence are recorded in `VALIDATION.md`.

## HK2 lifecycle rollout

Temp repo: `/tmp/hk-rollout-smoke-final.C17EuD`

Successful lifecycle commands via `scripts/hk-dev`:

```bash
hk start rollout-smoke --plan 'Exercise lifecycle after architecture refactor'
hk context 'Temporary smoke repo exercising lifecycle after architecture refactor'
hk decide 'No spec-impacting behavior changed in this external dogfood smoke.' --spec-impact not-needed
hk validate --why 'Smoke validation command for rollout lifecycle' -- python3 -c 'print("ok")'
hk review add --backend subagent --reviewer rollout-fresh-context --rubric core-quality --summary 'Smoke review accepted'
hk sync
hk ready --json
hk handoff
```

Result: `ready: true`, `status: ready`.

Removed legacy command checks:

- `hk legacy plan` returned non-zero with unknown command.
- `hk attach` returned non-zero with unknown command.

Observed note: bare `hk context` and bare `hk decide --spec-impact not-needed` correctly fail because both require text.

## Profile/config rollout

Temp config under `/tmp/hk-rollout-b-20260505220008/harness.toml`.

Verified:

- Repo target resolved to `repo-profile`.
- Nested module target resolved to `module-profile` via longest-prefix matching.
- Independent second repo resolved to `widget-profile`.
- Checks and reviews returned as guidance only.
- `prompt_file` loaded relative to `harness.toml`.

No functional degradation observed.

## Spec/rendering rollout

Temp repo: `/tmp/hk-dogfood-c-clean.Un5rw2`

Verified:

- `hk spec init --local` created local-only spec.
- `hk spec status`, `hk spec outline`, and `hk spec promote --dry-run` worked.
- `hk review prompt` rendered expected reviewer instructions and no Codex slash-command guidance.
- `hk handoff` rendered expected lifecycle sections and conservative not-ready state.

Follow-up action taken after rollout:

- Reworded Claude Code review guidance from `legacy Task` to `Task alias` to avoid unrelated legacy terminology.

## Disposition

No degradation or failure mode remains that blocks merge readiness. The only observed command failures were expected argument-validation failures or expected removed-command failures.
