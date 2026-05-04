---
id: harness-kit-2-design
title: Harness Kit 2.0 Design
description: >
  Ledger-first local assistant design for Harness Kit 2.0, including state,
  evidence, sync checkpoints, optional specs, profiles, and staged migration.
index:
  - id: thesis
    keywords: [hk, shell-first, local-assistant, ledger, evidence]
  - id: cli-contract
    keywords: [brief, work, note, sync, capture, handoff, spec]
  - id: migration
    keywords: [staged, breaking, parity, fixtures, validation]
---

# Harness Kit 2.0 Design

## Status

Draft implementation design. This is the repo-local companion to the vault note
`Harness Kit 2.0 SPEC.md`.

## Thesis

Harness Kit 2.0 is a shell-first local repo assistant for agent-assisted
engineering.

It should not make agents use a worse shell. It should give agents and humans:

- a concise repo map;
- local structured work memory;
- exact command evidence;
- generated human-readable views;
- sync checkpoints that force reconciliation;
- optional local/external specs;
- profile guidance without heuristic auto-selection;
- explicit promotion boundaries for committed artifacts.

## Product boundaries

### `hk`

`hk` is the local assistant for existing and scaffolded repos. It owns repo
briefing, local/external harness state, work ledgers, typed notes, command
evidence, sync checkpoints, handoff rendering, optional local specs, and profile
listing/showing/creation.

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

### Ledger-first work model

The canonical work state is append-only JSONL, not a required bundle of Markdown
files.

```text
<harness-state>/work/<timestamp>-<slug>/
  events.jsonl
  evidence.jsonl
  artifacts/
  views/                 # generated/materialized, not canonical
```

Generated views may include `learning-log.md`, `decisions.md`, `gaps.md`, and
`handoff.md`, but the ledger remains the source of truth.

### Typed notes capture planning and learning without ceremony

Planning may happen outside HK in a human/AI conversation, issue, scratch doc, or
research pass. Agents should translate the agreed result into a compact `plan`
note instead of asking HK to parse the conversation heuristically. The plan note
is a durable summary of implementation intent, not a project-management system
or a requirement to explode work into many serial task commands.

Plan, learning, decisions, gaps, context, and spec impact are typed events:

```bash
hk note --kind plan "Update sync/readiness docs, validate with check/sync-check, and record external review."
hk note --kind plan --from-file /tmp/adopted-plan.md
hk note --kind learning "Auth timeout behavior is owned by session refresh."
hk note --kind decision "Preserved retry count semantics."
hk note --kind gap "Full suite not run."
hk note --kind spec-impact "No product/spec change: internal refactor only."
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

1. **Research** — read repo context, inspect specs/instructions, and record
   discoveries with learning/context notes.
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
| Research | `LEARNING_LOG.md` | learning/context events |
| Plan | `TODO.md`, `IMPLEMENTATION.md` | plan notes, optional task events, and generated plan view |
| Decisions/spec | `DECISIONS.md`, ADR/ledger links | decision/spec-impact events with durable reflection metadata |
| Validation | `VALIDATION.md`, `artifacts/manifest.yaml` | captured command evidence with rationale and generated evidence views |
| Review | `REVIEW.md` | review events with backend/reviewer/rubrics/findings/disposition |
| Handoff gate | `mise run sync-check` | future `hk ready --check` plus `hk sync --check` |

This keeps HK 2.0 shell-first while making the old plan package an optional
materialized view of the ledger rather than the canonical source of truth.

### Profiles are guidance, not detection

Keep profile UX close to the current model:

```bash
hk profile list --target . --json
hk profile show generic --json
hk profile create <name> ...
```

Do not add heuristic command mining or auto-selected profile recommendations.
`hk brief` may report facts such as `.mise.toml`, `scripts/check`, and CI files,
but must not claim a recommended command or confidence score.

### Specs can be local/external before committed

Random existing repos can get useful spec context without committing `SPEC.md`.
Committed `SPEC.md` wins when present; local/external specs are labeled drafts;
promotion is explicit and should dry-run before writing.

### Committed config root is `.harness/`

Use `.harness/` for committed harness config when a repo opts in. `AGENTS.md`
remains the durable instruction map. `.agent/skills/` remains the skill root.

## CLI contract

Core 2.0 commands:

```bash
hk brief [--target PATH] [--json|--markdown]
hk init [--target PATH] [--no-local-files] [--json]
hk work start <slug> [--target PATH] [--json]
hk work status [--target PATH] [--json]
hk work materialize [--target PATH] [--json]
hk note --kind plan|learning|decision|gap|context|spec-impact "TEXT" [--target PATH] [--json]
hk note --kind plan|learning|decision|gap|context|spec-impact --from-file PATH [--target PATH] [--json]
hk sync [--target PATH] [--json]
hk sync --check [--target PATH] [--json]
hk capture [--target PATH] [--kind KIND] [--shell TEXT] [--no-log|--raw-log] -- <command...>
hk evidence list [--target PATH] [--json]
hk handoff [--target PATH] [--format markdown|pr|json] [--write PATH]
hk spec init --local [--target PATH] [--json]
hk spec status [--target PATH] [--json]
hk spec outline [--target PATH] [--json]
hk spec promote --dry-run [--target PATH]
hk profile list|show|create
```

Planned parity commands before deprecating the plan-artifact workflow:

```bash
compact plan record/readiness checks, with optional task/checklist commands only when useful
hk capture --why "WHAT THIS VALIDATES" -- <command...>
hk review add --backend NAME --reviewer NAME --rubric NAME --summary TEXT --disposition TEXT
hk ready --check [--target PATH] [--json]
hk work materialize --format handoff|plan-dir [--target PATH]
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
  harness.toml
  profiles/
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
6. Handoff/materialized views.
7. Optional local/external SPEC.
8. Scaffold task-contract prototype.
9. Readiness parity with plan artifacts:
   - compact plan records and optional task/checklist events;
   - validation evidence rationale;
   - review events with backend/reviewer/rubrics/findings/disposition;
   - `hk ready --check`;
   - plan-directory materialization from the ledger.
10. Docs/release/public cutover.

## Validation philosophy

Validation must be fixture-heavy and behavior-focused.

Fixture repos should cover generic git repos, Python/uv repos, Rust/mise repos,
the current harness-toolkit repo shape, monorepo scoped targets, repos with
committed specs, repos with local/external specs, and repos with no specs.

Test layers:

- unit tests for state resolution, event appending, JSON schemas, and sync
  freshness;
- golden tests for brief, handoff, and materialized Markdown;
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
