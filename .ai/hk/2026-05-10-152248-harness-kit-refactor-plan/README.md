# HK export: `2026-05-10-152248-harness-kit-refactor-plan`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-10-152248-harness-kit-refactor-plan --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-10-152248-harness-kit-refactor-plan`
- Branch: `hk-safe-refactor`
- Git SHA: `d70a0aa`
- Dirty: `true`
- Sync status: `synced`

## Context
- Interview decisions: hybrid refactor with isolated semantic-fix chunks; JSON stable/text smoke-tested; gates include fast unit, lifecycle integration, CLI smoke, dogfood, and mise run check; artifact location is generated .ai/hk export.
- User correction incorporated: use agent_sim/workflow_sim for scripted fake-agent tests and reserve dogfood for real HK dogfooding/replay; do not overbuild long-term backwards compatibility for new internals; apply TDD-style sequencing throughout; run agent-friendly CLI design review for CLI-facing changes; update HK profile path matchers after refactors and consider repo-owned profiles.

## Plan
- Create a safe TDD refactor plan for Harness Kit architecture, conformance tests, and simulated dogfood runs.
- # Harness Kit safe TDD refactor plan

## Purpose

Refactor Harness Kit from a working lifecycle prototype into a deeper, safer product implementation without breaking existing agent workflows. The work should move behavior out of `src/harness_toolkit/kit/local.py` and the large Cyclopts adapter into deeper product seams while preserving public CLI behavior, JSON contracts, ledger/export compatibility, and scaffold compatibility.

## Planning decisions

- Scope: hybrid. Structural refactors are no-behavior-change by default; semantic safety changes land only in isolated TDD chunks with explicit failing tests.
- Compatibility: public JSON, exit codes, ledger JSONL, evidence JSONL, and generated export file formats are stable. Human text is smoke-tested for key phrases/examples but may improve.
- Required gates: fast pure unit suite, lifecycle integration suite, black-box CLI smoke suite, simulated dogfood agent runs, and `mise run check` before handoff.
- Required dogfood scenarios: happy-path code change, profile-required changed path, mistake recovery / agent UX, local agent-state churn, failed validation/review path, exported handoff freshness.
- Major seam order: conformance/dogfood first, then Git/sync, typed events plus validation/review freshness contract, evidence, export, profiles, and finally LifecycleApp/CLI cleanup.
- Done means: `local.py` no longer owns most lifecycle behavior; CLI primarily delegates to `LifecycleApp`; sync exclusions and validation/review freshness are fixed; command capture has timeout/truncation/process cleanup; dogfood agents pass; test marker taxonomy is cleaned up; docs/spec/ADR reflect changed semantics.

## Non-negotiable safety rules

1. Do not mix mechanical extraction and behavior-changing semantics in the same slice.
2. Every behavior-changing safety fix starts with a failing test that describes the desired product behavior.
3. Keep compatibility wrappers until the corresponding public-CLI dogfood scenarios pass.
4. Prefer additive JSON changes; no public JSON/file-format breaking changes without an explicit decision and migration note.
5. Preserve shell-first validation: no `hk run` task runner, no automatic command selection, no readiness scoring.
6. Keep each implementation slice PR-sized and independently shippable.
7. Simulated dogfood journeys must use public `hk` CLI commands, except for fixture setup helpers.

## Phase 0 — Baseline characterization and conformance harness

Goal: make current product behavior observable before moving code.

### 0A. Test taxonomy and commands

Add and apply markers for:

- `unit`: pure, fast, no subprocess Git/uv where possible.
- `integration`: real temp Git repos and LifecycleApp/local state flows.
- `cli`: public black-box `uv run hk ...` entrypoint coverage.
- `dogfood`: scripted fake-agent journeys through public CLI commands.
- `e2e`: generated repo / scaffold workflows.
- `slow`: toolchain-heavy or long-running checks.

Reclassify existing tests instead of only registering marker names. For example, tests that initialize Git repos or run `uv run hk` should not remain marked as pure unit just because they live under `tests/unit/`.

Suggested commands:

- `uv run pytest -m unit`
- `uv run pytest -m "integration or cli"`
- `uv run pytest -m dogfood`
- `mise run check` as the full final gate.

Acceptance criteria:

- Marker descriptions match actual behavior.
- Fast unit suite is meaningfully fast and does not include black-box CLI subprocess tests.
- Existing `mise run check` remains green.

### 0B. Public CLI smoke coverage

Add black-box CLI smoke tests for stable JSON fields, exit codes, and key human text phrases/examples. Cover at least:

- `hk brief --json`
- `hk start --plan --json`
- `hk context --json`
- `hk decide --spec-impact ... --json`
- `hk status --json`
- `hk validate --why ... -- <command>`
- `hk review prompt`
- `hk review add ... --json`
- `hk artifact attach ... --json`
- `hk sync --check --json`
- `hk dangerously-skip ... --json`
- `hk ready --json`
- `hk summary`
- `hk handoff`
- `hk checks --changed --json`
- `hk profile resolve --json`
- `hk export --format handoff-dir --check --json`

JSON assertions should check stable fields and allowed additive fields. Human text assertions should check key repair hints, examples, and scary dangerous-skip language rather than full paragraphs.

### 0C. Backward-compatibility fixtures

Add fixture tests for old persisted formats before adding new fields:

- old `events.jsonl`
- old `evidence.jsonl`
- old review events without diff coverage metadata
- old dangerous skip events without diff/event boundary metadata
- old `meta.json` handoff-dir export metadata

Decide and encode legacy behavior:

- preferred default: legacy validation/review evidence is accepted for existing ledgers but reported as freshness-unknown with actionable revalidation guidance; newly created evidence/review after this refactor records freshness metadata.
- if the product chooses stricter semantics, document the breaking behavior explicitly before implementation.

### 0D. Dogfood harness skeleton

Create a fixture harness for scripted fake-agent journeys in tiny temp Git repos. Dogfood journeys must call the public CLI for all HK interactions. Setup helpers may create fixture repos, profiles, and files directly.

Acceptance criteria:

- Dogfood tests can run independently.
- Dogfood failures print the command transcript / JSON payload that failed.
- The minimal happy-path journey passes before structural extraction begins.

## Phase 1 — Git snapshot and sync freshness module

Goal: extract Git and freshness behavior from `local.py` into a deep module that owns repo facts, changed paths, diff hashes, sync exclusions, and agent-local state warnings.

Proposed modules:

- `src/harness_toolkit/kit/git/snapshot.py`
- `src/harness_toolkit/kit/sync/freshness.py`

### TDD-first semantic fix: sync exclusion revalidation

Add failing public-CLI dogfood/integration tests before implementation:

- Given `hk sync --exclude .pi --reason agent-local`, when `.pi/session.json` changes, then `hk sync --check` reports stale.
- Given an excluded directory gets a new file, `hk sync --check` reports stale.
- Given an excluded path becomes tracked/staged, `hk sync --check` reports stale with a repair message.

Implementation:

- Store recursive metadata/content hashes for excluded untracked files/directories.
- Compare stored excluded metadata during sync checks.
- Keep excludes literal/path-safe and local-only.

### No-behavior-change extraction

Move behind wrappers:

- `git_sha`
- `git_dirty`
- changed path discovery
- diff hashing
- untracked hashing
- pathspec excludes
- sync exclude safety checks
- agent-local state warnings

Acceptance criteria:

- Existing sync/profile changed-path tests pass.
- New excluded-path-content-change tests pass.
- Local agent-state churn dogfood scenario passes.
- `local.py` wrappers still preserve old import paths.

## Phase 2 — Typed lifecycle events and freshness contract foundation

Goal: stop leaking raw event dictionaries throughout readiness, rendering, review prompts, export, and status, while preparing additive freshness metadata for evidence/review semantics.

Proposed module:

- `src/harness_toolkit/kit/ledger/lifecycle_events.py`

Implementation shape:

- Keep JSONL storage format stable.
- Add typed event constructors and parsed event/query helpers for:
  - work started
  - note added by kind
  - command captured
  - review added
  - artifact attached
  - sync checkpoint
  - dangerous skip
- Add compatibility parsing for old events missing newly introduced optional fields.
- Add query helpers for validation/review coverage state, even before enforcement is fully enabled.

Acceptance criteria:

- Existing malformed JSONL tests still pass.
- Old ledger fixtures parse successfully.
- Readiness and handoff rendering no longer need to know raw event payload keys except inside the event module.

## Phase 3 — Validation/review diff freshness semantics

Goal: ensure `hk ready` cannot accidentally bless validation or review evidence that covered an older diff.

This phase intentionally happens before the broad evidence/export/profile/LifecycleApp refactors so later seams are built around the correct readiness contract.

### TDD-first tests

Add failing tests for:

- validate, mutate code, sync, ready should fail or warn until revalidated or dangerously skipped.
- review, mutate code, sync, ready should fail or warn until rereviewed or dangerously skipped.
- named profile checks/reviews must cover the current matching changed paths.
- legacy validation/review records without freshness metadata produce the chosen legacy behavior from Phase 0C.
- dangerous validation/review skips are diff/event scoped, or explicitly rendered as not diff-scoped if that is the chosen product behavior.

### Implementation

Record additive fields on new evidence/review events:

- diff hash
- changed paths
- event sequence or coverage boundary
- target scope

Update readiness policy to require current diff coverage for validation and review unless an explicit dangerous skip covers the current state.

Acceptance criteria:

- Current diff must be covered by latest accepted validation/review or explicit dangerous skip.
- Handoff clearly renders freshness state and any dangerous skips.
- Happy-path and failed validation/review dogfood scenarios pass.

## Phase 4 — Evidence capture module and command hardening

Goal: make exact command evidence a deep module instead of behavior split across `local.capture_command`, process adapter, redaction, transcripts, Git facts, and ledger writes.

Proposed module:

- `src/harness_toolkit/kit/evidence/capture.py`

### Public contract before implementation

Define the command-capture contract before writing tests:

- CLI flags: decide whether to add `--timeout-seconds` and `--max-log-bytes`, or use config/env defaults first.
- Defaults: choose conservative defaults that do not break normal long-running checks unexpectedly.
- Timeout result: define exit code, evidence `status`, `timed_out: true`, transcript marker, and whether timeout evidence can satisfy readiness.
- Truncation result: define `truncated: true`, `transcript_bytes`, deterministic marker text, and interaction with `--no-log` / `--raw-log`.
- Process cleanup: define process-group behavior for argv and shell mode.
- Backward compatibility: old evidence records without timeout/truncation fields parse normally.

### TDD-first hardening tests

- command times out and child process is cleaned up.
- shell mode timeout cleans up child process.
- transcript truncates after max bytes with marker.
- `--no-log` still avoids transcript contents.
- `--raw-log` disables redaction but not truncation/timeout metadata.

### No-behavior-change extraction

Move into evidence module:

- command validation
- command display redaction
- transcript path selection
- dirty-before/after and diff coverage snapshotting
- evidence JSONL writing
- `command_captured` event creation
- profile check-name validation hook via ProfileContext once available

Acceptance criteria:

- Existing capture/redaction tests pass.
- New hang/timeout and large-output tests pass.
- Failed validation dogfood scenario passes.

## Phase 5 — Handoff rendering and export package module

Goal: make handoff/export a deep package module that owns generated views, handoff-dir metadata, file hashes, stale checks, and safe file writes.

Proposed modules:

- `src/harness_toolkit/kit/handoff/render.py`
- `src/harness_toolkit/kit/handoff/export.py`

### TDD-first safety tests

Add public-CLI and module tests for:

- symlinked generated file such as `README.md` or `meta.json` is rejected or safely replaced without following the symlink.
- symlinked `artifacts/` directory remains safely handled.
- output directory symlink behavior is explicit and safe.
- missing generated file is caught by `hk export --check`.
- modified generated file is caught by `hk export --check`.
- stale ledger/diff metadata is caught by `hk export --check`.

### No-behavior-change extraction

Move out of `local.py`:

- `render_handoff`
- `summary`
- `handoff`
- `materialize_work`
- export helper functions
- `export_handoff_dir`

Acceptance criteria:

- Existing rendering/export tests pass.
- Exported handoff freshness dogfood scenario passes.
- `hk export --format handoff-dir --check` stays stable for generated `.ai/hk` packages.

## Phase 6 — ProfileContext module

Goal: make profile behavior target-specific and centralized without turning HK into a command selector.

Proposed module:

- `src/harness_toolkit/kit/profiles/context.py`

Responsibilities:

- Resolve profile for target.
- Validate check/review names.
- Produce changed-path suggestions.
- Produce required profile checks/reviews for readiness.
- Produce structured JSON fields for agents in addition to existing command snippets.

Dogfood requirement:

- Complete the profile-required changed path dogfood scenario before or during this phase, not at the end of the program.

Acceptance criteria:

- Profile guidance remains advisory.
- Required profile checks/reviews still enforce readiness only when configured rules match.
- Existing profile tests are promoted/reused where possible instead of duplicating coverage blindly.

## Phase 7 — LifecycleApp becomes the product seam

Goal: make `LifecycleApp` the main Harness Kit lifecycle module rather than a pass-through facade.

Work:

- Move CLI command bodies toward parse → request dataclass → `LifecycleApp` → print.
- Reduce direct `local.py` imports from `cli.py`.
- Migrate product behavior tests from direct `local.py` calls to `LifecycleApp` or public CLI dogfood scenarios.
- Keep low-level module tests for Git/sync, evidence, ledger events, profile context, and handoff export.
- Leave compatibility wrappers in `local.py` until all required dogfood scenarios pass.

Acceptance criteria:

- CLI primarily delegates to `LifecycleApp`.
- Product lifecycle tests read as scenarios, not storage implementation probes.
- No public JSON/file-format breakage.

## Phase 8 — Compatibility wrapper deletion and cleanup

Goal: remove old seams only after tests and dogfood prove the new modules.

Work:

- Delete or shrink obsolete `local.py` functions after call sites migrate.
- Remove duplicate status/rendering/profile helper paths.
- Clean imports and dead modules.
- Update docs/spec/ADR for changed semantics and new architecture.

Acceptance criteria:

- `local.py` no longer owns most lifecycle behavior.
- CLI primarily delegates to `LifecycleApp`.
- All selected dogfood scenarios pass.
- `mise run check` passes.
- `mise run sync-check` passes for generated HK exports when applicable.

## Simulated dogfood suite design

Implement dogfood tests as scripted fake-agent journeys against tiny temp Git repos. They should use public CLI commands for HK interactions and assert lifecycle state, JSON shape, exit codes, and agent-facing recoverability.

Required scenarios and phase gates:

1. Happy-path code change — create in Phase 0D and keep green throughout.
   - start work
   - record plan/context/decision
   - edit fixture file
   - validate with passing native command
   - record external-enough review
   - sync
   - ready/summary/handoff

2. Local agent-state churn — complete before/with Phase 1.
   - create `.pi` or equivalent local-only state
   - sync with exclusion
   - mutate excluded content
   - assert sync check stales under new semantics

3. Failed validation/review path — complete before/with Phase 3/4.
   - capture failing command
   - record rejected/blocking review
   - assert ready remains not-ready until fixed or dangerously skipped

4. Exported handoff freshness — complete before/with Phase 5.
   - export `.ai/hk/<work-id>/`
   - check export freshness
   - mutate ledger/diff/generated file
   - assert export check catches staleness or generated-file modification

5. Profile-required changed path — complete before/with Phase 6.
   - configure profile rules
   - edit matching path
   - assert ready fails until named `hk validate --check` and named review are recorded

6. Mistake recovery / agent UX — keep green across all CLI-affecting phases.
   - pass `--profile` to lifecycle command
   - omit plan or review
   - assert status/help gives actionable repair hints

## Validation ladder per slice

For each implementation slice:

1. Run focused new tests first.
2. Run related existing unit/integration tests.
3. Run CLI smoke/dogfood tests affected by the seam.
4. Run `mise run check` before handoff.
5. For slices that touch exported HK state or plan artifacts, run `mise run sync-check`.
6. Record validation with `hk validate --why ...` when dogfooding in this repo.

## Revised slice outline

1. Register and apply test marker taxonomy; separate pure unit from integration/CLI.
2. Add public CLI smoke tests for current lifecycle commands and negative states.
3. Add backward-compat fixtures for old ledgers/evidence/reviews/exports.
4. Add minimal public-CLI dogfood harness and happy-path scenario.
5. Extract Git snapshot/sync modules with wrappers.
6. Add sync exclusion content revalidation semantic fix plus local-state dogfood.
7. Add typed lifecycle event query module and migrate readiness/rendering queries incrementally.
8. Add validation/review freshness metadata and readiness semantics.
9. Extract evidence capture module.
10. Add command timeout/truncation/process cleanup contract and implementation.
11. Extract handoff/export module and safe export file writes.
12. Extract ProfileContext and structured profile suggestion JSON.
13. Migrate CLI/product behavior to LifecycleApp as the primary seam.
14. Run full dogfood suite, then delete compatibility wrappers and shrink `local.py`.
15. Update docs/spec/ADR, run full validation, and export final HK handoff.

## Risks and mitigations

- Risk: test churn from direct `local.py` imports. Mitigation: keep wrappers, migrate tests gradually to product seams.
- Risk: semantic fixes break existing dogfood habits. Mitigation: isolate behavior changes, update docs/status guidance, and make failure messages actionable.
- Risk: legacy ledgers become ambiguous. Mitigation: add explicit backward-compat fixture behavior before introducing new fields.
- Risk: CLI text snapshot brittleness. Mitigation: stable JSON snapshots plus key-phrase text smoke tests.
- Risk: dogfood suite becomes slow. Mitigation: keep dogfood fixture repos tiny and separate from generated scaffold e2e.
- Risk: diff freshness semantics become too strict for docs-only or planning work. Mitigation: allow explicit dangerous skip with precise rendering, or classify evidence scope by changed paths.
- Risk: command timeout defaults break legitimate long validations. Mitigation: choose conservative defaults, support overrides, and document behavior before enabling readiness enforcement.
- # Harness Kit safe TDD refactor plan

## Purpose

Refactor Harness Kit from a working lifecycle prototype into a deeper, safer product implementation without breaking existing agent workflows. The work should move behavior out of `src/harness_toolkit/kit/local.py` and the large Cyclopts adapter into deeper product seams while preserving public CLI behavior, JSON contracts, ledger/export compatibility, and scaffold compatibility.

## Planning decisions

- Scope: hybrid. Structural refactors are no-behavior-change by default; semantic safety changes land only in isolated TDD chunks with explicit failing tests.
- Compatibility: public JSON, exit codes, ledger JSONL, evidence JSONL, and generated export file formats are stable. Human text is smoke-tested for key phrases/examples but may improve.
- Required gates: fast pure unit suite, lifecycle integration suite, black-box CLI smoke suite, scripted agent-simulation tests, real HK dogfood/replay where appropriate, and `mise run check` before handoff.
- Required scripted agent-simulation scenarios: happy-path code change, profile-required changed path, mistake recovery / agent UX, local agent-state churn, failed validation/review path, exported handoff freshness. Reserve “dogfood” for real Harness Kit dogfooding through the repo-local harness/skill workflow.
- Major seam order: conformance/agent-simulation first, then Git/sync, typed events plus validation/review freshness contract, evidence, export, profiles, and finally LifecycleApp/CLI cleanup.
- Done means: `local.py` no longer owns most lifecycle behavior; CLI primarily delegates to `LifecycleApp`; sync exclusions and validation/review freshness are fixed; command capture has timeout/truncation/process cleanup; agent-simulation scenarios and selected real dogfood/replay checks pass; test marker taxonomy is cleaned up; docs/spec/ADR reflect changed semantics.

## Non-negotiable safety rules

1. Do not mix mechanical extraction and behavior-changing semantics in the same slice.
2. Every behavior-changing safety fix starts with a failing test that describes the desired product behavior.
3. Keep compatibility wrappers until the corresponding public-CLI agent-simulation scenarios pass.
4. Prefer additive JSON changes; no public JSON/file-format breaking changes without an explicit decision and migration note.
5. Preserve shell-first validation: no `hk run` task runner, no automatic command selection, no readiness scoring.
6. Keep each implementation slice PR-sized and independently shippable.
7. Scripted agent-simulation journeys must use public `hk` CLI commands, except for fixture setup helpers. Reserve `dogfood` for real HK dogfooding/replay runs.
8. Use TDD-style sequencing throughout: characterize existing behavior before mechanical extraction and write failing tests before semantic changes.
9. Do not overbuild long-term backward compatibility for short-lived pre-refactor internals; temporary wrappers are for safe migration only.

## Phase 0 — Baseline characterization and conformance harness

Goal: make current product behavior observable before moving code.

### 0A. Test taxonomy and commands

Add and apply markers for:

- `unit`: pure, fast, no subprocess Git/uv where possible.
- `integration`: real temp Git repos and LifecycleApp/local state flows.
- `cli`: public black-box `uv run hk ...` entrypoint coverage.
- `agent_sim` or `workflow_sim`: scripted fake-agent journeys through public CLI commands. Do not call this marker `dogfood`; dogfood means real HK use/replay.
- `e2e`: generated repo / scaffold workflows.
- `slow`: toolchain-heavy or long-running checks.

Reclassify existing tests instead of only registering marker names. For example, tests that initialize Git repos or run `uv run hk` should not remain marked as pure unit just because they live under `tests/unit/`.

Suggested commands:

- `uv run pytest -m unit`
- `uv run pytest -m "integration or cli"`
- `uv run pytest -m agent_sim` (or the chosen simulation marker)
- `mise run check` as the full final gate.

Acceptance criteria:

- Marker descriptions match actual behavior.
- Fast unit suite is meaningfully fast and does not include black-box CLI subprocess tests.
- Existing `mise run check` remains green.

### 0B. Public CLI smoke coverage

Add black-box CLI smoke tests for stable JSON fields, exit codes, and key human text phrases/examples. Cover at least:

- `hk brief --json`
- `hk start --plan --json`
- `hk context --json`
- `hk decide --spec-impact ... --json`
- `hk status --json`
- `hk validate --why ... -- <command>`
- `hk review prompt`
- `hk review add ... --json`
- `hk artifact attach ... --json`
- `hk sync --check --json`
- `hk dangerously-skip ... --json`
- `hk ready --json`
- `hk summary`
- `hk handoff`
- `hk checks --changed --json`
- `hk profile resolve --json`
- `hk export --format handoff-dir --check --json`

JSON assertions should check stable fields and allowed additive fields. Human text assertions should check key repair hints, examples, and scary dangerous-skip language rather than full paragraphs.

### 0C. Compatibility stance and current-format characterization

Do not build long-term compatibility for short-lived pre-refactor internals. This tool is new enough that preserving every one-day-old local ledger shape is not worth extra architecture or test burden. Instead:

- Characterize the current public CLI JSON/file formats that must stay stable during the refactor.
- Keep temporary wrappers while moving call sites.
- Add migration/compatibility code only when it protects active in-repo work during the refactor.
- Remove temporary compatibility paths before merge if the final design no longer needs them.

Acceptance criteria:

- The plan distinguishes public compatibility from internal prototype compatibility.
- No phase adds permanent legacy machinery just to preserve short-lived pre-refactor internals.

### 0D. Agent-simulation harness skeleton

Create a fixture harness for scripted fake-agent journeys in tiny temp Git repos. These are simulation tests, not the repo-local HK dogfood/replay skill. Agent-simulation journeys must call the public CLI for all HK interactions. Setup helpers may create fixture repos, profiles, and files directly.

Acceptance criteria:

- Agent-simulation tests can run independently.
- Failures print the command transcript / JSON payload that failed.
- The minimal happy-path journey passes before structural extraction begins.

## Phase 1 — Git snapshot and sync freshness module

Goal: extract Git and freshness behavior from `local.py` into a deep module that owns repo facts, changed paths, diff hashes, sync exclusions, and agent-local state warnings.

Proposed modules:

- `src/harness_toolkit/kit/git/snapshot.py`
- `src/harness_toolkit/kit/sync/freshness.py`

### TDD-first semantic fix: sync exclusion revalidation

Add failing public-CLI agent-simulation/integration tests before implementation:

- Given `hk sync --exclude .pi --reason agent-local`, when `.pi/session.json` changes, then `hk sync --check` reports stale.
- Given an excluded directory gets a new file, `hk sync --check` reports stale.
- Given an excluded path becomes tracked/staged, `hk sync --check` reports stale with a repair message.

Implementation:

- Store recursive metadata/content hashes for excluded untracked files/directories.
- Compare stored excluded metadata during sync checks.
- Keep excludes literal/path-safe and local-only.

### No-behavior-change extraction

Move behind wrappers:

- `git_sha`
- `git_dirty`
- changed path discovery
- diff hashing
- untracked hashing
- pathspec excludes
- sync exclude safety checks
- agent-local state warnings

Acceptance criteria:

- Existing sync/profile changed-path tests pass.
- New excluded-path-content-change tests pass.
- Local agent-state churn agent-simulation scenario passes.
- `local.py` wrappers still preserve old import paths.

## Phase 2 — Typed lifecycle events and freshness contract foundation

Goal: stop leaking raw event dictionaries throughout readiness, rendering, review prompts, export, and status, while preparing additive freshness metadata for evidence/review semantics.

Proposed module:

- `src/harness_toolkit/kit/ledger/lifecycle_events.py`

Implementation shape:

- Keep JSONL storage format stable.
- Add typed event constructors and parsed event/query helpers for:
  - work started
  - note added by kind
  - command captured
  - review added
  - artifact attached
  - sync checkpoint
  - dangerous skip
- Add temporary/default handling only where needed for active in-refactor events missing newly introduced optional fields.
- Add query helpers for validation/review coverage state, even before enforcement is fully enabled.

Acceptance criteria:

- Existing malformed JSONL tests still pass.
- Old ledger fixtures parse successfully.
- Readiness and handoff rendering no longer need to know raw event payload keys except inside the event module.

## Phase 3 — Validation/review diff freshness semantics

Goal: ensure `hk ready` cannot accidentally bless validation or review evidence that covered an older diff.

This phase intentionally happens before the broad evidence/export/profile/LifecycleApp refactors so later seams are built around the correct readiness contract.

### TDD-first tests

Add failing tests for:

- validate, mutate code, sync, ready should fail or warn until revalidated or dangerously skipped.
- review, mutate code, sync, ready should fail or warn until rereviewed or dangerously skipped.
- named profile checks/reviews must cover the current matching changed paths.
- records created before the freshness change follow the explicit compatibility stance from Phase 0C; do not add permanent legacy machinery unless needed for active in-repo work.
- dangerous validation/review skips are diff/event scoped, or explicitly rendered as not diff-scoped if that is the chosen product behavior.

### Implementation

Record additive fields on new evidence/review events:

- diff hash
- changed paths
- event sequence or coverage boundary
- target scope

Update readiness policy to require current diff coverage for validation and review unless an explicit dangerous skip covers the current state.

Acceptance criteria:

- Current diff must be covered by latest accepted validation/review or explicit dangerous skip.
- Handoff clearly renders freshness state and any dangerous skips.
- Happy-path and failed validation/review agent-simulation scenarios pass.

## Phase 4 — Evidence capture module and command hardening

Goal: make exact command evidence a deep module instead of behavior split across `local.capture_command`, process adapter, redaction, transcripts, Git facts, and ledger writes.

Proposed module:

- `src/harness_toolkit/kit/evidence/capture.py`

### Public contract before implementation

Define the command-capture contract before writing tests:

- CLI flags: decide whether to add `--timeout-seconds` and `--max-log-bytes`, or use config/env defaults first.
- Defaults: choose conservative defaults that do not break normal long-running checks unexpectedly.
- Timeout result: define exit code, evidence `status`, `timed_out: true`, transcript marker, and whether timeout evidence can satisfy readiness.
- Truncation result: define `truncated: true`, `transcript_bytes`, deterministic marker text, and interaction with `--no-log` / `--raw-log`.
- Process cleanup: define process-group behavior for argv and shell mode.
- Compatibility stance: additive fields are okay, but do not preserve unused prototype-only evidence formats beyond the refactor unless active work requires it.

### TDD-first hardening tests

- command times out and child process is cleaned up.
- shell mode timeout cleans up child process.
- transcript truncates after max bytes with marker.
- `--no-log` still avoids transcript contents.
- `--raw-log` disables redaction but not truncation/timeout metadata.

### No-behavior-change extraction

Move into evidence module:

- command validation
- command display redaction
- transcript path selection
- dirty-before/after and diff coverage snapshotting
- evidence JSONL writing
- `command_captured` event creation
- profile check-name validation hook via ProfileContext once available

Acceptance criteria:

- Existing capture/redaction tests pass.
- New hang/timeout and large-output tests pass.
- Failed validation agent-simulation scenario passes.

## Phase 5 — Handoff rendering and export package module

Goal: make handoff/export a deep package module that owns generated views, handoff-dir metadata, file hashes, stale checks, and safe file writes.

Proposed modules:

- `src/harness_toolkit/kit/handoff/render.py`
- `src/harness_toolkit/kit/handoff/export.py`

### TDD-first safety tests

Add public-CLI and module tests for:

- symlinked generated file such as `README.md` or `meta.json` is rejected or safely replaced without following the symlink.
- symlinked `artifacts/` directory remains safely handled.
- output directory symlink behavior is explicit and safe.
- missing generated file is caught by `hk export --check`.
- modified generated file is caught by `hk export --check`.
- stale ledger/diff metadata is caught by `hk export --check`.

### No-behavior-change extraction

Move out of `local.py`:

- `render_handoff`
- `summary`
- `handoff`
- `materialize_work`
- export helper functions
- `export_handoff_dir`

Acceptance criteria:

- Existing rendering/export tests pass.
- Exported handoff freshness agent-simulation scenario passes.
- `hk export --format handoff-dir --check` stays stable for generated `.ai/hk` packages.

## Phase 6 — ProfileContext module

Goal: make profile behavior target-specific and centralized without turning HK into a command selector.

Proposed module:

- `src/harness_toolkit/kit/profiles/context.py`

Responsibilities:

- Resolve profile for target.
- Validate check/review names.
- Produce changed-path suggestions.
- Produce required profile checks/reviews for readiness.
- Produce structured JSON fields for agents in addition to existing command snippets.

Agent-simulation requirement:

- Complete the profile-required changed path agent-simulation scenario before or during this phase, not at the end of the program.

Acceptance criteria:

- Profile guidance remains advisory.
- Required profile checks/reviews still enforce readiness only when configured rules match.
- Existing profile tests are promoted/reused where possible instead of duplicating coverage blindly.

## Phase 7 — LifecycleApp becomes the product seam

Goal: make `LifecycleApp` the main Harness Kit lifecycle module rather than a pass-through facade.

Work:

- Move CLI command bodies toward parse → request dataclass → `LifecycleApp` → print.
- Reduce direct `local.py` imports from `cli.py`.
- Migrate product behavior tests from direct `local.py` calls to `LifecycleApp` or public CLI agent-simulation scenarios.
- Keep low-level module tests for Git/sync, evidence, ledger events, profile context, and handoff export.
- Leave compatibility wrappers in `local.py` until all required agent-simulation scenarios and any selected real dogfood/replay checks pass.

Acceptance criteria:

- CLI primarily delegates to `LifecycleApp`.
- Product lifecycle tests read as scenarios, not storage implementation probes.
- No public JSON/file-format breakage.

## Phase 8 — Compatibility wrapper deletion and cleanup

Goal: remove old seams only after tests, agent simulations, and selected real dogfood/replay checks prove the new modules.

Work:

- Delete or shrink obsolete `local.py` functions after call sites migrate.
- Remove duplicate status/rendering/profile helper paths.
- Clean imports and dead modules.
- Update docs/spec/ADR for changed semantics and new architecture.

Acceptance criteria:

- `local.py` no longer owns most lifecycle behavior.
- CLI primarily delegates to `LifecycleApp`.
- All selected agent-simulation scenarios and real dogfood/replay checks pass.
- `mise run check` passes.
- `mise run sync-check` passes for generated HK exports when applicable.

## Agent-simulation and real-dogfood suite design

Use two distinct concepts:

- **Agent simulations** are pytest/scripted fake-agent journeys against tiny temp Git repos. Use marker `agent_sim` or `workflow_sim`, not `dogfood`. They should use public CLI commands for HK interactions and assert lifecycle state, JSON shape, exit codes, and agent-facing recoverability.
- **Real dogfood/replay** means using Harness Kit to build Harness Kit, including repo-local skill/harness workflows such as `.agent/skills/hk-pr-sized-dogfood/` when a PR-sized replay study is useful.

Required agent-simulation scenarios and phase gates:

1. Happy-path code change — create in Phase 0D and keep green throughout.
   - start work
   - record plan/context/decision
   - edit fixture file
   - validate with passing native command
   - record external-enough review
   - sync
   - ready/summary/handoff

2. Local agent-state churn — complete before/with Phase 1.
   - create `.pi` or equivalent local-only state
   - sync with exclusion
   - mutate excluded content
   - assert sync check stales under new semantics

3. Failed validation/review path — complete before/with Phase 3/4.
   - capture failing command
   - record rejected/blocking review
   - assert ready remains not-ready until fixed or dangerously skipped

4. Exported handoff freshness — complete before/with Phase 5.
   - export `.ai/hk/<work-id>/`
   - check export freshness
   - mutate ledger/diff/generated file
   - assert export check catches staleness or generated-file modification

5. Profile-required changed path — complete before/with Phase 6.
   - configure profile rules
   - edit matching path
   - assert ready fails until named `hk validate --check` and named review are recorded

6. Mistake recovery / agent UX — keep green across all CLI-affecting phases.
   - pass `--profile` to lifecycle command
   - omit plan or review
   - assert status/help gives actionable repair hints

## Validation ladder per slice

For each implementation slice:

1. Run focused new tests first.
2. Run related existing unit/integration tests.
3. Run CLI smoke and agent-simulation tests affected by the seam.
4. For CLI-facing changes, run an agent-friendly CLI design review focused on non-interactive behavior, JSON shape, help examples, exit codes, and repair hints.
5. Run `mise run check` before handoff.
6. For slices that touch exported HK state or plan artifacts, run `mise run sync-check`.
7. Record validation with `hk validate --why ...` when dogfooding in this repo.

## Revised slice outline

1. Register and apply test marker taxonomy; separate pure unit from integration/CLI.
2. Add public CLI smoke tests for current lifecycle commands and negative states.
3. Add current-format characterization tests and document the no-long-term-legacy compatibility stance.
4. Add minimal public-CLI agent-simulation harness and happy-path scenario.
5. Extract Git snapshot/sync modules with wrappers.
6. Add sync exclusion content revalidation semantic fix plus local-state agent simulation.
7. Add typed lifecycle event query module and migrate readiness/rendering queries incrementally.
8. Add validation/review freshness metadata and readiness semantics.
9. Extract evidence capture module.
10. Add command timeout/truncation/process cleanup contract and implementation.
11. Extract handoff/export module and safe export file writes.
12. Extract ProfileContext and structured profile suggestion JSON.
13. Migrate CLI/product behavior to LifecycleApp as the primary seam.
14. Run full agent-simulation suite plus selected real dogfood/replay checks, then delete compatibility wrappers and shrink `local.py`.
15. Update docs/spec/ADR and this repo’s HK profile/check path matchers, run full validation, and export final HK handoff.

## Review and profile maintenance requirements

- Any slice that changes CLI command names, options, help text, JSON output, exit behavior, or examples must include an agent-friendly CLI design review in addition to normal code review.
- Any slice that moves files, modules, templates, task scripts, exported HK artifact paths, or profile-sensitive areas must update this repo’s Harness Kit profile/check path matchers. Treat profile drift as part of the refactor, not a separate optional cleanup.
- Follow-up product question: decide whether this repo’s HK profile should live in-repo so file matcher drift is reviewed with the code changes that cause it.

## Risks and mitigations

- Risk: test churn from direct `local.py` imports. Mitigation: keep wrappers, migrate tests gradually to product seams.
- Risk: semantic fixes break existing HK workflow habits. Mitigation: isolate behavior changes, update docs/status guidance, and make failure messages actionable.
- Risk: temporary compatibility grows into permanent baggage. Mitigation: document the no-long-term-legacy stance, keep wrappers temporary, and delete prototype-only compatibility before merge.
- Risk: CLI text snapshot brittleness. Mitigation: stable JSON snapshots plus key-phrase text smoke tests.
- Risk: agent-simulation suite becomes slow. Mitigation: keep fixture repos tiny and separate from generated scaffold e2e; reserve heavier real dogfood/replay for PR-sized checkpoints.
- Risk: diff freshness semantics become too strict for docs-only or planning work. Mitigation: allow explicit dangerous skip with precise rendering, or classify evidence scope by changed paths.
- Risk: command timeout defaults break legitimate long validations. Mitigation: choose conservative defaults, support overrides, and document behavior before enabling readiness enforcement.
- # Harness Kit safe TDD refactor plan

## Purpose

Refactor Harness Kit from a working lifecycle prototype into a deeper, safer product implementation without breaking existing agent workflows. The work should move behavior out of `src/harness_toolkit/kit/local.py` and the large Cyclopts adapter into deeper product seams while preserving public CLI behavior, JSON contracts, ledger/export compatibility, and scaffold compatibility.

## Planning decisions

- Scope: hybrid. Structural refactors are no-behavior-change by default; semantic safety changes land only in isolated TDD chunks with explicit failing tests.
- Compatibility: public JSON, exit codes, ledger JSONL, evidence JSONL, and generated export file formats are stable. Human text is smoke-tested for key phrases/examples but may improve.
- Required gates: fast pure unit suite, lifecycle integration suite, black-box CLI smoke suite, scripted agent-simulation tests, real HK dogfood/replay where appropriate, and `mise run check` before handoff.
- Required scripted agent-simulation scenarios: happy-path code change, profile-required changed path, mistake recovery / agent UX, local agent-state churn, failed validation/review path, exported handoff freshness. Reserve “dogfood” for real Harness Kit dogfooding through the repo-local harness/skill workflow.
- Major seam order: conformance/agent-simulation first, then Git/sync, typed events plus validation/review freshness contract, evidence, export, profiles, and finally LifecycleApp/CLI cleanup.
- Done means: `local.py` no longer owns most lifecycle behavior; CLI primarily delegates to `LifecycleApp`; sync exclusions and validation/review freshness are fixed; command capture has timeout/truncation/process cleanup; agent-simulation scenarios and selected real dogfood/replay checks pass; test marker taxonomy is cleaned up; docs/spec/ADR reflect changed semantics.

## Non-negotiable safety rules

1. Do not mix mechanical extraction and behavior-changing semantics in the same slice.
2. Every behavior-changing safety fix starts with a failing test that describes the desired product behavior.
3. Keep compatibility wrappers until the corresponding public-CLI agent-simulation scenarios pass.
4. Prefer additive JSON changes; no public JSON/file-format breaking changes without an explicit decision and migration note.
5. Preserve shell-first validation: no `hk run` task runner, no automatic command selection, no readiness scoring.
6. Keep each implementation slice PR-sized and independently shippable.
7. Scripted agent-simulation journeys must use public `hk` CLI commands, except for fixture setup helpers. Reserve `dogfood` for real HK dogfooding/replay runs.
8. Use TDD-style sequencing throughout: characterize existing behavior before mechanical extraction and write failing tests before semantic changes.
9. Do not overbuild long-term backward compatibility for short-lived pre-refactor internals; temporary wrappers are for safe migration only.

## Phase 0 — Baseline characterization and conformance harness

Goal: make current product behavior observable before moving code.

### 0A. Test taxonomy and commands

Add and apply markers for:

- `unit`: pure, fast, no subprocess Git/uv where possible.
- `integration`: real temp Git repos and LifecycleApp/local state flows.
- `cli`: public black-box `uv run hk ...` entrypoint coverage.
- `agent_sim` or `workflow_sim`: scripted fake-agent journeys through public CLI commands. Do not call this marker `dogfood`; dogfood means real HK use/replay.
- `e2e`: generated repo / scaffold workflows.
- `slow`: toolchain-heavy or long-running checks.

Reclassify existing tests instead of only registering marker names. For example, tests that initialize Git repos or run `uv run hk` should not remain marked as pure unit just because they live under `tests/unit/`.

Suggested commands:

- `uv run pytest -m unit`
- `uv run pytest -m "integration or cli"`
- `uv run pytest -m agent_sim` (or the chosen simulation marker)
- `mise run check` as the full final gate.

Acceptance criteria:

- Marker descriptions match actual behavior.
- Fast unit suite is meaningfully fast and does not include black-box CLI subprocess tests.
- Existing `mise run check` remains green.

### 0B. Public CLI smoke coverage

Add black-box CLI smoke tests for stable JSON fields, exit codes, and key human text phrases/examples. Cover at least:

- `hk brief --json`
- `hk start --plan --json`
- `hk context --json`
- `hk decide --spec-impact ... --json`
- `hk status --json`
- `hk validate --why ... -- <command>`
- `hk review prompt`
- `hk review add ... --json`
- `hk artifact attach ... --json`
- `hk sync --check --json`
- `hk dangerously-skip ... --json`
- `hk ready --json`
- `hk summary`
- `hk handoff`
- `hk checks --changed --json`
- `hk profile resolve --json`
- `hk export --format handoff-dir --check --json`

JSON assertions should check stable fields and allowed additive fields. Human text assertions should check key repair hints, examples, and scary dangerous-skip language rather than full paragraphs.

### 0C. Compatibility stance and current-format characterization

Do not build long-term compatibility for short-lived pre-refactor internals. This tool is new enough that preserving every one-day-old local ledger shape is not worth extra architecture or test burden. Instead:

- Characterize the current public CLI JSON/file formats that must stay stable during the refactor.
- Keep temporary wrappers while moving call sites.
- Add migration/compatibility code only when it protects active in-repo work during the refactor.
- Remove temporary compatibility paths before merge if the final design no longer needs them.

Acceptance criteria:

- The plan distinguishes public compatibility from internal prototype compatibility.
- No phase adds permanent legacy machinery just to preserve short-lived pre-refactor internals.

### 0D. Agent-simulation harness skeleton

Create a fixture harness for scripted fake-agent journeys in tiny temp Git repos. These are simulation tests, not the repo-local HK dogfood/replay skill. Agent-simulation journeys must call the public CLI for all HK interactions. Setup helpers may create fixture repos, profiles, and files directly.

Acceptance criteria:

- Agent-simulation tests can run independently.
- Failures print the command transcript / JSON payload that failed.
- The minimal happy-path journey passes before structural extraction begins.

## Phase 1 — Git snapshot and sync freshness module

Goal: extract Git and freshness behavior from `local.py` into a deep module that owns repo facts, changed paths, diff hashes, sync exclusions, and agent-local state warnings.

Proposed modules:

- `src/harness_toolkit/kit/git/snapshot.py`
- `src/harness_toolkit/kit/sync/freshness.py`

### TDD-first semantic fix: sync exclusion revalidation

Add failing public-CLI agent-simulation/integration tests before implementation:

- Given `hk sync --exclude .pi --reason agent-local`, when `.pi/session.json` changes, then `hk sync --check` reports stale.
- Given an excluded directory gets a new file, `hk sync --check` reports stale.
- Given an excluded path becomes tracked/staged, `hk sync --check` reports stale with a repair message.

Implementation:

- Store recursive metadata/content hashes for excluded untracked files/directories.
- Compare stored excluded metadata during sync checks.
- Keep excludes literal/path-safe and local-only.

### No-behavior-change extraction

Move behind wrappers:

- `git_sha`
- `git_dirty`
- changed path discovery
- diff hashing
- untracked hashing
- pathspec excludes
- sync exclude safety checks
- agent-local state warnings

Acceptance criteria:

- Existing sync/profile changed-path tests pass.
- New excluded-path-content-change tests pass.
- Local agent-state churn agent-simulation scenario passes.
- `local.py` wrappers still preserve old import paths.

## Phase 2 — Typed lifecycle events and freshness contract foundation

Goal: stop leaking raw event dictionaries throughout readiness, rendering, review prompts, export, and status, while preparing additive freshness metadata for evidence/review semantics.

Proposed module:

- `src/harness_toolkit/kit/ledger/lifecycle_events.py`

Implementation shape:

- Keep JSONL storage format stable.
- Add typed event constructors and parsed event/query helpers for:
  - work started
  - note added by kind
  - command captured
  - review added
  - artifact attached
  - sync checkpoint
  - dangerous skip
- Add temporary/default handling only where needed for active in-refactor events missing newly introduced optional fields.
- Add query helpers for validation/review coverage state, even before enforcement is fully enabled.

Acceptance criteria:

- Existing malformed JSONL tests still pass.
- Current active in-refactor ledger fixtures parse successfully where temporary compatibility is needed.
- Readiness and handoff rendering no longer need to know raw event payload keys except inside the event module.

## Phase 3 — Validation/review diff freshness semantics

Goal: ensure `hk ready` cannot accidentally bless validation or review evidence that covered an older diff.

This phase intentionally happens before the broad evidence/export/profile/LifecycleApp refactors so later seams are built around the correct readiness contract.

### TDD-first tests

Add failing tests for:

- validate, mutate code, sync, ready should fail or warn until revalidated or dangerously skipped.
- review, mutate code, sync, ready should fail or warn until rereviewed or dangerously skipped.
- named profile checks/reviews must cover the current matching changed paths.
- records created before the freshness change follow the explicit compatibility stance from Phase 0C; do not add permanent legacy machinery unless needed for active in-repo work.
- dangerous validation/review skips are diff/event scoped, or explicitly rendered as not diff-scoped if that is the chosen product behavior.

### Implementation

Record additive fields on new evidence/review events:

- diff hash
- changed paths
- event sequence or coverage boundary
- target scope

Update readiness policy to require current diff coverage for validation and review unless an explicit dangerous skip covers the current state.

Acceptance criteria:

- Current diff must be covered by latest accepted validation/review or explicit dangerous skip.
- Handoff clearly renders freshness state and any dangerous skips.
- Happy-path and failed validation/review agent-simulation scenarios pass.

## Phase 4 — Evidence capture module and command hardening

Goal: make exact command evidence a deep module instead of behavior split across `local.capture_command`, process adapter, redaction, transcripts, Git facts, and ledger writes.

Proposed module:

- `src/harness_toolkit/kit/evidence/capture.py`

### Public contract before implementation

Define the command-capture contract before writing tests:

- CLI flags: decide whether to add `--timeout-seconds` and `--max-log-bytes`, or use config/env defaults first.
- Defaults: choose conservative defaults that do not break normal long-running checks unexpectedly.
- Timeout result: define exit code, evidence `status`, `timed_out: true`, transcript marker, and whether timeout evidence can satisfy readiness.
- Truncation result: define `truncated: true`, `transcript_bytes`, deterministic marker text, and interaction with `--no-log` / `--raw-log`.
- Process cleanup: define process-group behavior for argv and shell mode.
- Compatibility stance: additive fields are okay, but do not preserve unused prototype-only evidence formats beyond the refactor unless active work requires it.

### TDD-first hardening tests

- command times out and child process is cleaned up.
- shell mode timeout cleans up child process.
- transcript truncates after max bytes with marker.
- `--no-log` still avoids transcript contents.
- `--raw-log` disables redaction but not truncation/timeout metadata.

### No-behavior-change extraction

Move into evidence module:

- command validation
- command display redaction
- transcript path selection
- dirty-before/after and diff coverage snapshotting
- evidence JSONL writing
- `command_captured` event creation
- profile check-name validation hook via ProfileContext once available

Acceptance criteria:

- Existing capture/redaction tests pass.
- New hang/timeout and large-output tests pass.
- Failed validation agent-simulation scenario passes.

## Phase 5 — Handoff rendering and export package module

Goal: make handoff/export a deep package module that owns generated views, handoff-dir metadata, file hashes, stale checks, and safe file writes.

Proposed modules:

- `src/harness_toolkit/kit/handoff/render.py`
- `src/harness_toolkit/kit/handoff/export.py`

### TDD-first safety tests

Add public-CLI and module tests for:

- symlinked generated file such as `README.md` or `meta.json` is rejected or safely replaced without following the symlink.
- symlinked `artifacts/` directory remains safely handled.
- output directory symlink behavior is explicit and safe.
- missing generated file is caught by `hk export --check`.
- modified generated file is caught by `hk export --check`.
- stale ledger/diff metadata is caught by `hk export --check`.

### No-behavior-change extraction

Move out of `local.py`:

- `render_handoff`
- `summary`
- `handoff`
- `materialize_work`
- export helper functions
- `export_handoff_dir`

Acceptance criteria:

- Existing rendering/export tests pass.
- Exported handoff freshness agent-simulation scenario passes.
- `hk export --format handoff-dir --check` stays stable for generated `.ai/hk` packages.

## Phase 6 — ProfileContext module

Goal: make profile behavior target-specific and centralized without turning HK into a command selector.

Proposed module:

- `src/harness_toolkit/kit/profiles/context.py`

Responsibilities:

- Resolve profile for target.
- Validate check/review names.
- Produce changed-path suggestions.
- Produce required profile checks/reviews for readiness.
- Produce structured JSON fields for agents in addition to existing command snippets.

Agent-simulation requirement:

- Complete the profile-required changed path agent-simulation scenario before or during this phase, not at the end of the program.

Acceptance criteria:

- Profile guidance remains advisory.
- Required profile checks/reviews still enforce readiness only when configured rules match.
- Existing profile tests are promoted/reused where possible instead of duplicating coverage blindly.

## Phase 7 — LifecycleApp becomes the product seam

Goal: make `LifecycleApp` the main Harness Kit lifecycle module rather than a pass-through facade.

Work:

- Move CLI command bodies toward parse → request dataclass → `LifecycleApp` → print.
- Reduce direct `local.py` imports from `cli.py`.
- Migrate product behavior tests from direct `local.py` calls to `LifecycleApp` or public CLI agent-simulation scenarios.
- Keep low-level module tests for Git/sync, evidence, ledger events, profile context, and handoff export.
- Leave compatibility wrappers in `local.py` until all required agent-simulation scenarios and any selected real dogfood/replay checks pass.

Acceptance criteria:

- CLI primarily delegates to `LifecycleApp`.
- Product lifecycle tests read as scenarios, not storage implementation probes.
- No public JSON/file-format breakage.

## Phase 8 — Compatibility wrapper deletion and cleanup

Goal: remove old seams only after tests, agent simulations, and selected real dogfood/replay checks prove the new modules.

Work:

- Delete or shrink obsolete `local.py` functions after call sites migrate.
- Remove duplicate status/rendering/profile helper paths.
- Clean imports and dead modules.
- Update docs/spec/ADR for changed semantics and new architecture.

Acceptance criteria:

- `local.py` no longer owns most lifecycle behavior.
- CLI primarily delegates to `LifecycleApp`.
- All selected agent-simulation scenarios and real dogfood/replay checks pass.
- `mise run check` passes.
- `mise run sync-check` passes for generated HK exports when applicable.

## Agent-simulation and real-dogfood suite design

Use two distinct concepts:

- **Agent simulations** are pytest/scripted fake-agent journeys against tiny temp Git repos. Use marker `agent_sim` or `workflow_sim`, not `dogfood`. They should use public CLI commands for HK interactions and assert lifecycle state, JSON shape, exit codes, and agent-facing recoverability.
- **Real dogfood/replay** means using Harness Kit to build Harness Kit, including repo-local skill/harness workflows such as `.agent/skills/hk-pr-sized-dogfood/` when a PR-sized replay study is useful.

Required agent-simulation scenarios and phase gates:

1. Happy-path code change — create in Phase 0D and keep green throughout.
   - start work
   - record plan/context/decision
   - edit fixture file
   - validate with passing native command
   - record external-enough review
   - sync
   - ready/summary/handoff

2. Local agent-state churn — complete before/with Phase 1.
   - create `.pi` or equivalent local-only state
   - sync with exclusion
   - mutate excluded content
   - assert sync check stales under new semantics

3. Failed validation/review path — complete before/with Phase 3/4.
   - capture failing command
   - record rejected/blocking review
   - assert ready remains not-ready until fixed or dangerously skipped

4. Exported handoff freshness — complete before/with Phase 5.
   - export `.ai/hk/<work-id>/`
   - check export freshness
   - mutate ledger/diff/generated file
   - assert export check catches staleness or generated-file modification

5. Profile-required changed path — complete before/with Phase 6.
   - configure profile rules
   - edit matching path
   - assert ready fails until named `hk validate --check` and named review are recorded

6. Mistake recovery / agent UX — keep green across all CLI-affecting phases.
   - pass `--profile` to lifecycle command
   - omit plan or review
   - assert status/help gives actionable repair hints

## Validation ladder per slice

For each implementation slice:

1. Run focused new tests first.
2. Run related existing unit/integration tests.
3. Run CLI smoke and agent-simulation tests affected by the seam.
4. For CLI-facing changes, run an agent-friendly CLI design review focused on non-interactive behavior, JSON shape, help examples, exit codes, and repair hints.
5. Run `mise run check` before handoff.
6. For slices that touch exported HK state or plan artifacts, run `mise run sync-check`.
7. Record validation with `hk validate --why ...` when dogfooding in this repo.

## Revised slice outline

1. Register and apply test marker taxonomy; separate pure unit from integration/CLI.
2. Add public CLI smoke tests for current lifecycle commands and negative states.
3. Add current-format characterization tests and document the no-long-term-legacy compatibility stance.
4. Add minimal public-CLI agent-simulation harness and happy-path scenario.
5. Extract Git snapshot/sync modules with wrappers.
6. Add sync exclusion content revalidation semantic fix plus local-state agent simulation.
7. Add typed lifecycle event query module and migrate readiness/rendering queries incrementally.
8. Add validation/review freshness metadata and readiness semantics.
9. Extract evidence capture module.
10. Add command timeout/truncation/process cleanup contract and implementation.
11. Extract handoff/export module and safe export file writes.
12. Extract ProfileContext and structured profile suggestion JSON.
13. Migrate CLI/product behavior to LifecycleApp as the primary seam.
14. Run full agent-simulation suite plus selected real dogfood/replay checks, then delete compatibility wrappers and shrink `local.py`.
15. Update docs/spec/ADR and this repo’s HK profile/check path matchers, run full validation, and export final HK handoff.

## Review and profile maintenance requirements

- Any slice that changes CLI command names, options, help text, JSON output, exit behavior, or examples must include an agent-friendly CLI design review in addition to normal code review.
- Any slice that moves files, modules, templates, task scripts, exported HK artifact paths, or profile-sensitive areas must update this repo’s Harness Kit profile/check path matchers. Treat profile drift as part of the refactor, not a separate optional cleanup.
- Follow-up product question: decide whether this repo’s HK profile should live in-repo so file matcher drift is reviewed with the code changes that cause it.

## Risks and mitigations

- Risk: test churn from direct `local.py` imports. Mitigation: keep wrappers, migrate tests gradually to product seams.
- Risk: semantic fixes break existing HK workflow habits. Mitigation: isolate behavior changes, update docs/status guidance, and make failure messages actionable.
- Risk: temporary compatibility grows into permanent baggage. Mitigation: document the no-long-term-legacy stance, keep wrappers temporary, and delete prototype-only compatibility before merge.
- Risk: CLI text snapshot brittleness. Mitigation: stable JSON snapshots plus key-phrase text smoke tests.
- Risk: agent-simulation suite becomes slow. Mitigation: keep fixture repos tiny and separate from generated scaffold e2e; reserve heavier real dogfood/replay for PR-sized checkpoints.
- Risk: diff freshness semantics become too strict for docs-only or planning work. Mitigation: allow explicit dangerous skip with precise rendering, or classify evidence scope by changed paths.
- Risk: command timeout defaults break legitimate long validations. Mitigation: choose conservative defaults, support overrides, and document behavior before enabling readiness enforcement.

## Decisions and spec reflection
- Adopted the reviewer feedback: move validation/review freshness earlier, define command timeout/truncation contract before implementation, phase dogfood scenarios before the semantics they protect, and add legacy fixture tests.
- Revised refactor plan terminology and gates: scripted tests are agent simulations, not dogfood; long-term legacy compatibility is not required for short-lived prototype state; CLI-facing slices need agent-friendly CLI review; final cleanup must update HK profile matchers.
  - Spec: not-needed: Spec/docs update not needed.
  - Spec: not-needed: Spec/docs update not needed.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after Phase 0 marker taxonomy, CLI marker reclassification, and agent-simulation harness. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_155024_461669.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after fixing Phase 0 marker taxonomy and agent-simulation test typing. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_160635_969252.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after narrowing CLI marker coverage to actual public CLI tests. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_161933_573135.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes for Phase 0 marker taxonomy and agent-simulation changes. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_162736_216245.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes for generated handoff package. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_163130_512632.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes after Phase 1 Git/sync extraction and sync exclusion revalidation. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_174701_383961.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes before Phase 1 handoff export refresh. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_175103_883609.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes after Phase 2 typed lifecycle event query seam. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_182223_497022.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes before Phase 2 handoff export refresh. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_182619_978394.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes after Phase 3 validation/review freshness semantics. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_194154_483668.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes before Phase 3 handoff export refresh. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_194552_309082.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes after Phase 4 command capture timeout/truncation hardening. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_203014_941823.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes before Phase 4 handoff export refresh. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_203420_328769.transcript.log`
- `mise run check`: pass (exit 0) — validates: Required profile fast gate passes after Phase 5 handoff export symlink safety. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_210728_914064.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Required HK export sync-check passes before Phase 5 handoff export refresh. — `.harness-local/harness-kit/root/work/2026-05-10-152248-harness-kit-refactor-plan/artifacts/ev_20260510_211130_409280.transcript.log`

## Readiness
- Status: `not-ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:hk-dev-dogfood: fail — missing required profile check `hk-dev-dogfood` (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/capture/process.py, src/harness_toolkit/kit/cli.py, +12 more); run `hk validate --check hk-dev-dogfood --why 'Fast gate passes' -- mise run check` using the matching native command, or `hk dangerously-skip validation --label hk-dev-dogfood --reason ... --mitigation ...`
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/artifacts/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/meta.json, +32 more)
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/artifacts/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/meta.json)
- profile-check:hk-readiness: fail — missing required profile check `hk-readiness` (matched .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/artifacts/README.md, .ai/hk/2026-05-10-152248-harness-kit-refactor-plan/meta.json, +32 more); run `hk validate --check hk-readiness --why 'Fast gate passes' -- mise run check` using the matching native command, or `hk dangerously-skip validation --label hk-readiness --reason ... --mitigation ...`
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched AGENTS.md, src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/capture/process.py, +28 more)
- profile-review:hk-lifecycle-review: fail — missing required profile review `hk-lifecycle-review` (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/capture/process.py, src/harness_toolkit/kit/cli.py, +12 more); run `hk review prompt hk-lifecycle-review` and record with `hk review add --review hk-lifecycle-review ...`, or `hk dangerously-skip review --label hk-lifecycle-review --reason ... --mitigation ...`
- sync: pass — sync checkpoint fresh

## Review
- subagent / reviewer-fresh-context (plan-quality): Fresh-context reviewer found the plan direction feasible but requested changes before implementation: move freshness earlier, specify timeout/truncation contract, sequence dogfood before protected phases, and add legacy fixture coverage. Revised plan incorporates these points. [accepted]
- subagent / reviewer-fresh-context (phase0-quality): Final review found no blockers. Prior CLI marker over-broad issue was fixed by keeping test_harness_kit_2 as integration by default and marking individual public CLI tests with pytest.mark.cli; agent_sim marker and test are registered and focused collect/test passed. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Fresh-context review found the only blocker was over-broad CLI marker coverage; this was fixed by removing file-wide cli from mixed test_harness_kit_2.py and marking individual public CLI tests. Follow-up focused collect/test passed with no blockers. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Phase 1 review found no blockers after fail-closed metadata fix. Git snapshot and sync freshness extraction is coherent; sync checks and sync_status_for revalidate excluded metadata; tests cover file content churn, directory additions, nested git directories, missing/mismatched metadata, tracked descendants, and public CLI agent_sim local-state churn. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Phase 2 review found no blockers. New lifecycle_events query seam concentrates event payload parsing for notes, reviews, dangerous skips, artifacts, and sync checkpoints; readiness and handoff rendering use the seam; focused and full validation passed. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Phase 3 review found no blockers after base-aware path/content hashing. Validation and review evidence now record freshness metadata, readiness rejects stale source diffs including committed changes, preserves fresh sync-excluded local state, and keeps validated content fresh when committed unchanged. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Phase 4 review found no blockers after restoring live streaming with transcript-only capping, avoiding no-log buffering, preserving timeout/truncation markers, and streaming full start-failure errors. Focused and full validation passed. [accepted]
- subagent / reviewer-fresh-context [codex-review] (correctness-regression-test-adequacy): Phase 5 review found only that new handoff package files must be tracked; they are included in the phase commit. Export now rejects symlinked output parents on write and check, replaces terminal output symlinks safely, and avoids following generated file symlinks. [accepted]

## Dangerous skips
- validation: hk-readiness — reason: Current repo profile has a circular hk-readiness required check for any change: hk ready cannot pass until hk-readiness evidence exists, but the evidence command itself is hk ready.; mitigation: Recorded required fast-gate and handoff-sync-check evidence, recorded fresh-context review, and added plan follow-up to update repo HK profile/check matchers after the refactor.
