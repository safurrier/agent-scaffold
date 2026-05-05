# HK 2.0 PR-sized dogfood rerun after UX fixes

## Setup

Reran PR-sized dogfood after the first implementation pass for dogfood UX fixes.
The rerun used varied tasks from the first study and the new checkout-local HK
shim path.

Temp root:

```text
/tmp/hk2-pr-sized-trials-v2
```

HK wrapper:

```text
/tmp/hk2-pr-sized-trials-v2/bin/hk
```

The wrapper delegates to:

```text
/Users/alex.furrier/git_repositories/harness-toolkit/scripts/hk-dev
```

Unlike the first run's `uv --directory` wrapper, `scripts/hk-dev` uses
`uv --project`, so it preserves the worker cwd and allows `--target .` to mean
the temp repo.

Worker reports:

- `/tmp/hk2-pr-sized-trials-v2/reports/discord-ads-ml-worker-report.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/discord-ads-api-worker-report.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/foreman-worker-report.md`

Generated handoffs:

- `/tmp/hk2-pr-sized-trials-v2/reports/discord-ads-ml-handoff.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/discord-ads-api-handoff.md`
- `/tmp/hk2-pr-sized-trials-v2/reports/foreman-handoff.md`

HK command log:

- `/tmp/hk2-pr-sized-trials-v2/hk-commands.jsonl`

## Trial matrix

| Trial | Temp repo | Baseline commit | Task |
|---|---|---:|---|
| Discord Ads ML | `/tmp/hk2-pr-sized-trials-v2/discord-ads-ml` | `6d67f5d09` | Schedule `table_endorsement_scorer` monthly and add per-run metrics/output summary |
| Discord Ads API | `/tmp/hk2-pr-sized-trials-v2/discord-ads-api` | `4170b7bc` | Migrate delivery/pacing readers from flat AdSet delivery fields to `delivery_config` accessors |
| Foreman | `/tmp/hk2-pr-sized-trials-v2/foreman` | `95d8611` | Keep native agent signals hook-only |

## Results by trial

### Discord Ads ML

Worker implemented monthly production scheduling and run metrics for
`table_endorsement_scorer`.

Changed files included:

- `discord_ai/models/py/table_endorsement_scorer/settings.py`
- `discord_ai/models/py/table_endorsement_scorer/publish.py`
- `discord_ai/models/py/table_endorsement_scorer/model.py`
- `discord_ai/models/py/table_endorsement_scorer/card.py`
- `discord_ai/models/py/table_endorsement_scorer/README.md`
- `discord_ai/models/py/table_endorsement_scorer/test/BUILD.bazel`
- new `discord_ai/models/py/table_endorsement_scorer/test/test_publish.py`
- new `discord_dagster/repositories/ml_predictions/repo/pipelines/ml_output/table_endorsement_scorer_batch.py`

Validation:

- Passed HK-captured `python3 -m py_compile` for changed scorer/Dagster files.
- Passed HK-captured `clint lint --fix` after formatting.
- Blocked HK-captured Clyde AI tests on macOS ARM due Linux-only `fbgemm-gpu`.
- Blocked HK-captured Bazel tests due missing `.bazelconfigs/bazel-8-6/MODULE.bazel.lock` in the shallow snapshot.

Final parent-observed readiness:

```json
{"ready": false, "status": "not-ready"}
```

Readiness state:

- plan: pass
- decision/spec reflection: pass
- validation: pass
- review: fail, as expected for implementation worker
- sync: fail, with new `.pi` agent-local warning

### Discord Ads API

Worker implemented a broader delivery reader migration to `delivery_config`.

Changed files included 22 Ads API files across:

- delivery config/ad set models;
- final select/auction stages;
- delivery pipeline utilities;
- UAI utilities;
- pacing context/calculation/logging/tracking surfaces;
- traffic prediction;
- Ads Manager response/update copy paths;
- focused pacing tests.

Validation:

- Passed HK-captured `python3 -m py_compile` on changed modules.
- Passed HK-captured `clint lint --fix`.
- Passed direct `git diff --check`.
- Blocked HK-captured Clyde/API and direct pytest attempts due Slyncy/macOS/local dependency constraints.

Final parent-observed readiness:

```json
{"ready": false, "status": "not-ready"}
```

Readiness state:

- plan: fail
- decision/spec reflection: fail
- validation: pass
- review: fail
- sync: fail, with new `.pi` agent-local warning

### Foreman

Worker implemented hook-only native signal handling.

Changed files:

- `src/integrations/native.rs`
- `tests/native_hook_tmux_e2e.rs`
- `SPEC.md`
- `docs/architecture.md`
- `docs/workflows.md`

Validation:

- Passed HK-captured focused native integration tests.
- Passed HK-captured native hook tmux E2E smoke.
- Passed HK-captured final `cargo fmt --check`.
- HK-captured `mise run check` remained blocked/failing on an existing or unrelated `notification_runtime` timeout.

Final parent-observed readiness:

```json
{"ready": false, "status":"not-ready"}
```

Readiness state:

- context: recorded
- plan: pass
- decision/spec reflection: fail
- validation: pass
- review: fail
- sync: fail, with new `.pi` agent-local warning

## HK command counts

| Trial | HK commands | Failed HK commands | Most-used commands |
|---|---:|---:|---|
| Ads ML | 41 | 6 | `validate` 11, `sync` 4, `ready` 4 |
| Ads API | 27 | 7 | `validate` 9, `status` 4 |
| Foreman | 29 | 7 | `validate` 12, `status` 5 |

Parent `ready`/`handoff` commands are included in the counts when they targeted a
trial repo.

## UX fix evaluation

### Current-HK dev shim: improved

Workers used `--target .` successfully in all three repos. The first dogfood's
major wrapper/cwd confusion did not recur.

This suggests `scripts/hk-dev` plus a wrapper using that script solves the
current-checkout dogfood problem.

### Failed evidence wording: fixed

Generated handoffs now render failed evidence as:

```text
attempted to validate: ...
```

Passing evidence still renders as:

```text
validates: ...
```

This directly fixed the previous overclaim.

### Legacy command drift: improved

No worker tried `hk sync-check` in the rerun. The root command being moved under
`hk legacy sync-check`, plus updated profile handoff guidance, appears to reduce
legacy drift.

### Agent-local sync warning: improved but still noisy

All parent readiness checks reported stale sync and now included:

```text
Common agent-local state is present in git status (.pi); remove/ignore it or resync intentionally.
```

This is clearer than silent staleness, but confirms the product still needs a
proper policy: warning-only, explicit ignore file, or scary override.

### Bare `hk evidence`: partially improved

Workers still tried bare `hk evidence --target .` in Ads ML and Ads API. The new
hint prevented a dead end and they then ran `hk evidence list --target . --json`.

This supports the user's selected policy: strict command group, direct hint.

### Context guidance: slightly improved

Foreman used `hk context` for missing task context files. Ads ML and Ads API still
did not record context. Stronger optional guidance helped some but did not make
context universal.

### Plan/decision guidance: mixed

Ads ML recorded plan and multiple decisions. Foreman recorded context + plan but
missed decision/spec reflection. Ads API recorded neither plan nor decision.

`hk start` guidance helped, but agents doing complex implementation still skip or
forget lifecycle records unless they run `hk ready` and react to failures.

### Review gate: still working as intended

No implementation worker attempted self-review. All readiness checks remained
blocked on missing external/fresh-context review.

## Product takeaways after rerun

### Fixes that worked

- Current checkout dev shim avoids `--target .` wrapper confusion.
- Failed evidence wording is correct in handoffs.
- Moving legacy `sync-check` out of root reduced accidental old-workflow use.
- Bare `hk evidence` hint helped recovery.
- Agent-local sync warning made stale sync more explainable.

### Remaining issues

1. **Lifecycle record completion is still unreliable.**
   - Agents still skip plan/decision on some PR-sized tasks.
   - `ready` catches this, but only if agents run it and iterate.

2. **Sync freshness remains noisy because of `.pi/`.**
   - Warning is useful, but not a complete policy.
   - Follow-up design likely needs a `.harnessignore` or explicit dangerous sync override.

3. **Context remains optional enough to be skipped.**
   - That may be acceptable, but context is not naturally used by every agent even
     for PR-sized work.

4. **Environment blockers dominate Discord validation.**
   - HK captures them well, but local macOS dogfood cannot prove full CI behavior.
   - Future Discord trials should run in Coder/Slyncy/Linux-compatible contexts
     when validation quality matters.

5. **Finalization helper remains deferred.**
   - Agents still often end without a ready handoff, but this is mostly because
     review is intentionally unavailable in worker context and `.pi` stales sync.
