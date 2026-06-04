# HK export: `2026-06-03-134231-status-evidence-freshness`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-06-03-134231-status-evidence-freshness --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-06-03-134231-status-evidence-freshness`
- Branch: `feat/hk-status-evidence-freshness`

## Context
- Implement HK status evidence freshness: generic no-profile path coverage, profile label freshness, export neutrality notes, and dogfood regression scenarios under repo-local hk-pr-sized-dogfood skill.

## Plan
- # HK Status Evidence Freshness Plan

## Architecture polish review applied

Current plan grade after review: **A-**. The shape is product-aligned: keep profile config simple, make HK derive freshness from evidence coverage, and move loop avoidance into `hk status` facts instead of policy knobs. The main polish needed is to avoid letting readiness, evidence capture, and CLI rendering collapse into one string-message module.

### Highest-leverage review changes

1. **Add a typed closeout/freshness diagnostic seam.** Do not pack stale paths, counters, export neutrality, and suggested commands into `ReadyCheck.message` strings. Keep `ready_for_events()` as the binary readiness policy and add a separate typed diagnostic builder that `hk status` renders.
2. **Keep required profile checks authoritative.** Path-aware validation can decide whether a recorded `--check fast-gate` remains fresh; it must not let unrelated focused evidence satisfy a required profile check.
3. **Make evidence coverage semantics explicit.** Validation evidence should record post-command changed path hashes, excluding active HK export artifacts, with backward-compatible exact-diff fallback for older evidence.
4. **Bake active HK export neutrality into lifecycle code, not profile config.** Status should explain when only active export artifacts changed and route the agent to export checks.
5. **Expose loop/counter facts as observability only.** Status can say “codex-review has 2 accepted records” or “fast-gate has 3 runs”; it should not enforce max turns or add profile knobs.

## Product goal

Make `hk status` the default agent closeout coach so agents do not repeatedly rerun broad validation and review when no source-risk changed. Preserve the lifecycle guarantees: plan, decision/spec reflection, validation evidence, external-enough review, sync, and handoff readiness.

No new profile config for this slice:

- no `rerun_policy`
- no `prefer_targeted_followup`
- no `max_turns`
- no per-profile export ignore rules

Profiles continue to define only checks/reviews, purpose, command/prompt hints, `applies_when`, and `required_when`. HK derives freshness from current changed paths and evidence coverage.

The feature has two usefulness layers:

1. **Generic evidence freshness, always available.** Even with no `harness.toml` or custom profile, HK can compare current changed paths to validation/review evidence snapshots and report fresh/stale/uncovered paths.
2. **Profile-required item freshness, available when profiles resolve.** Profiles add named requiredness, such as `profile-check:fast-gate` or `profile-review:codex-review`, but they are not required for the closeout diagnostics to be useful.

Product principle: **profiles make freshness specific; path coverage makes freshness useful even without profiles.**

## Target user-facing behavior

`hk status --target .` should include compact default guidance like this when profile-required checks/reviews exist:

```text
checks:
- profile-check:fast-gate: pass — required profile check is fresh for current matched paths
- profile-review:codex-review: fail — required profile review is stale for 2 paths

evidence freshness:
- validation fast-gate: 1 passing run, fresh
  covered current paths: src/foo.py, tests/test_foo.py
- review codex-review: 2 accepted records, stale
  uncovered paths: src/foo.py, tests/test_foo.py
  next: record targeted review with --path for those paths, or rerun codex-review if the change affects broader design

export:
- active HK export files changed after evidence; they do not invalidate validation/review freshness
  check: hk export --format handoff-dir --output .ai/hk/<work-id> --check --target .
```

Without profile-required items, `hk status --target .` should still show generic evidence freshness:

```text
validation:
- fresh for current changed paths
  covered current paths: src/foo.py, tests/test_foo.py

review:
- stale for 1 path
  uncovered paths: src/foo.py
  next: record targeted review for that path, or rerun broad review if the change affects broader design

history:
- validation: 2 passing runs
- review: 1 accepted record
```

This wording should avoid claiming repo-specific validation completeness when no profile exists. Say “validation evidence is fresh for current changed paths,” not “all required validation is complete.”

The output should prioritize:

1. required profile checks/reviews when present;
2. stale/uncovered paths;
3. generic freshness when no profile-specific requirements exist;
4. active export neutrality;
5. repeated broad evidence counts when useful;
6. optional profile suggestions last.

## Architecture seams

### Evidence capture module

Files:

- `src/harness_toolkit/kit/local.py`
- `src/harness_toolkit/kit/ledger/models.py`
- `src/harness_toolkit/kit/ledger/store.py`

Owns recording what a validation command proved: command, result, rationale, changed paths, and path hashes.

### Readiness policy module

Files:

- `src/harness_toolkit/kit/readiness/policy.py`
- `src/harness_toolkit/kit/readiness/diagnostics.py`

Owns binary readiness: pass/fail for lifecycle checks and required profile items. It should not own human CLI prose beyond short messages.

### Closeout diagnostics module

New or existing-home candidate:

- `src/harness_toolkit/kit/readiness/coverage.py`, or
- `src/harness_toolkit/kit/readiness/status.py`

Owns typed freshness/history diagnostics for `hk status`: counts, latest record, fresh/stale, covered paths, uncovered paths, export-neutral notes, and suggested next commands. This keeps the diagnostic interface deep and prevents CLI rendering code from reverse-engineering `ReadyCheck.message` strings.

### CLI rendering module

File:

- `src/harness_toolkit/kit/cli.py`

Owns compact text output only. JSON output should expose the same typed diagnostic objects.

## Implementation plan

### 1. Characterize current behavior first

Add tests around current readiness so the refactor has guardrails:

- required profile check passes only when matching `EvidenceRecord.check_name` has a current exact diff hash;
- required profile review can be satisfied by path-aware review coverage;
- active HK export paths are review-neutral;
- older evidence records without path hashes still work through exact diff hashes.

Prefer focused unit tests for `ready_for_events()` and one CLI/status integration test for JSON shape.

### 2. Extend validation evidence with path hashes

Add to `EvidenceRecord`:

```py
changed_path_hashes: dict[str, str] | None = None
```

Update ledger parsing/writing to keep backward compatibility:

- new evidence records write the field;
- old evidence records load with `None`;
- readiness falls back to exact `diff_hash` when hashes are absent.

In `capture_command()`:

1. run the command;
2. compute coverage after the command finishes so hashes describe the resulting working tree;
3. exclude active HK handoff export paths with existing `active_handoff_export_excludes(work_dir)`;
4. record both `changed_paths` and `changed_path_hashes`.

Rationale: a validation command may format or update files. The evidence should cover the tree state it left behind, not a pre-command snapshot.

### 3. Add validation coverage helpers

In a readiness/coverage seam, add helpers parallel to review coverage:

- normalize current changed paths;
- remove active HK export paths;
- compare path hashes for evidence records;
- return `(covered: bool, uncovered_paths: tuple[str, ...])`;
- support label filtering for profile checks.

Do not generalize into a large framework yet. Reviews and validation are similar enough to share small helpers, but they still have different acceptance rules.

### 4. Update required profile check freshness

For each required profile check:

1. collect passing evidence with matching `check_name`;
2. accept exact current diff hash for old/new records;
3. otherwise accept path coverage for that profile item’s current `matched_paths`;
4. if neither applies, fail with uncovered paths and a targeted next action.

Required labels remain authoritative. A focused test recorded as `--check focused-unit-tests` does not satisfy `profile-check:fast-gate`. The agent must either run/record `fast-gate` or explicitly skip that validation label.

### 5. Keep generic validation useful but non-loophole-y

The generic `validation` readiness check can pass when there is any passing validation with rationale that is exact-current or path-current for all non-generated changed paths.

However, this generic pass does not replace required profile checks. Status should make that visible:

```text
validation: pass — some fresh validation evidence exists
profile-check:fast-gate: fail — required check label not fresh for src/foo.py
```

### 6. Add typed closeout diagnostics to status

Add small dataclasses, names flexible:

```py
@dataclass(frozen=True)
class EvidenceFreshnessItem:
    kind: str                  # validation | review
    label: str                 # check_name, review_name, or general
    total: int
    accepted_or_passing: int
    latest_status: str
    latest_at: str
    fresh: bool
    covered_paths: list[str]
    uncovered_paths: list[str]
    next_action: str = ""

@dataclass(frozen=True)
class ExportFreshnessNote:
    fresh_neutral_paths: list[str]
    check_command: str
    message: str
```

Add to `StatusResult`:

```py
evidence_freshness: list[EvidenceFreshnessItem] | None = None
export_freshness: ExportFreshnessNote | None = None
```

Build these in `local.status()` or a dedicated status/coverage helper. Avoid making `ready_for_events()` return a giant UI object.

Diagnostics should be built in two passes:

1. **Generic pass:** compare all accepted/passing validation and review evidence against current non-generated changed paths. This always works, including no-profile repos.
2. **Profile pass:** for required profile checks/reviews, filter the same evidence by `check_name`/`review_name` and compare against that profile item’s matched paths.

The generic pass can produce useful loop-avoidance guidance, but only the profile pass should claim a named required check/review is satisfied.

### 7. Render diagnostics in default `hk status`

In text output, print a compact `evidence freshness:` section before optional profile suggestions.

Keep it terse:

- show required labels always;
- show stale items always;
- show repeated broad items only when the count is greater than one;
- show optional/focused evidence only when it explains a current pass/fail.

JSON should include full typed diagnostics so agents can parse without scraping messages.

### 8. Add active HK export neutrality note

Compute:

- current changed paths including active export paths;
- current changed paths excluding active export paths;
- active export paths under `.ai/hk/<active-work-id>/`.

When active export paths are present and readiness evidence remains fresh after excluding them, status should print an export note and the exact export check command.

This is built-in HK lifecycle behavior, not profile configuration.

## Test plan

### Unit tests

- `EvidenceRecord` reads old records without `changed_path_hashes`.
- New validation evidence writes `changed_path_hashes` for changed source paths.
- Required profile check accepts path-current evidence for its own label.
- Required profile check rejects stale source edits and reports uncovered paths.
- Required profile check does not accept evidence from a different check label.
- Generic validation can pass while a required profile check fails.
- Active HK export paths do not stale validation/review diagnostics.
- Review diagnostics report counts and stale paths from existing review coverage.

### CLI/status integration tests

- `hk status --json` exposes `evidence_freshness` and `export_freshness`.
- `hk status` text names stale paths and targeted review action.
- `hk status` text includes the active export check command when applicable.
- In a no-profile/generic repo, `hk status` still shows generic evidence freshness and stale paths without requiring custom profile config.

### Repo validation commands

For this repo, use focused tests first:

```bash
uv run pytest -m "not slow" tests/path/to/new_tests.py
```

Final gate:

```bash
mise run check
```

## Dogfood regression scenarios

Promote the targeted dogfood replay into a small scenario set under the repo-local `.agent/skills/hk-pr-sized-dogfood/` skill. Treat these as product regression evals for agent-facing workflow behavior, not as normal pytest unit tests.

The point is to answer:

> Does `hk status` give enough information for a fresh agent to avoid broad validation/review loops and choose a targeted follow-up when appropriate?

Commit scenario definitions, not every raw run. For a meaningful implementation PR, save the run output under `.harness-local/` and attach/export it through HK when useful.

### Scenario directory shape

Add:

```text
.agent/skills/hk-pr-sized-dogfood/scenarios/
  status-freshness-no-profile/
    README.md
    setup.sh
    worker-prompt.md
    expected-observations.md
    collect.sh
  status-freshness-profile-label-authority/
    README.md
    setup.sh
    worker-prompt.md
    expected-observations.md
    collect.sh
```

### Scenario file responsibilities

#### `README.md`

Document the product behavior under test, success signals, and failure signals.

For `status-freshness-no-profile`, success means:

- generic evidence freshness works without `harness.toml`;
- status names stale/uncovered paths;
- status suggests targeted follow-up;
- status does not claim repo-specific required validation passed.

Failure means:

- the worker reruns broad review only because status is unclear;
- the worker thinks no-profile means HK cannot help;
- the worker misses the targeted `--path` follow-up;
- generic wording overclaims readiness.

#### `setup.sh`

Create a deterministic temp repo and HK logging wrapper.

The no-profile setup should:

1. create `/tmp/.../bin/hk` that logs every invocation and delegates to `scripts/hk-dev`;
2. initialize a tiny Python repo with `src/example.py`, `tests/test_example.py`, and `pyproject.toml`;
3. make an initial commit;
4. print the temp root path.

The profile-label setup should do the same, but add a minimal profile/config fixture where `fast-gate` is required for `src/**`.

#### `worker-prompt.md`

Provide the fresh-agent prompt. Keep HK guidance intentionally small so the scenario tests product discoverability.

No-profile prompt shape:

```text
Use the HK CLI at ROOT/bin/hk for this workflow. Begin by exploring the CLI/status guidance enough to use it, but do not follow a pre-written command sequence.

Task:
1. Start HK work for improving normalize_name.
2. Change the implementation and tests.
3. Record validation and review evidence.
4. After review, make one small follow-up source edit.
5. Use hk status to decide whether to rerun broad review or record targeted follow-up.
6. Prefer the narrowest safe follow-up if status gives enough information.
7. Write ROOT/reports/worker-report.md with every HK command you ran, what hk status told you, whether you reran broad review or used targeted follow-up, and what was confusing.
```

#### `expected-observations.md`

Keep a lightweight rubric.

No-profile must observe:

- worker runs `hk status` after the follow-up edit;
- status output names stale/uncovered path(s);
- worker either records targeted review or explains why broad review is safer.

No-profile should observe:

- worker does not require custom profile config;
- worker does not rerun broad review purely because “review stale”;
- worker uses evidence/review history to avoid looping.

#### `collect.sh`

Summarize the run into `ROOT/reports/collection.md`:

- HK commands and exit statuses from `hk-commands.jsonl`;
- final git status/diff stat;
- worker report;
- optional parent notes about whether the run passed the observation rubric.

### Scenario A: no-profile generic usefulness

Create a temporary minimal repo with no `harness.toml` and no custom profile.

1. Start HK work.
2. Change `src/example.py` and `tests/test_example.py`.
3. Record validation with `hk validate --why "Focused tests pass" -- pytest`.
4. Record external review with `hk review add ...` covering the current changed paths.
5. Edit `src/example.py` again.
6. Run `hk status`.

Expected observation:

- status reports validation/review freshness as stale for `src/example.py`;
- status still gives useful targeted follow-up guidance without profile config;
- wording does not claim a named repo-specific required check passed.

### Scenario B: targeted review follow-up closes the loop

Continue from Scenario A.

1. Record targeted review for only `src/example.py` with `hk review add --path src/example.py ...`.
2. Run `hk status` again.

Expected observation:

- review freshness becomes current for all changed paths;
- history shows the broad review plus targeted follow-up count;
- agent sees no reason to rerun the broad review unless broader design changed.

### Scenario C: profile-specific label authority

Create or use a temp repo/profile where `fast-gate` is required for `src/**`.

1. Change `src/example.py`.
2. Record `hk validate --check focused-tests ...` only.
3. Run `hk status`.

Expected observation:

- generic validation can be fresh;
- `profile-check:fast-gate` still fails because the required label was not recorded;
- status suggests running/recording `fast-gate` or explicitly dangerous-skipping that label.

### Dogfood acceptance

- Capture every HK invocation with the dogfood logging wrapper.
- Save a short report under `.harness-local/` or the active HK artifact area describing whether the status output was enough for an agent to choose targeted follow-up instead of rerunning broad review/validation.
- If the agent still loops, treat that as product feedback and revise status wording before expanding the implementation.

### Promotion path

Keep subagent dogfood as the behavior eval. Promote deterministic pieces to pytest only after the product wording and JSON shape stabilize:

- evidence path hashes recorded;
- status JSON includes stale paths;
- active export neutral note appears;
- label authority works.

## MVP boundary

Implement now:

1. validation path hashes;
2. generic freshness diagnostics that work without profile config;
3. path-aware required profile check freshness;
4. typed `hk status` evidence freshness diagnostics;
5. active HK export neutrality note;
6. focused tests plus one targeted dogfood replay for no-profile and targeted-review behavior.

Defer:

- `hk validate --path ...` targeted validation coverage;
- policy knobs for rerun behavior;
- max-turn or max-review enforcement;
- broader profile schema changes.

## Re-grade criteria

- **A** when `hk status` explains stale validation/review paths and active export neutrality without new profile config, and required check labels remain authoritative.
- **A+** when diagnostics are typed, compact in default text output, covered by focused tests, and old ledgers remain backward-compatible.

## Decisions and spec reflection
- Make hk status derive freshness from validation/review path coverage while keeping profile labels authoritative and profile config unchanged.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, docs/reference/decisions/0011-path-aware-review-freshness.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m 'not slow' tests/unit/test_hk2_readiness_policy.py tests/unit/test_hk2_ledger_events.py tests/unit/test_portable_workflow.py -q`: pass (exit 0) — validates: Focused HK freshness tests pass — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Docs and scenario contracts still pass — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Final fast gate passes for status freshness implementation — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final fast gate passes for status freshness implementation — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final fast gate passes after review fixes — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final fast gate passes after targeted review fixes — `<local HK state not exported>`
- `bash -lc 'root=$(.agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-no-profile/setup.sh /tmp/hk-dogfood-validate-no-profile); (cd "$root/repo" && "$root/bin/hk" status --target . --json >/tmp/hk-dogfood-validate-status.json); root2=$(.agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-profile-label-authority/setup.sh /tmp/hk-dogfood-validate-profile); (cd "$root2/repo" && "$root2/bin/hk" checks --target . --changed --json >/tmp/hk-dogfood-validate-checks.json)'`: pass (exit 0) — validates: Dogfood scenario setup wrappers and hk status smoke pass — `<local HK state not exported>`
- `uv run pytest -m 'not slow' tests/unit/test_portable_workflow.py::test_status_reports_active_export_neutrality -q`: pass (exit 0) — validates: Focused export freshness message test passes after Codex fixes — `<local HK state not exported>`
- `bash -lc 'root=$(.agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-no-profile/setup.sh /tmp/hk-dogfood-validate-no-profile-2); (cd "$root/repo" && "$root/bin/hk" status --target . --json >/tmp/hk-dogfood-validate-status-2.json)'`: pass (exit 0) — validates: Dogfood smoke passes after Codex export-message fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final fast gate passes after Codex export-message fix — `<local HK state not exported>`
- `uv run pytest -m 'not slow' tests/unit/test_portable_workflow.py::test_status_reports_generic_stale_paths_without_profile -q`: pass (exit 0) — validates: Focused path decision hint test passes — `<local HK state not exported>`
- `bash -lc 'root=$(.agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-no-profile/setup.sh /tmp/hk-dogfood-validate-no-profile-3); (cd "$root/repo" && "$root/bin/hk" status --target . --json >/tmp/hk-dogfood-validate-status-3.json)'`: pass (exit 0) — validates: Dogfood smoke passes after local-only hint refinement — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final fast gate passes after local-only hint refinement — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/reference/decisions/0011-path-aware-review-freshness.md)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/ledger/models.py, src/harness_toolkit/kit/ledger/store.py, +3 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-no-profile/README.md, .agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-profile-label-authority/README.md, SPEC.md, +9 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched SPEC.md, docs/reference/decisions/0011-path-aware-review-freshness.md, src/harness_toolkit/kit/cli.py, +7 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/ledger/models.py, src/harness_toolkit/kit/ledger/store.py, +3 more)

## Review
- subagent / reviewer-fresh-context [codex-review]: Fresh-context review found no blockers after targeted fixes; earlier blockers around dangerous skips, sync exclusions, copy-paste commands, and latest_status were addressed. paths: SPEC.md, docs/reference/decisions/0011-path-aware-review-freshness.md, src/harness_toolkit/kit/cli.py, +17 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Focused HK lifecycle review found no blockers after targeted fixes; confirmed label authority, sync-exclude filtering, generic/profile distinction, and portable dogfood scripts. paths: SPEC.md, docs/reference/decisions/0011-path-aware-review-freshness.md, src/harness_toolkit/kit/cli.py, +17 more. [accepted]
- codex / codex-exec [codex-review]: Codex review blockers addressed: narrowed export freshness wording and captured generated-file dogfood observation; HK export was regenerated and export check passed. paths: src/harness_toolkit/kit/readiness/status.py, .agent/skills/hk-pr-sized-dogfood/scenarios/status-freshness-no-profile/expected-observations.md. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Targeted lifecycle follow-up accepted export freshness wording change; no blockers. paths: src/harness_toolkit/kit/readiness/status.py. [accepted]
- codex / codex-exec [codex-review]: Targeted follow-up: local-only path decision hint now uses a PATH placeholder so agents choose only paths they judge local-only, rather than excluding all uncovered paths. paths: src/harness_toolkit/kit/readiness/status.py, tests/unit/test_portable_workflow.py. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Targeted lifecycle follow-up accepted local-only path decision hint refinement; no blockers. paths: src/harness_toolkit/kit/readiness/status.py. [accepted]
- codex / codex-exec [codex-review]: Targeted follow-up accepted path-decision status rendering and scenario prompt/rubric updates; no blockers. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/readiness/status.py, tests/unit/test_portable_workflow.py, +2 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Targeted lifecycle follow-up accepted path-decision status rendering and freshness hint changes; no blockers. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/readiness/status.py. [accepted]

## Attached artifacts
- dogfood-report: `artifacts/artifact_6_dogfood-report_artifact_20260603_140326_323032_dogfood-report_collection.md` (copied, redaction=unknown, 8711 bytes, sha256:1442b5bf8930) — status freshness no-profile dogfood collection
