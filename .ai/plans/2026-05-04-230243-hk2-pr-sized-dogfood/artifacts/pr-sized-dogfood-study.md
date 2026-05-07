# HK 2.0 PR-sized dogfood study

## Setup

Ran three parallel worker subagents against temporary shallow snapshots, not the
original repositories:

| Trial | Temp repo | Baseline commit | Intended replay |
|---|---|---:|---|
| <REDACTED_ORG> Ads ML | `/tmp/hk2-pr-sized-trials/<REDACTED_ORG>-ads-ml` | `7d73f2c35` | table_endorsement_scorer coalesce phase |
| <REDACTED_ORG> Ads API | `/tmp/hk2-pr-sized-trials/<REDACTED_ORG>-ads-api` | `05f586067` | AdSetBuilder DeliveryConfig / delivery_config_json migration |
| Foreman | `/tmp/hk2-pr-sized-trials/foreman` | `61e0f23` | macOS notification sound + click/lifecycle handling |

The trial repos were created via shallow fetch of the parent commits, with no git
remote configured. That reduces the chance of simply reading the future PR diff.
Workers were given little HK guidance beyond:

> Use the HK CLI for this workflow; begin by exploring the CLI to onboard to it.

Because the installed `~/.local/bin/hk` is still an older command surface, the
trial provided this current-checkout wrapper:

```text
/tmp/hk2-pr-sized-trials/bin/hk
```

The wrapper delegates to `uv --directory ~/git_repositories/harness-toolkit run
hk` and logs every HK invocation to:

```text
/tmp/hk2-pr-sized-trials/hk-commands.jsonl
```

Worker reports:

- `/tmp/hk2-pr-sized-trials/reports/<REDACTED_ORG>-ads-ml-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/<REDACTED_ORG>-ads-api-worker-report.md`
- `/tmp/hk2-pr-sized-trials/reports/foreman-worker-report.md`

Generated handoffs after the run:

- `/tmp/hk2-pr-sized-trials/reports/<REDACTED_ORG>-ads-ml-handoff.md`
- `/tmp/hk2-pr-sized-trials/reports/<REDACTED_ORG>-ads-api-handoff.md`
- `/tmp/hk2-pr-sized-trials/reports/foreman-handoff.md`

## Trial results

### <REDACTED_ORG> Ads ML

Worker implemented a table endorsement scorer coalesce phase.

Changed tracked files:

- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/BUILD.bazel`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/README.md`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/model.py`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/publish.py`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/score.py`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/settings.py`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/test/BUILD.bazel`

Untracked implementation files:

- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/coalesce.py`
- `<REDACTED_ORG>_ai/models/py/table_endorsement_scorer/test/test_coalesce.py`

Validation:

- Passed HK-captured `python3 -m py_compile` on changed scorer modules/tests.
- Passed HK-captured `clint lint --fix` after one formatting failure and manual
  wrap fix.
- Blocked HK-captured Bazel tests because the shallow snapshot lacked
  `.bazelconfigs/bazel-8-6/MODULE.bazel.lock`.
- Blocked HK-captured `./clyde test ai` on macOS arm64 because
  `fbgemm-gpu==1.3.0+cu129` has no compatible local wheel.

Final readiness observed by parent:

```json
{"ready": false, "status": "not-ready"}
```

Readiness failures: missing plan, missing decision/spec reflection, missing
review, stale sync.

### <REDACTED_ORG> Ads API

Worker implemented a DeliveryConfig migration for ad set construction and JSON
persistence.

Changed files:

- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/lib/model_ops/builders/ad_set_builder.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/lib/update_campaign/utils/ad_sets.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/models/ad_sets.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/models/tests/test_ad_sets.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/response_models/ads_manager/ad_sets.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/modules/ads/scripts/create_bounty_ad_hierarchy.py`
- `<REDACTED_ORG>_api/<REDACTED_ORG>/views/admin/tests/quests/test_update_quest.py`

Validation:

- Passed HK-captured `python -m py_compile` on changed Python files.
- Passed HK-captured `clint lint --fix`, then a second clean lint pass.
- Blocked HK-captured focused API tests:
  - first attempt used moved command shape `./clyde test api` and hit Slyncy
    setup failure;
  - local retry with `SLYNCY_FORCE_LOCAL=1 ./clyde api test ...` failed because
    backend service tests are unsupported locally on macOS.
- Passed direct `git diff --check` outside HK.

Final readiness observed by parent:

```json
{"ready": false, "status": "not-ready"}
```

Readiness failures: missing review and stale sync. Plan/decision/validation were
present.

### Foreman

Worker implemented macOS notification sound config and terminal-notifier style
click/lifecycle handling.

Changed files:

- `README.md`
- `SPEC.md`
- `docs/architecture.md`
- `src/cli.rs`
- `src/config.rs`
- `src/runtime.rs`
- `src/services/logging.rs`
- `src/services/notifications.rs`
- `src/services/startup_cache.rs`

Validation:

- Passed direct local iteration commands:
  - `cargo fmt && cargo check`
  - `cargo test notifications --lib --tests`
  - focused config/runtime tests
- HK-captured `mise run check`:
  - failed first because mise config was untrusted;
  - failed second on clippy `derivable_impls`;
  - passed after fix.

Final readiness observed by parent:

```json
{"ready": false, "status": "not-ready"}
```

Readiness failures: missing review and stale sync. Plan/decision/validation were
present.

## HK command path observations

### Common successful path

All three workers did begin by exploring HK, usually with:

```bash
hk --help
hk status --help
hk start --help
hk validate --help
```

The most natural successful lifecycle shape was:

```bash
hk brief/status --target <repo>
hk init --target <repo>          # two <REDACTED_ORG> workers used this
hk start <slug> --target <repo>
hk plan ... --target <repo>      # Ads API and Foreman only
hk validate --why ... --target <repo> -- <native command>
hk evidence list --target <repo>
hk sync --target <repo>
hk ready --target <repo> --json
hk decide ... --target <repo>    # Ads API and Foreman discovered this late
hk sync --target <repo>
```

The validation verb remained the clearest piece: every worker used HK to record
meaningful command evidence with rationale, including failed environment-blocked
commands.

### Where HK was not used

Workers correctly did not use HK for code edits, search, or normal file reads.
They used regular tools for that.

Workers also used direct commands for fast local iteration/discovery:

- Ads ML: direct `./clyde -h`, `./clyde test -h`, direct failed pytest/syntax
  exploration before settling on HK-captured validation.
- Ads API: direct `./clyde -h`, `./clyde api test -h`, `git status`, `git diff`,
  `git diff --check`.
- Foreman: direct `cargo fmt`, `cargo check`, focused `cargo test` iterations,
  then HK-captured the full `mise run check` gate.

This is mostly good: HK remained shell-first evidence capture, not a task runner.

### Incorrect or confusing HK usage

1. **`--target .` resolved unexpectedly for Foreman.**
   - Foreman worker ran `hk brief --target .` and `hk status --target .` from the
     trial repo, but reported that HK resolved to harness-toolkit context.
   - This likely comes from the wrapper implementation using `uv --directory`,
     which changes cwd before invoking HK. Explicit absolute `--target` fixed it.
   - Product implication: the current-checkout wrapper is useful for dogfood but
     creates target confusion. For real usage, install the current HK binary or
     make wrapper preserve caller cwd semantics.

2. **`hk evidence` subcommand shape was missed by all workers.**
   - Workers tried `hk evidence --target ...`; it failed because `evidence`
     requires `evidence list`.
   - Product implication: either show a stronger error/next step for bare command
     groups, or consider `hk evidence` defaulting to list.

3. **`hk sync --profile` was guessed.**
   - Ads ML tried `hk sync --target ... --profile python --json`; failed because
     sync has no profile.
   - Product implication: agents infer profile flags should be accepted on most
     lifecycle commands. Either keep help clearer or decide if harmless profile
     acceptance should be supported/ignored.

4. **Legacy `hk sync-check` still attracted a worker.**
   - Foreman tried `hk sync-check --target ... --profile rust-mise --json` and got
     `No plan found`.
   - Product implication: legacy commands are still too prominent/confusing in a
     lifecycle-first flow. Mark legacy more clearly or move under `hk legacy` in
     help once migration allows.

5. **`decide` was discovered late.**
   - Ads API and Foreman only recorded decisions/spec reflections after `ready`
     failed.
   - Ads ML never recorded plan or decision at all.
   - Product implication: `start`/`ready` next-step guidance should make the full
     minimum lifecycle more obvious without making trivial context mandatory.

6. **Review gate behaved correctly.**
   - No worker attempted to self-review after the updated review UX.
   - All final readiness checks failed on missing review, which is the desired
     behavior for same-context implementation workers.

7. **Sync went stale after worker activity.**
   - Parent-observed readiness was stale for all three. Causes include late
     decision/note events after sync and untracked `.pi/` state created by agent
     tooling in the temp repos.
   - Product implication: sync freshness is doing its job, but agent-generated
     local tool state can surprise workers. Consider docs/warnings around ignored
     local agent state, or ensure common local dirs do not perturb trial diffs.

8. **Handoff rendering still says failed commands “validate”.**
   - Failed validation evidence renders as `fail ... — validates: <why>`.
   - Product implication: handoff wording should distinguish “attempted to
     validate” from passing evidence.

9. **No context records were created.**
   - All three handoffs show no context. Given the minimal prompt, workers did
     not treat context as part of onboarding or handoff. This may be acceptable,
     but for PR-sized work it suggests `hk context` is under-discovered unless
     explicitly prompted.

## Command counts from wrapper log

| Trial | HK commands | Failed HK commands | Most-used commands |
|---|---:|---:|---|
| Ads ML | 30 | 5 | `validate` 10, `evidence` 4, `sync` 4 |
| Ads API | 32 | 3 | `validate` 7, `status` 4, `evidence` 3, `sync` 3 |
| Foreman | 27 | 5 | `validate` 4, `status` 4, `evidence` 3, `sync` 3 |

Parent ran three post-trial `ready` checks and generated three handoffs; those are
separate from the worker paths.

## Product takeaways

### Worked

- The HK CLI was discoverable enough for workers to onboard with `--help`.
- Workers naturally used HK for evidence capture and sync/readiness checks.
- Review independence change worked: implementation workers did not launder
  self-review as external review.
- Readiness failures were actionable; they identified missing review, missing
  decision/plan, and stale sync.
- HK stayed out of native command semantics.

### Needs follow-up

1. Install/current-binary story: dogfood wrapper caused `--target .` confusion.
2. Bare command-group UX: `hk evidence` should guide to `hk evidence list`.
3. Legacy command prominence: `sync-check` still pulls agents into old workflow.
4. Full lifecycle guidance: agents discover `decide` and review late; Ads ML
   skipped plan/decision entirely.
5. Failed evidence rendering: handoff should not say failed commands “validate.”
6. Agent local state: `.pi/` untracked state can stale sync checkpoints.
7. Context under-discovery: workers did not record context even for PR-sized work.
