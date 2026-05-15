# harness-toolkit

**Harness Engineering Toolkit** for agent-ready repositories.

This package contains two related CLIs:

- **`hk` / `harness-kit`** — portable planning, validation, local work-ledger,
  command-evidence, sync-checkpoint, and handoff workflow for existing
  repositories without committing scaffold files.
- **`harness-scaffold`** — starter-template CLI for creating new agent-ready
  repositories with a stable task contract, docs structure, CI wiring, and slice
  workflow defaults.

## Prerequisites

Only one tool needs to be on your `PATH` before anything else — mise handles the rest.

```bash
# macOS / Linux (curl)
curl https://mise.run | sh

# macOS (Homebrew)
brew install mise

# Windows (PowerShell)
winget install jdx.mise
```

Once mise is installed, `mise install` will pull down everything declared in `.mise.toml`
(currently Python and uv for the scaffold itself; stack-specific tooling after `init`).

## Install the CLIs

To use `hk` / `harness-kit` from any repository, install Harness Toolkit as a uv tool:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

For a pinned GitHub release:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git@v0.1.0
```

For local development from a checkout:

```bash
uv tool install --editable ~/git_repositories/harness-toolkit
```

Verify:

```bash
hk --version
harness-kit --version
harness-scaffold --version
```

See [Release and Installation](docs/release.md) for release tags, upgrade commands,
and the current no-PyPI-yet policy. See [Harness Kit Design](docs/harness-kit-lifecycle-design.md)
for the lifecycle-first local assistant direction backed by ledger state.

To make Harness Kit the default workflow for your AI tools, add a compact
instruction block to your user-level `AGENTS.md`. See
[Agent Adoption](docs/agent-adoption.md) for the snippet and agent-facing first
steps.

## Getting Started

```bash
# 1. Clone
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project

# 2. Install tools (Python + uv via mise)
mise install

# 3. Initialize — interactive
mise run init

# 4. Or non-interactively
mise run init -- --non-interactive --name my-project --shape single --stack python
```

## Harness Kit Agent Workflow

To have agents use Harness Kit across repos, add the short directive from
[Agent Adoption](docs/agent-adoption.md) to your user-level `AGENTS.md`.

Harness Kit is a **readiness ledger for serious agent-driven changes**. It is
primarily an agent-facing lifecycle, not a task runner or human task manager.
The usual adoption story is that a human shapes the work in normal conversation,
issues, or scratch docs, then asks an implementation agent to use `hk` so the
agent leaves behind plan, evidence, review, and handoff state. The ceremony pays
for itself when the work is risky, broad, multi-step, likely to span context
compaction, or when skipped validation needs to be explicit rather than implied.

The docs follow that journey: first explain what the tool is for, then give
agents a small path that works, then let `hk status` reveal the deeper lifecycle
only when needed.

1. Add a small Harness Kit directive to repo or user `AGENTS.md`.
2. Research and shape the idea in chat, issues, or scratch docs with normal
   human/agent back-and-forth.
3. Hand the agreed intent to an implementation agent and tell it to use `hk`.
4. The agent records enough lifecycle evidence for handoff without committing
   workflow ceremony.

The happy-path agent loop is intentionally short:

```bash
hk profile resolve --target . --json   # optional; uses explicit user config if present
hk start demo-work --plan 'Adopted implementation intent'
# work normally in the repo
hk checks --target . --changed --json  # suggests configured checks/reviews, does not run them
hk validate --why 'Fast gate passes' -- mise run check
hk status
hk ready
hk summary
```

`hk status` is the coach. It tells the agent when to add optional context, record
a decision/spec reflection, dispatch review, reconcile sync state, or use a
scary explicit bypass. Agents should not memorize a long command checklist.
User-level `harness.toml` can bind known repo/module paths to inline profiles or
to standalone TOML profiles loaded from `profiles_dir`, so agents do not need
validation/review conventions re-explained every session. If an agent works in a
Git linked worktree, HK projects configured repo/module target bindings from the
canonical worktree into the linked worktree before falling back to the default
profile. Separate clones are not auto-matched by remote URL. Profiles can suggest
checks/reviews for changed paths and mark specific path matches as required while
still leaving execution and reviewer dispatch to the agent. Path rules accept
both repo-root-relative changed paths and target-relative paths for scoped module
targets.

### Agent command index

Most agents should start with the short loop above and follow `hk status`. These
are the common commands to reach for when the coach asks for something specific:

| Need | Command |
|---|---|
| Read repo shape without mutating state | `hk brief --target . --json` |
| Start or inspect active work | `hk start demo-work --plan "..."`, `hk status`, `hk work status` |
| Record useful framing | `hk context "..."` |
| Record or refine the adopted plan | `hk plan "..."` / `hk plan --from-file FILE` |
| Record decisions and spec impact | `hk decide "..." --spec-impact none\|updated\|not-needed` |
| See configured guidance without running it | `hk profile resolve --target . --json`, `hk checks --target . --changed --json` |
| Capture validation evidence | `hk validate --why "Fast gate passes" -- mise run check`, `hk validate --why "Env-specific test" -- env PYTHONPATH=src pytest -q`, `hk validate --timeout-seconds 120 --max-log-bytes 200000 --why "Bounded test" -- pytest -q` |
| Record external-enough review | `hk review prompt core-review`, `hk review add --review core-review --backend subagent --reviewer fresh-context --summary "No blockers."`, `hk review add --review core-review --path src/foo.py ...` for targeted follow-up |
| Attach/list real tool/harness files | `hk artifact attach --path FILE --kind KIND`, `hk artifact list --json` |
| Reconcile local changes before handoff | `hk sync`, `hk sync --exclude PATH --reason "..."` |
| Check readiness or explain it to humans | `hk ready`, `hk status`, `hk summary`, `hk handoff`, `hk export` |
| Make an explicit exception | `hk dangerously-skip review\|validation\|sync --label LABEL --reason "..." --mitigation "..."` |

Lower-level commands such as `hk note`, `hk evidence`, `hk capture`, and `hk spec`
are inspection/escape hatches, not the promoted path.

`hk` now exposes the Harness Kit lifecycle only: local agent memory, compact adopted
plans, exact command evidence with rationale, review records, readiness checks,
and generated handoffs without committed ceremony. Use `hk start --plan`,
`hk validate`, `hk status`, and then follow the next actions. For meaningful
Harness Toolkit repo work, export a compact committed handoff package with
`hk export --format handoff-dir --output .ai/hk/2026-05-09-120000-demo`; the export
contains a human `README.md`, machine `meta.json`, and explicit-only `artifacts/`.
Do not hand-author new `.ai/plans` slices for this repo. Removed portable plan-artifact commands
(`hk attach`, `hk legacy plan`, and `hk legacy sync-check`) are no longer part of
`hk`. Scaffolded repos still use `mise run plan` and `mise run sync-check`
through the separate slice-workflow CLI.

Planning can happen outside HK; agents translate the agreed intent into compact
HK context/plan/decision records rather than asking HK to infer it. `hk start
--plan` seeds the first lifecycle plan when work starts; `hk start` can also be
used without a plan followed by repeated `hk plan "..."` calls as a living plan
when the implementation shape emerges progressively. `hk profile resolve`, `hk checks --changed`, and `hk status` explain the resolved profile, direct/default/worktree match
kind, and the changed files/patterns that triggered suggested or required
checks/reviews. Suggested profile reviews appear as non-blocking status guidance;
required profile reviews remain readiness blockers. Profile reviews can include
inline or file-backed instructions, which is the recommended way to wrap a skill
or checklist for a fresh-context reviewer. See [Profile Reviews](docs/profile-reviews.md).
`hk artifact attach` can attach real harness/tool files such as
agent session transcripts or Codex review transcripts by copying or referencing
the file, hashing it, and rendering the metadata in handoff/export; `hk artifact
list --json` gives agents a read-only way to verify what is attached. Slugs should be short human-readable task names;
HK-generated work IDs provide chronological ordering. Review is required by
default: prefer an independent AI/tool reviewer (ideally different model,
runtime, or context) and use a fresh-context subagent as the minimum fallback.
Implementation-agent self-review does not satisfy readiness. If the harness has a
fresh-context review mechanism, dispatch `hk review prompt` to it before handoff.
Examples include Pi `subagent`, Claude Code `Agent`/legacy `Task`, and Codex via
the Shell tool running `codex review --uncommitted`. Re-run `hk status` after
review because review tools may create agent-local state. HK records path/content
facts for reviewed changed paths, so later small fixes can be covered by targeted
follow-up review records using `hk review add --path PATH ...` instead of always
rerunning a full review. Generated `.ai/hk/<active-work-id>/` export refreshes are
lifecycle-neutral for validation/review/sync freshness and readiness changed-path
checks; validate their integrity with
`hk export --format handoff-dir --check` / `mise run sync-check`.
If review is impossible,
record an explicit dangerous review skip with a label, reason, and mitigation.
Use `hk brief --json` for read-only workspace cards: it reports repo/scope,
branch/SHA/dirty state, Git worktree identity, active work, and handoff export
status without writing files. Use `hk handoff --json` for a live deterministic
handoff preview, and use `hk export --format handoff-dir --check --json` for a
focused machine-readable export freshness check; JSON check failures still exit
nonzero but return structured missing/stale/invalid/no-active-work states. Use
`hk status` for the agent next-action loop, `hk summary` for a concise
human-readable readiness digest, and `hk handoff` for the longer transfer
artifact. Explicit untracked local-only state can
be handled with recorded one-shot sync exclusions rather than silent ignores;
`hk sync --exclude` is not limited to a hardcoded `.pi`/`.claude` allowlist, but
it still rejects root, pathspec, tracked, staged, or missing paths. Validation
capture can bound process runtime and transcript size with `--timeout-seconds`
and `--max-log-bytes`; timeout/truncation are recorded in evidence, and non-raw
live output uses the same built-in secret redaction guarantees as transcripts.
Today, scaffolded plan artifacts represent that lifecycle as Markdown/YAML files.
The current direction is to make the ledger canonical and export durable handoff
views only when needed.

## Task Contract

Every project initialized from harness-scaffold exposes these commands:

| Command | Purpose |
|---------|---------|
| `mise run init` | Initialize scaffold into a project |
| `mise run setup` | Install dependencies |
| `mise run fmt` | Auto-format code |
| `mise run lint` | Lint checks (non-modifying) |
| `mise run typecheck` | Static type analysis |
| `mise run test` | Unit tests |
| `mise run build` | Build artifacts |
| `mise run check` | Fast quality gate |
| `mise run plan-check` | Validate the active plan and metadata |
| `mise run spec-check` | Validate decision promotion and reflected docs |
| `mise run evidence-check` | Validate declared evidence artifacts |
| `mise run review-check` | Validate external review artifacts |
| `mise run sync-check` | Aggregate handoff readiness checks |
| `mise run slice-plan` | Render the planner prompt for the active slice |
| `mise run slice-implement` | Render the implementer prompt for the active slice |
| `mise run slice-review` | Render the reviewer prompt for the active slice |
| `mise run slice-status` | Show active slice state; use `mise -q run slice-status -- --json` for automation |
| `mise run dev` | Local development |
| `mise run ci` | CI entrypoint (= check) |
| `mise run docs` | Documentation server |
| `mise run plan -- <slug>` | Create a plan directory on a feature branch |
| `mise run verify` | Heavy validation |

## Supported Stacks

| Stack | fmt | lint | typecheck | test |
|-------|-----|------|-----------|------|
| Python | ruff format | ruff check | ty | pytest |
| Go | gofumpt | golangci-lint | go vet | go test |
| Rust | cargo fmt | cargo clippy | cargo check | cargo test |
| Web (TS) | prettier | eslint | tsc --noEmit | vitest |

> Web is planned. Python, Go, and Rust ship with templates and task wiring.

## Repo Shapes

- **Single-project**: One language, conventional layout (`src/`, `tests/` or `cmd/`, `internal/`)
- **Apps workspace**: Multiple apps under `apps/`, shared packages under `packages/`, with an explicit `workspace.toml` module registry

## Design Principles

1. **Stable task contract** — same commands regardless of stack or shape
2. **Thin orchestration** — mise delegates to language-native tools
3. **Fast `check`, explicit `verify`** — `check` is deterministic and fast; `verify` is heavier
4. **Deterministic CI** — GitHub Actions calls `mise run ci` and nothing else
5. **Deterministic slice handoff** — `sync-check` keeps plan/spec/evidence/review in lockstep
6. **CI parity** — pre-commit hooks call the same tasks as CI
