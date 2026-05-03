# harness-toolkit

**When a user corrects you or gives repo-specific tribal knowledge, document it
in the closest `AGENTS.md` before continuing.**

harness-toolkit contains two related CLIs. `harness-scaffold` is the
starter-template CLI: it generates projects with a stable mise task contract,
plan/evidence/review handoff checks, provider-neutral slice workflow prompts, and
stack templates for Python, Go, and Rust. `hk` / `harness-kit` is the portable CLI
for applying the workflow to existing repos without committing scaffold files.
Generated repos receive a skill-local uv CLI, while `mise run slice-*` remains
the stable operator interface.

## How to Work Here

The local checkout path is `~/git_repositories/harness-toolkit`; older notes or
session summaries may still refer to the pre-rename path `~/git_repositories/agent-scaffold`.

Use `mise run plan -- <slug>` for meaningful work, keep the active plan current,
and close the slice with evidence and review before handoff. Treat `SPEC.md` as
the correctness envelope and `docs/task-contract.md` as the task-surface
reference.

## Commands

**Setup**: `mise run setup`.

**Fast gate**: `mise run check`.

**Handoff gate**: `mise run sync-check`.

**Focused tests**: `uv run pytest -m "not slow"`.

**Slice prompt rendering**: `mise run slice-plan -- --task <task.md>`, then
`mise run slice-implement` and `mise run slice-review` when useful.

**Docs preview**: `mise run docs`.

**One-time scaffold transform**: `mise run init`. This is destructive by design;
use it only in a copied scaffold or throwaway init target.

## Gotchas

- **DO** run `uv run pytest -m "not slow"` for fast feedback. **NOT** plain
  `uv run pytest` by default. **BECAUSE** the full suite can include slow stack
  E2E paths that need extra toolchains.

- **DO** run `mise run check` before committing. **NOT** individual quality
  tasks only. **BECAUSE** `check` preserves the intended fmt, lint, typecheck,
  and test order.

- **DO** edit `.mise/tasks/<task>` to change task behavior. **NOT** `.mise.toml`
  task definitions. **BECAUSE** the command contract is file-based task scripts.

- **DO** keep `templates/.agent/skills/slice-workflow/cli` and the slice-related
  `.mise/tasks/*` wrappers aligned. **NOT** duplicate the slice contract in
  repo-local Python scripts. **BECAUSE** the skill-local CLI is the portable
  implementation and mise is the compatibility surface.

- **DO** update the stack registry package, stack templates, and affected mise
  task dispatch handlers together when adding stack behavior. **NOT** by editing
  only one layer. **BECAUSE** init owns generated files while the task contract
  owns how generated projects run stack tools.

- **DO** keep small durable plan evidence committed when it helps review. **NOT**
  commit raw scratch transcripts or ignored artifact subtrees. **BECAUSE**
  `sync-check` treats manifest entries as promises that evidence exists and is
  reviewable.

- **DO** use Cyclopts for portable/agent-facing CLIs like `hk` and
  `harness-scaffold`. **NOT** add new Click surfaces there. **BECAUSE** typed
  signatures, Literal choices, and generated help make the CLI safer for agents
  to call.

## Related Context

| Path | What's there |
|---|---|
| `SPEC.md` | Requirements, interfaces, invariants, acceptance |
| `docs/task-contract.md` | Stable mise task contract and slice workflow tasks |
| `src/harness_toolkit/scaffold/` | Starter-template implementation for `harness-scaffold init` |
| `src/harness_toolkit/kit/` | Portable workflow implementation for `hk` / `harness-kit` |
| `docs/development.md` | Test layers, fixtures, and stack development |
| `docs/init-system.md` | How `mise run init` transforms the scaffold |
| `docs/AGENTS.md` | Docs routing index, including stack and ADR docs |
| `docs/decisions/` | ADRs for scaffold workflow and contract choices |
| `templates/.agent/skills/slice-workflow/` | Skill shipped to generated repos |
| `templates/.ai/plans/AGENTS.md` | Plan artifact contract shipped to generated repos |

<!-- generated-by: context-engineering@2.2.0 | last-updated: 2026-04-30 -->
