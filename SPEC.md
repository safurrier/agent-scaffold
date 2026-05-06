---
id: harness-toolkit-spec
title: harness-toolkit Specification
description: >
  Correctness envelope for harness-toolkit — the requirements, contracts,
  and invariants that any valid implementation must satisfy.
index:
  - id: requirements
    keywords: [must, should, may, task-contract, init, check, ci, verify, plan]
  - id: interfaces
    keywords: [cli, mise, tasks, stack-protocol, shapes, config, plan]
  - id: invariants
    keywords: [ci-parity, golden-path, worktree, deterministic, stack-dispatch]
---

# harness-toolkit — Specification

> Correctness envelope for the Harness Engineering Toolkit. For how the system
> works now, see `docs/` (MkDocs site). For how to work in this repo, see
> `AGENTS.md`.

## Summary

harness-toolkit contains two related CLIs: `harness-scaffold`, the starter-template CLI for new agent-ready repositories, and `hk` / `harness-kit`, the portable workflow CLI for existing repositories. `harness-scaffold` transforms a cloned template into a fully configured project with a stable 22-task command surface. `hk` applies planning, validation, review, readiness, and handoff workflow state without committing scaffold files, and is evolving toward a cleaner lifecycle-first Harness Kit backed by local ledgers, sync checkpoints, captured command evidence, generated handoffs, and optional local specs. Both humans and AI agents benefit from language-agnostic, CI-parity contracts where `mise run check` is the fast local gate and handoff evidence stays inspectable.

## Goals / Non-Goals

**Goals:**

- Provide a stable, minimal command surface for humans and agents
- Support two repo shapes: single-project and apps workspace
- Keep orchestration thin — delegate to language-native tools
- Make CI call the same entrypoints as local usage
- Preserve "batteries included" capabilities from reference templates (python-collab-template, go-template-project)

**Non-Goals:**

- No Bazel/Buck2 (v1)
- No implicit auto-discovery of apps based on folder existence — configuration is explicit
- No mandatory spec folder layout beyond the generated defaults
- No specific agent runtime requirement (Claude Code, Codex, Pi, etc.)

## Requirements

### MUST

- `mise run init` supports interactive and non-interactive modes
- `mise run init -- --non-interactive` with explicit flags produces deterministic output
- All 22 task scripts exist in `.mise/tasks/`, are executable, and have `# MISE description=` headers
- `mise run check` passes on a freshly initialized project without manual intervention (golden path)
- `mise run ci` produces identical results to `mise run check` (CI parity)
- Pre-commit hooks call the same tasks as CI
- Non-interactive init fails fast with clear errors on missing required inputs
- Generated projects include `AGENTS.md`, `SPEC.md`, `docs/explanation/architecture.md`, `docs/explanation/decisions/`, and CI workflow
- All generated docs have valid YAML frontmatter with `id`, `title`, `description`, and `index` fields
- ADRs have Status (from allowed values), Context, Decision, and Consequences sections
- `mise run plan -- <slug>` creates a plan directory with META.yaml, TODO.md, LEARNING_LOG.md, VALIDATION.md, REVIEW.md, DECISIONS.md, and artifacts/manifest.yaml; invalid or duplicate slugs fail with clear errors
- `mise run slice-plan`, `slice-implement`, and `slice-review` render provider-neutral prompts into the active plan's `prompts/` directory
- `mise -q run slice-status -- --json` emits machine-readable active slice state
- Generated projects include `.ai/plans/` with routing AGENTS.md, templates, and example
- Generated projects include `.agent/skills/slice-workflow/` with artifact policy, handoff rubric, holdout sample tasks, and prompt templates
- Plan META.yaml has required fields: `slug`, `created` (YYYY-MM-DD), `status` (from allowed values)

### SHOULD

- `mise run check` completes in under 60 seconds for a single-project repo
- Init prompts have sensible defaults for every field
- Generated docs have machine-readable frontmatter index entries with keywords
- Adding a new stack requires changes in one file (stack module) plus templates

### MAY

- Support additional stacks beyond Python, Go, and Rust (Web/TS planned)
- Support `workspace.toml` module registry for apps-shape repos
- Support custom task scripts via plugin directories

## Interfaces & Contracts

**Scaffold CLI:**

```
harness-scaffold init [OPTIONS]
  --non-interactive     Skip prompts, require all flags
  --name TEXT           Project name (required)
  --shape [single|apps] Repo shape (required)
  --stack [python|go|rust] Primary stack (required)
  --modules TEXT        Comma-separated module names (apps shape)
  --go-module TEXT      Go module path (Go stack)
  --no-hooks            Skip pre-commit hook installation
  --no-examples         Remove example code after init
```

**Harness Kit CLI:**

Current `hk` commands are lifecycle-first. Portable plan-artifact
commands (`hk attach`, `hk legacy plan`, and `hk legacy sync-check`) are removed;
scaffold plan artifacts use `mise run plan` and `mise run sync-check` through the
slice-workflow CLI instead.

```
hk profile list --target <repo-or-module> --json
hk profile resolve --target <repo-or-module> --json
hk checks --target <repo-or-module> [--profile <profile>] --json
```

The public shape is lifecycle-first rather than generic-note-first:

```
hk brief --target <repo-or-module> --json
hk start <slug> --plan "TEXT" --target <repo-or-module> --json
hk start <slug> --context "TEXT" --plan "TEXT" --target <repo-or-module> --json
hk status --target <repo-or-module> --json
hk plan "TEXT" --target <repo-or-module> --json
hk plan --from-file <path> --target <repo-or-module> --json
hk context "TEXT" --target <repo-or-module> --json
hk context --from-file <path|-> --target <repo-or-module> --json
hk decide "TEXT" --spec-impact none|updated|not-needed --spec-ref <path> --target <repo-or-module> --json
hk validate --why "WHAT THIS VALIDATES" --target <repo-or-module> -- <command...>
hk review prompt --target <repo-or-module> --json
hk review add --backend <independent-tool> --reviewer <independent-reviewer-or-fresh-context-subagent> --rubric <name> --summary "TEXT" --target <repo-or-module> --json
hk artifact attach --path <file> --kind <kind> --label "TEXT" --target <repo-or-module> --json
hk sync --exclude <path> --reason "TEXT" --target <repo-or-module> --json
hk sync --target <repo-or-module> --json
hk sync --check --target <repo-or-module> --json
hk dangerously-skip sync --reason "TEXT" --target <repo-or-module> --json
hk ready --target <repo-or-module> --json
hk handoff --target <repo-or-module> --format markdown|pr [--json]
hk export --target <repo-or-module> --format handoff --json
hk spec init|status|outline|promote --target <repo-or-module> --json
```

Slugs are short human-readable task names; chronological ordering comes from
HK-generated timestamped work IDs. `hk start --plan` starts work and records the
first lifecycle plan event; `hk plan` records or refines lifecycle plan text for
already-active Harness Kit work. Spec impact uses explicit modes (`none`, `updated`, or
`not-needed`) plus optional `--spec-ref` file references. Review is required by
default. Preferred review comes from an independent AI/tool reviewer, ideally a
different model, runtime, or context. A fresh-context subagent is the minimum
acceptable fallback. Implementation-agent self-review does not satisfy readiness;
if the harness provides a fresh-context review mechanism, the agent should dispatch
`hk review prompt` to it before handoff. Examples include Pi `subagent`, Claude
Code `Agent`/legacy `Task`, and Codex via the Shell tool running
`codex review --uncommitted`. Agents should re-run `hk status` after review
because review tools may create agent-local state. If no independent AI/tool
or fresh-context review is available, the
agent must use an explicit dangerous review skip. If sync freshness is stale only because of
understood untracked local-only state, the agent should prefer a constrained
`hk sync --exclude PATH --reason ...`; exclusions are recorded and revalidated
rather than limited to a hardcoded `.pi`/`.claude` allowlist, while root,
pathspec, tracked, staged, and missing paths remain invalid. Whole-sync dangerous
skips remain an explicit fallback.

`hk artifact attach` records harness/tool-produced files such as agent session
transcripts, Codex review transcripts, HAR files, or raw validation artifacts by
copying or referencing the source file, hashing it, and appending metadata to the
Harness Kit lifecycle ledger. Agents should attach real files produced by tools rather
than narrating their own session text into HK.

Profiles and repo-owned scripts are validation guidance and stable native command
surfaces for `hk validate`, not task-runner commands that HK chooses and runs.
Lower-level work/note/capture/evidence commands may remain as compatibility or
advanced interfaces, but Harness Kit is not complete until lifecycle readiness reaches
parity with the plan-artifact workflow.

`harness-kit` is the readable long command for the same portable CLI. `hk` is the
short daily command.

**22-task contract:**

| Task | Purpose | Composition |
|------|---------|-------------|
| `init` | Transform scaffold into project | One-time, destructive |
| `setup` | Install dependencies | `uv sync` / `go mod download` |
| `fmt` | Auto-format | `ruff format` / `gofumpt` |
| `lint` | Lint check | `ruff check` / `golangci-lint` |
| `typecheck` | Type analysis | `ty check` / `go vet` |
| `test` | Unit tests | `pytest` / `go test` |
| `build` | Produce artifacts | Stack-dependent |
| `check` | Fast quality gate | fmt-check + lint + typecheck + test |
| `dev` | Local development | Stack-dependent |
| `ci` | CI entrypoint | Delegates to `check` |
| `docs` | Documentation server | MkDocs dev server |
| `plan` | Create plan directory | Scaffolds `.ai/plans/<slug>/` |
| `plan-check` | Validate plan metadata | Checks active or explicit plan files |
| `spec-check` | Validate decision promotion | Checks ledger/ADR reflection |
| `evidence-check` | Validate evidence artifacts | Checks validation commands and manifest |
| `review-check` | Validate review artifact | Checks external-enough review fields |
| `sync-check` | Handoff readiness gate | Runs active, explicit, or changed-plan checks |
| `slice-plan` | Render planner prompt | Writes `prompts/planner.md` |
| `slice-implement` | Render implementer prompt | Writes `prompts/implementer.md` |
| `slice-review` | Render reviewer prompt | Writes `prompts/reviewer.md` |
| `slice-status` | Show active slice state | Text or JSON status |
| `verify` | Heavy validation | Integration, docker, security |

**Stack Protocol:**

```python
class Stack(Protocol):
    def init_single(self, root: Path, config: Config) -> dict[str, str]: ...
    def init_module(self, mod_dir: Path, config: Config, mod_name: str) -> dict[str, str]: ...
    def remove_examples(self, root: Path, config: Config) -> None: ...
    def remove_module_examples(self, mod_dir: Path) -> None: ...
    def tools_toml(self) -> str: ...
    def adr_notes(self) -> str: ...
    def stack_notes(self) -> str: ...
```

## Invariants

- **CI parity**: `mise run check` locally MUST match the CI quality gate, and CI MUST also run `mise run sync-check` for handoff-contract coverage. Pull request CI MUST validate changed completed plans with `sync-check --changed-plans`. Pre-commit hooks call the same quality tasks. Violation causes green-local/red-CI divergence or missing handoff evidence.
- **Golden path guarantee**: A freshly initialized project (`mise run init`) MUST pass `mise run check` out of the box. Violation breaks first-run experience.
- **Worktree safety**: All tasks must run from a clean checkout or Git worktree. No reliance on absolute paths, mutable global state, or undeclared local artifacts.
- **Stack dispatch via env**: Tasks read `SCAFFOLD_PROJECT_STACK` from `.mise.toml` to dispatch to the correct toolchain. Wrong dispatch = wrong tools run.
- **Deterministic output**: Non-interactive init with identical inputs produces identical output. Template rendering is deterministic.
- **stdlib-only test helpers**: `_docs_helpers.py` uses only stdlib (no pyyaml) so it's portable into generated repos without adding dependencies.
- **Lifecycle-first Harness Kit**: Harness Kit MUST preserve the handoff-safety spine: useful context when it prevents rediscovery, explicit plan, spec/decision reflection, validation evidence, external-enough review, readiness gate, and handoff artifact. A generic note ledger without readiness parity is an implementation foundation, not the completed product.
- **Shell-first command evidence**: `hk` MAY capture exact native commands and local work state, but MUST NOT hide validation behind `hk run`-style task-runner commands. Captured evidence preserves command identity, exit code, rationale, and transcript metadata. Profiles and dumb scripts may guide which native commands to validate, but the proof remains `hk validate --why ... -- <native command>`.
- **Freshness vs readiness**: `hk sync --check` answers whether ledger work changed after the last checkpoint. `hk ready` is the ledger-backed Harness Kit lifecycle readiness gate; `mise run sync-check` remains scoped to scaffold/task-contract plan artifacts.
- **No heuristic readiness/profile scoring**: `hk brief` and profile commands report facts and guidance, not readiness grades, confidence scores, or silent validation command selection. Planning may happen outside HK, but agents must translate the agreed intent into explicit lifecycle records; HK records those declarations and checks evidence consistency while humans/reviewers judge quality. HK does not infer whether context is non-obvious; agents record `hk context` when it improves handoff or prevents rediscovery.
- **Local-first adoption boundary**: default `hk` local assistant state stays ignored or external. Committed `.harness/`, `SPEC.md`, or task-contract artifacts require explicit adoption/promotion.

## Acceptance

```bash
mise run check          # fast: fmt-check + lint + typecheck + all tests
mise run sync-check     # handoff: plan/spec/evidence/review contract
mise run verify         # heavy: integration, e2e, docker (when applicable)
```

Contract tests verify structural invariants (task files, doc schemas, template sections).
Golden output tests verify deterministic rendering across all 4 shapes (Python single/apps, Go single/apps).
E2E tests verify the full init → setup → check pipeline produces passing projects.
