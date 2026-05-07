# HK2 Dogfood Readout

Date: 2026-05-05

Legend: ✅ used successfully · ⚠️ partial / late / recovered · ❌ not used / missed · N/A not available in that run

## Executive readout

| Run | Repos / workers | Prompt style | Main expected workflow under test | What happened | Improvement made afterward |
|---|---|---|---|---|---|
| Real-repo smoke | dread, foreman | Guided by parent | Basic lifecycle: plan/context/decision/validate/review/sync/ready/handoff | Both completed realistic changes and reached ready; proved the lifecycle model could work outside synthetic repos. | Added sharper lifecycle UX: `context --from-file`, better examples, self-review rejection, readiness in handoff, sync-neutral generated views. |
| PR-sized v1 | <REDACTED_ORG> Ads ML, <REDACTED_ORG> Ads API, foreman | Minimally guided; current HK wrapper was awkward | Natural discovery of HK2 lifecycle on larger work | `hk validate --why` was strong; target confusion from wrapper; bare `hk evidence` guessed; legacy `sync-check` attracted workers; decisions/context inconsistent; review gate correctly blocked self-review. | Added `scripts/hk-dev`, strict bare `hk evidence` hint, moved root `sync-check` under `hk legacy`, `.pi` sync warning, dogfood skill. |
| PR-sized v2 | <REDACTED_ORG> Ads ML, <REDACTED_ORG> Ads API, foreman | Targeted rerun after UX fixes | Verify wrapper/legacy/evidence/sync-warning fixes | `--target .` worked; no root `sync-check`; failed evidence wording fixed; `.pi` warning worked; context still under-used; plan/decision still inconsistent; review gate remained correct. | Planned and implemented `hk start --plan`, lifecycle-only root `hk plan`, coaching `hk status`, `dangerously-skip sync`. |
| PR-sized v3 | dread, foreman, obsidian-sync | Targeted at new ergonomics | `start --plan`, status coach, dangerous sync skip | All workers used `hk start --plan`; all used `hk status`; all used `dangerously-skip review`; all used `dangerously-skip sync` for forced `.pi`; review skipped because workers had no independent reviewer. | Added prior-checkpoint requirement for sync skip, promoted `start --plan` in instructions, made dogfood artifacts reviewable, fixed legacy docs. |
| PR-sized v4 | dread, foreman, obsidian-sync | Less-guided: “Use HK; begin by exploring CLI” | Natural discovery of final polish: `sync --exclude`, structured spec impact, review prompt, status phase | All used `start --plan`; 2/3 found `sync --exclude`; 1/3 used structured `--spec-impact not-needed`; 0/3 found `review prompt`; all stopped at missing review rather than launching/recording review. | Patched `hk status` review action to explicitly suggest `hk review prompt`; strengthened review-default-on wording. |
| PR-sized v5 | dread, foreman, obsidian-sync | Review-default-on: complete HK lifecycle; may dispatch independent AI/tool or fresh-context subagent review | Whether stronger review guidance leads workers to review prompt / review record / explicit bypass | All used `review prompt`; 0/3 obtained actual review due delegated-worker environment; all used `dangerously-skip review`; all used `sync --exclude`; 2/3 used structured `not-needed`, 1/3 used `none`. | Next gap is reviewer dispatch ergonomics, not review policy. |
| Single-worker v6 | foreman | Review-dispatch hint: if a fresh-context review mechanism exists, dispatch review prompt | Whether explicit dispatch wording changes behavior | Worker used `review prompt` and recognized it should dispatch, but reported no fresh-context reviewer mechanism was available; used `dangerously-skip review`; final ready-with-dangerous-skips. | Wording is sufficient; actual dispatch support must come from harness/tooling. |
| Single-worker v7 | dread | Tool-callable Codex review hint | Whether Codex Shell review guidance produces `hk review add` instead of dangerous skip | Worker ran `hk review prompt`, tried Codex, obtained accepted Codex review, and recorded `hk review add`; exact stdin form failed, but `codex review --uncommitted` worked. Review tooling created `.pi` state after sync; parent used `sync --exclude .pi` and reached `ready`. | Patch Codex hint to `codex review --uncommitted`; tell agents to re-run `hk status` after review tools. |

## Expected workflow matrix — latest less-guided run (v4)

## Expected workflow matrix — review-default-on run (v5)

| Expected lifecycle step | dread | foreman | obsidian-sync | Finding |
|---|---:|---:|---:|---|
| Explore HK help / status | ✅ | ✅ | ✅ | Baseline CLI onboarding worked. |
| Start work with initial plan (`hk start --plan`) | ✅ | ✅ | ✅ | Happy path remained discoverable. |
| Record decision + structured spec impact | ✅ `not-needed` | ✅ `none` | ✅ `not-needed` | Structured spec-impact discoverability improved. |
| Capture validation with rationale | ✅ | ✅ | ✅ | Still consistently strong. |
| Use review prompt (`hk review prompt`) | ✅ | ✅ | ✅ | Stronger review guidance fixed discovery. |
| Obtain actual independent/fresh-context review | ❌ | ❌ | ❌ | Delegated-worker environment still could not dispatch/obtain reviewers. |
| Explicitly bypass review if no reviewer (`dangerously-skip review`) | ✅ | ✅ | ✅ | Audit path works and avoids self-review. |
| Exclude local-only state (`hk sync --exclude .pi --reason ...`) | ✅ | ✅ | ✅ | Consistent once workers tried to complete readiness. |
| Final readiness | ✅ with dangerous review skip | ✅ with dangerous review skip | ✅ with dangerous review skip | Review remains default-on, but bypass is explicit and auditable. |

## Expected workflow matrix — latest less-guided run (v4)

| Expected lifecycle step | dread | foreman | obsidian-sync | Finding |
|---|---:|---:|---:|---|
| Explore HK help / status | ✅ | ✅ | ✅ | Baseline CLI onboarding worked. |
| Start work with initial plan (`hk start --plan`) | ✅ | ✅ | ✅ | Happy path is naturally discoverable. |
| Record context when useful | ✅ | ✅ via `--context` | ✅ | Context improved compared with early runs. |
| Refine plan if needed (`hk plan`) | ⚠️ guessed old flags first, recovered | ✅ used help / one plan action | ✅ checked help | Root `hk plan` still has some learned/guessed surface area, but no legacy fallback confusion. |
| Record decision + spec reflection | ✅ `--spec-impact not-needed` | ✅ `--no-spec-impact` | ✅ `--no-spec-impact` | Structured mode was discovered by one worker; compatibility alias still common. |
| Capture validation with rationale (`hk validate --why`) | ✅ | ✅ | ✅ | Strongest, most consistently used command across all dogfood. |
| Use review prompt (`hk review prompt`) | ❌ | ❌ | ❌ | Not naturally discoverable. Status needed stronger guidance. |
| Record accepted independent/fresh-context review (`hk review add`) | ❌ | ❌ | ❌ | Workers understood self-review did not count, but did not launch/record subagent review. |
| Explicitly bypass review if no reviewer (`dangerously-skip review`) | ❌ | ❌ | ❌ | In v4 less-guided, workers stopped at review missing rather than bypassing. In v3 targeted, all used it. |
| Reconcile sync checkpoint (`hk sync`) | ⚠️ plain sync; stale on `.pi` | ✅ | ✅ | Dread missed constrained exclude. |
| Exclude local-only state (`hk sync --exclude .pi --reason ...`) | ❌ | ✅ | ✅ | Useful and reasonably discoverable, but status should prioritize it when only agent-local paths are dirty. |
| Check readiness (`hk ready`) | ✅ | parent checked | ✅ | Readiness failures were actionable. |
| Handoff (`hk handoff`) | parent generated | parent generated | parent generated | Workers mostly focused on reports; parent collected handoffs. |

## Expected workflow matrix — targeted ergonomics run (v3)

| Expected lifecycle step | dread | foreman | obsidian-sync | Finding |
|---|---:|---:|---:|---|
| Start work with initial plan (`hk start --plan`) | ✅ | ✅ | ✅ | Directly fixed missed/late plan records. |
| Seed or record context | ✅ | ✅ via `--context` | ✅ | Context usage was much better when workflow was targeted. |
| Record decision/spec reflection | ✅ | ✅ | ✅ | All did it. |
| Capture validation with rationale | ✅ | ✅ | ✅ | All did it. |
| Avoid self-review | ✅ | ✅ | ✅ | Policy understood. |
| Dangerous review skip when no independent reviewer | ✅ | ✅ | ✅ | Works when the prompt makes fallback/constraint salient. |
| Status guidance | ✅ | ✅ | ✅ | Workers reported it was useful. |
| Dangerous sync skip for forced `.pi` churn | ✅ | ✅ | ✅ | Worked, but later parent collection showed snapshot-tied skips can go stale if `.pi` keeps changing. |
| Final ready | ✅ with dangerous skips | ✅ with dangerous skips | ✅ with dangerous skips | Confirmed readiness/handoff semantics. |

## Earlier run summary matrix

| Expected behavior | Real-repo smoke | PR-sized v1 | PR-sized v2 | Resulting improvement |
|---|---:|---:|---:|---|
| Use current checkout HK correctly | ✅ | ❌ wrapper confused `--target .` | ✅ | Added `scripts/hk-dev` using `uv --project`. |
| Avoid legacy root `sync-check` | N/A | ❌ one worker attracted | ✅ | Moved root `sync-check` to `hk legacy sync-check`. |
| Bare `hk evidence` recovery | N/A | ❌ all tripped | ⚠️ still guessed but recovered | Bare command now fails with direct hint. |
| Use context records | ⚠️ | ❌ | ⚠️ only foreman | Added stronger optional context guidance and `start --context`. |
| Record plan early | ⚠️ | ⚠️ inconsistent | ⚠️ inconsistent | Added `hk start --plan`. |
| Record decisions/spec reflection | ⚠️ | ⚠️ late/skipped | ⚠️ inconsistent | Added coaching `hk status` and structured spec impact later. |
| Capture validation with rationale | ✅ | ✅ | ✅ | Kept as core HK strength. |
| Preserve no-self-review gate | ✅ | ✅ | ✅ | Strengthened review docs/help and added `review prompt`. |
| Handle `.pi` / agent-local sync state | N/A | ❌ stale/confusing | ⚠️ warning worked | Added `dangerously-skip sync`, then `sync --exclude`. |

## Improvements made across dogfood cycles

| Problem observed | Improvement shipped | Current status |
|---|---|---|
| Installed/global HK or `uv --directory` made `--target .` point at the wrong repo | `scripts/hk-dev` shim preserving caller cwd | Fixed. |
| Agents used/guessed legacy `hk sync-check` | Root command moved to `hk legacy sync-check`; docs updated | Fixed for new runs. |
| Bare `hk evidence` caused confusion | Bare command now fails with direct `hk evidence list --target <repo> --json` hint | Mostly fixed; agents can recover. |
| Plan records were late or skipped | `hk start <slug> --plan '...'` | Fixed in v3/v4: all workers used it. |
| Root `hk plan` had legacy fallback ambiguity | Root `hk plan` lifecycle-only; legacy artifacts under `hk legacy plan` | Fixed. |
| Agents discovered readiness requirements only at the end | `hk status` now shows checks, next actions, and phase | Improved. |
| `.pi` made sync stale | First warning, then dangerous skip, then constrained `hk sync --exclude PATH --reason` | Improved; 2/3 discovered less-guided. |
| Dangerous sync skip could bypass sync without a prior checkpoint | Require prior `hk sync` checkpoint; skip tied to event seq + diff hash | Fixed after review. |
| Spec impact was vague/free-form | Structured modes `none|updated|not-needed`, optional `--spec-ref` | Improved, but compatibility alias still common. |
| Review path was policy-correct but not actionable | `hk review prompt`; status now suggests it | Needs another run or stronger default-on scaffolding. |

## Review default-on recommendation

Review should be treated as default-on readiness, not an optional nice-to-have.

Recommended policy:

1. New HK work defaults to requiring review for readiness.
2. Acceptable review sources, in order:
   - independent human/tool review;
   - fresh-context subagent review as the minimum fallback.
3. Implementation-agent self-review never satisfies readiness.
4. If review cannot be obtained, the agent must record an explicit event:

```bash
hk dangerously-skip review --reason 'No independent/fresh-context reviewer available before handoff.'
```

This already records an auditable `dangerous_skip_added` event in the HK ledger and renders in handoff under `## Dangerous skips`. The readiness result becomes `ready-with-dangerous-skips`, not plain `ready`.

Recommended next improvement:

- Put this default-on policy directly in scaffolded/AGENTS snippets and `hk status`:

```text
Review required by default.
Preferred: independent human/tool.
Minimum fallback: fresh-context subagent.
Run: hk review prompt
Then record: hk review add --backend subagent --reviewer reviewer-fresh-context ...
If impossible: hk dangerously-skip review --reason ...
```

- Consider a future config surface for review sources, but keep the default policy simple until repeated real use demands configurability.
