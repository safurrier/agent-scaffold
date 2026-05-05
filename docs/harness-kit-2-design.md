---
id: harness-kit-2-design
title: Harness Kit 2.0 Design
description: >
  Lifecycle-first Harness Kit 2.0 design, including the ledger-backed state,
  evidence, readiness, sync checkpoints, optional specs, profiles, and staged migration.
index:
  - id: thesis
    keywords: [hk, shell-first, lifecycle, readiness, ledger, evidence]
  - id: cli-contract
    keywords: [start, plan, decide, validate, review, ready, handoff]
  - id: migration
    keywords: [staged, breaking, parity, fixtures, validation]
---

# Harness Kit 2.0 Design

## Status

Draft implementation design, amended by
`docs/decisions/0009-hk-2-lifecycle-first-cli.md` after product review. This is
the repo-local companion to the vault note `Harness Kit 2.0 SPEC.md`.

The current implementation is a useful ledger/capture foundation, but it should
not be treated as the full HK 2.0 product until the lifecycle-readiness contract
is first-class.

## Thesis

Harness Kit 2.0 is a cleaner, simpler, more elegant version of HK 1.0's
handoff-safety lifecycle.

It should not make agents use a worse shell. It should preserve the original
workflow spine with less ceremony:

```text
plan → spec/decision reflection → validation evidence → external-enough review → readiness gate → handoff artifact
```

The ledger is the implementation substrate, not the primary product story. HK
2.0 should give agents and humans:

- a concise repo map;
- explicit lifecycle records for context, plan, decision/spec reflection,
  validation, review, readiness, and handoff;
- exact command evidence;
- generated human-readable views;
- sync checkpoints that force reconciliation;
- optional local/external specs;
- profile guidance without heuristic auto-selection;
- explicit promotion boundaries for committed artifacts.

## Product boundaries

### `hk`

`hk` is the lifecycle assistant for existing and scaffolded repos. It owns repo
briefing, local/external harness state, work ledgers, lifecycle records, command
evidence, sync checkpoints, readiness checks, handoff rendering, optional local
specs, and profile listing/showing/creation.

It does not own universal task execution, validation command selection, readiness
scoring, automatic repo adoption, or issue-tracker orchestration.

### `harness-scaffold`

`harness-scaffold` remains the greenfield path for harness-ready repos. A later
phase may prototype a canonical scripts adapter contract as an alternative or
companion to the current generated mise task contract.

### Future orchestrator

Future orchestration is deferred. 2.0 should produce state and evidence contracts
that an orchestrator could consume later without implementing daemons, dashboards,
or tracker polling now.

## Non-goals

- Do not add `hk run test`, `hk run check`, or other task-runner UX.
- Do not make `hk` choose validation commands through heuristic scoring.
- Do not create readiness scores or grades.
- Do not create a second durable guide competing with `AGENTS.md`.
- Do not force existing repos to commit `.harness/`, `.agent/`, `.ai/`, scripts,
  or `SPEC.md`.
- Do not require heavy planning ceremony for small changes.
- Do not implement Web/TypeScript scaffold in the core `hk` 2.0 migration.
- Do not implement future orchestration in 2.0.

## Design decisions

### Local state may be rich

Local standardization is allowed. The dangerous boundary is committing generated
ceremony to shared repos.

Default local state may contain ledgers, artifacts, generated Markdown views, and
local specs. Those files remain ignored/local unless explicitly promoted.

### Ledger-backed work model

The canonical work state is append-only JSONL, not a required bundle of Markdown
files. The public CLI should still read as lifecycle verbs rather than a generic
note/event ledger.

```text
<harness-state>/work/<timestamp>-<slug>/
  events.jsonl
  evidence.jsonl
  artifacts/
  views/                 # generated/materialized, not canonical
```

Generated views may include `learning-log.md`, `decisions.md`, `gaps.md`, and
`handoff.md`, but the ledger remains the source of truth.

### Typed notes are lower-level lifecycle records

Planning may happen outside HK in a human/AI conversation, issue, scratch doc, or
research pass. Agents should translate the agreed result into an explicit HK
lifecycle record instead of asking HK to parse the conversation heuristically.
Typed notes are useful as a storage and compatibility layer, but the common user
path should be lifecycle-oriented commands such as `hk context`, `hk plan`,
`hk decide`, and `hk validate`.

Context, plan, learning, decisions, gaps, and spec impact are typed records.
The public lifecycle command should be `hk context`, because HK is doing context
engineering for the next human or agent. It should stay lightweight and
agent-guided: the agent records context when it prevents rediscovery or clarifies
constraints, relevant files, assumptions, or repo facts. HK should not try to
infer when context is non-obvious, and it should not force filler records for
obvious small changes. Lower-level note/event storage may keep `background` as an
internal or migration alias when needed.

```bash
hk context "Relevant files: src/auth/session.py and tests/test_session.py."
hk plan "Update sync/readiness docs, validate with check/sync-check, and record external review."
hk plan --from-file /tmp/adopted-plan.md
hk note --kind learning "Auth timeout behavior is owned by session refresh."
hk decide "Preserved retry count semantics."
hk note --kind gap "Full suite not run."
hk decide "Internal refactor only." --no-spec-impact
```

### Evidence is exact command capture

`hk capture -- <command>` runs native commands while recording proof. It must not
abstract the command into `hk run`.

Required evidence fields include command display, argv or shell command, cwd,
target scope, branch, git SHA, dirty state before/after, timestamps, duration,
exit code, transcript path, and redaction metadata. Failed commands are evidence.

### Capture redaction is pluggable

MVP capture should include a redaction interface from the beginning: no env
capture by default, log caps, a built-in lightweight redactor, `--no-log`, an
explicit `--raw-log`, and optional external scanner configuration. Candidate
scanner tools include `scrubadub`, `detect-secrets`, `gitleaks`, and
`trufflehog`.

### Sync is a checkpoint/freshness bit

`hk sync` is not a semantic quality validator. It is a stop-and-reconcile
checkpoint.

Default behavior:

- print a short reconciliation checklist;
- append a `sync_checkpoint` event;
- store event sequence, git SHA, diff hash, evidence count, and note count;
- make `hk sync --check` binary: synced or needs sync.

Events after the last sync or a changed diff hash make the work unsynced.
Generated views such as handoffs and materialized Markdown are sync-neutral
because they do not change the substance of the work.

Adopted/scaffolded repos may configure stricter checks later.

### Readiness is separate from sync freshness

The existing scaffold task contract's `mise run sync-check` is a handoff
readiness gate, not only a freshness check. It aggregates `plan-check`,
`spec-check`, `evidence-check`, and `review-check` over plan artifacts. HK 2.0
should preserve those guarantees before the plan-artifact workflow is demoted or
removed.

The target 2.0 split is:

- `hk sync --check`: answers "has work changed since the last checkpoint?"
- future `hk ready --check`: answers "is this work ready to hand off?"

`hk ready --check` should validate explicit ledger declarations, not infer
semantic quality. Agents choose plans, commands, and review rubrics; HK records
and checks that required declarations are present, internally consistent, and
renderable.

### Agent work lifecycle

The intended human/agent loop is phase-oriented:

1. **Context** — read repo background, inspect specs/instructions, and record
   stable framing, constraints, relevant files, and discovered repo facts with
   `hk context`.
2. **Plan** — planning may happen in chat or external docs first; record the
   agreed implementation intent as a compact plan note, with optional tasks only
   when a checklist is useful.
3. **Implement** — edit code in the normal shell/editor loop; record notable
   decisions and spec impacts.
4. **Validate** — run native repo commands directly and capture exact evidence
   with a rationale for what each command proves.
5. **Review** — record external-enough reviews with backend, reviewer, rubric,
   findings, and disposition. Multiple rubric-specific reviews should be
   possible over time, such as core quality, repo conventions, design, security,
   UX, or technology-specific best practices.
6. **Handoff** — run sync/readiness checks and render a conservative handoff.

The current scaffold artifacts map to those phases as follows:

| Phase | Current plan artifact | HK 2.0 target |
|---|---|---|
| Context/research | `LEARNING_LOG.md` | `hk context` / learning records |
| Plan | `TODO.md`, `IMPLEMENTATION.md` | `hk plan` plus optional task/checklist records only when useful |
| Decisions/spec | `DECISIONS.md`, ADR/ledger links | `hk decide` and spec-impact reflection records |
| Validation | `VALIDATION.md`, `artifacts/manifest.yaml` | `hk validate --why ... -- <command>` captured evidence |
| Review | `REVIEW.md` | `hk review add` records with backend/reviewer/rubrics/findings/disposition |
| Handoff gate | `mise run sync-check` | `hk ready` plus `hk sync --check` |

This keeps HK 2.0 shell-first while making the old plan package an optional
materialized view of the ledger rather than the canonical source of truth. If
`hk ready` is future work, the implementation is not yet the HK 2.0 replacement;
it is the ledger/capture foundation for it. PR #12 should therefore be reshaped
before merge so the lifecycle commands exist in that branch, rather than landing
the ledger-first UX as the public 2.0 shape.

### Profiles and dumb scripts guide validation; they do not run it

Keep profile UX close to the current model:

```bash
hk profile list --target . --json
hk profile show generic --json
hk profile create <name> ...
```

Do not add heuristic command mining or auto-selected profile recommendations.
`hk brief` may report facts such as `.mise.toml`, `scripts/check`, and CI files,
but must not claim a recommended command or confidence score.

Profiles and dumb repo scripts fit into HK 2.0 as guidance and stable native
command surfaces for `hk validate`, not as a task-runner layer. Profiles are not
the same thing as `.harness/harness.toml`: a profile is a named validation and
workflow guidance object, while `.harness/harness.toml` is the optional committed
repo config/adoption root that can select defaults, policies, and repo-specific
profile locations. For example, `hk profile show python` or `hk checks` may point
an agent at `mise run check`, `uv run pytest`, or `scripts/check`, but the proof
should still be captured as:

```bash
hk validate --why "Full repo quality gate." -- mise run check
hk validate --why "Focused regression coverage." -- uv run pytest tests/unit/test_harness_kit_2.py -q
```

A future `hk ready` may use profile guidance to explain missing evidence kinds,
but it should check explicit captured evidence rather than silently choosing or
running commands.

### Specs can be local/external before committed

Random existing repos can get useful spec context without committing `SPEC.md`.
Committed `SPEC.md` wins when present; local/external specs are labeled drafts;
promotion is explicit and should dry-run before writing.

### Committed config root is `.harness/`

Use `.harness/` for committed harness config when a repo opts in. `AGENTS.md`
remains the durable instruction map. `.agent/skills/` remains the skill root.

## CLI contract

Target lifecycle-first 2.0 commands:

```bash
hk brief [--target PATH] [--json|--markdown]
hk start <slug> [--target PATH] [--json]
hk status [--target PATH] [--json]
hk plan "TEXT" [--target PATH] [--json]
hk plan --from-file PATH [--target PATH] [--json]
hk context "TEXT" [--target PATH] [--json]
hk context --from-file PATH|- [--target PATH] [--json]
hk decide "TEXT" [--spec-impact TEXT] [--target PATH] [--json]
hk validate --why "WHAT THIS VALIDATES" [--kind KIND] [--target PATH] -- <command...>
hk review add --backend NAME --reviewer INDEPENDENT_OR_FRESH_CONTEXT_REVIEWER --rubric NAME --summary TEXT [--disposition TEXT]
hk sync [--target PATH] [--json]
hk sync --check [--target PATH] [--json]
hk ready [--target PATH] [--json]
hk handoff [--target PATH] [--format markdown|pr|json] [--write PATH]
hk spec init|status|outline|promote
hk profile list|show|create
```

`hk review add` is intentionally not a self-review note. It records review from
an independent human/tool or a fresh-context subagent. Same-agent self-approval
must fail readiness; if no independent review is available, the workflow should
use an explicit dangerous review skip instead of laundering self-review as
external review.

Lower-level/compatibility commands may remain during migration, but should not
be equally promoted when a lifecycle command exists. If a redundant command is
only marginally useful, prefer cutting or explicitly marking it advanced or
legacy.

```bash
hk work start|status|materialize        # advanced/legacy work-state surface
hk note --kind ...                      # advanced event entry, if retained
hk capture ... -- <command...>          # lower-level command evidence
hk evidence list                        # inspection/debugging
hk export --format handoff [--target PATH]
hk legacy plan|sync-check               # legacy plan-artifact workflow only
```

Deferred commands also include state cleanup, deep spec impact, profile
validation, skill validation, and compatibility link helpers.

## State model

Default local state:

```text
.harness-local/harness-kit/
  state.json
  work/
  spec/
```

The path is ignored through `.git/info/exclude`, not committed `.gitignore`.

External state uses:

```text
$XDG_STATE_HOME/harness-toolkit/repos/<repo-key>/<scope>/
```

with `~/.local/state/harness-toolkit/repos/<repo-key>/<scope>/` as fallback.

Future committed/adopted config uses:

```text
.harness/
  harness.toml        # repo adoption/config: defaults, policies, selected profiles
  profiles/           # optional repo-specific profile definitions
  workflows/
  checks/
  schemas/
```

## Brief model

`hk brief` is read-only and must leave the worktree clean. It reports target
root/scope, branch/SHA/dirty state, visible harness state, AGENTS/SPEC presence,
profile catalog summary, common repo surfaces, active work status, and sync
status.

Evidence summaries are a planned follow-up once the evidence model stabilizes.

It must not choose validation commands, auto-select profiles, emit confidence
scores, or mutate state.

## Handoff model

Failed evidence in `hk handoff` should read as an attempted validation, not as a
successful validation claim.

`hk handoff` renders a conservative summary from ledgers and git facts. The
initial implementation includes target/branch state, typed decisions, learning
entries, gaps, captured evidence, failed commands, sync status, and spec-impact
notes. If no validation evidence exists, it says so.

Changed-file summaries, manual evidence labels, review focus, and continuation
notes are planned follow-ups.

## Migration strategy

This is a staged breaking migration. Compatibility does not need to be preserved
as a product promise, but the original plan-artifact workflow should not be
deprecated until HK 2.0 closes the readiness gaps that `mise run sync-check`
currently covers.

Each phase must include behavior-focused tests and old/new parity or migration
fixtures where conceptually relevant.

Each implementation phase must:

1. create/use an `hk` plan/work slice;
2. add fixture-based validation before or alongside implementation;
3. run local validation;
4. update plan evidence;
5. participate in final external review before PR.

## Phase plan

1. Canonical design/spec/ADR.
2. Read-only `hk brief`/inspection.
3. Local state + work ledger + typed notes.
4. Sync checkpoint.
5. Capture evidence + redaction prototype/interface.
6. Handoff/exported views.
7. Optional local/external SPEC.
8. Scaffold task-contract prototype.
9. Readiness parity with plan artifacts:
   - compact plan records and optional task/checklist events;
   - validation evidence rationale;
   - review events with backend/reviewer/rubrics/findings/disposition;
   - `hk ready`;
   - plan-directory export from the ledger as a future compatibility feature.
10. Docs/release/public cutover.

## Validation philosophy

Validation must be fixture-heavy and behavior-focused.

Fixture repos should cover generic git repos, Python/uv repos, Rust/mise repos,
the current harness-toolkit repo shape, monorepo scoped targets, repos with
committed specs, repos with local/external specs, and repos with no specs.

Test layers:

- unit tests for state resolution, event appending, JSON schemas, and sync
  freshness;
- golden tests for brief, handoff, and exported Markdown;
- E2E tests for clean worktree, overlay/external state, capture success/failure;
- migration/parity tests comparing current v1 concepts to v2 behavior where
  applicable.

## Acceptance criteria

- `hk brief` works without state and leaves the repo clean.
- `hk init` is idempotent and supports local/external state.
- `hk work start` creates an active ledger-backed work unit.
- `hk note` records typed note events.
- `hk sync` records a checkpoint; `hk sync --check` is freshness-based.
- `hk capture` preserves command identity, streams output, records exit code, and
  writes redacted evidence by default.
- `hk handoff` renders conservative Markdown/JSON without validation overclaims.
- `hk spec init --local` creates non-committed spec context.
- No default command commits harness artifacts to arbitrary existing repos.
- No command adds readiness scores or heuristic profile recommendations.
