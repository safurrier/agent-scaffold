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

**Current HK dev CLI**: `scripts/hk-dev ...` runs this checkout's `hk` while
preserving the caller cwd; use it for dogfood before the installed `hk` is
updated.

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

- **DO** treat HK 2.0 as a cleaner, simpler version of the HK 1.0
  handoff-safety lifecycle. **NOT** as a generic local note ledger or unrelated
  agent-memory product. **BECAUSE** the core product promise to preserve is:
  explicit plan, spec/decision reflection, validation evidence, external-enough
  review, readiness gate, and handoff artifact.

- **DO** consider `context` a plausible HK 2.0 product verb because it connects
  to context engineering: capturing framing, constraints, relevant files, and
  discovered repo facts for the next human/agent. **NOT** assume `background` is
  always the better public word just because generic LLM context is overloaded.
  **BECAUSE** a clear `hk context ...` command may express the user-facing job
  better than exposing lower-level note kinds.

- **DO** keep HK 2.0 lifecycle commands opinionated and singular. **NOT** expose
  multiple equally promoted ways to do the same thing. **BECAUSE** the desired
  product is a clean agent/human handoff workflow, not a compatibility maze;
  lower-level commands should be advanced/deprecated only when they are truly
  needed.

- **DO** make `hk context` agent-guided rather than magically detected. **NOT**
  require HK to infer whether work has "non-obvious context." **BECAUSE** the
  normal workflow is human/agent planning outside HK, then the agent distills
  useful context, plan, decisions, validation, and review records into the HK
  ledger only when they prevent rediscovery or improve handoff.

- **DO** use `export` language for turning ledger state into shareable files.
  **NOT** center `materialize` as the product verb. **BECAUSE** users understand
  exporting a handoff package; materialization is an implementation detail.

- **DO** make skipped readiness checks explicit and intentionally scary, e.g.
  `dangerously skip review` or a similarly unmistakable command. **NOT** hide
  skipped review/validation behind bland waiver language. **BECAUSE** skipping a
  lifecycle guarantee should read like a conscious YOLO-style exception.

- **DO** make HK 2.0 review UX plainly require an independent human/tool or a
  fresh-context subagent review. **NOT** rely only on regex-style self-review
  detection or let agents record their own review as external. **BECAUSE** the
  point of the review gate is to prevent same-context self-approval; heuristics
  are guardrails, not the guarantee.

- **DO** treat profiles and dumb repo scripts as validation guidance and stable
  command surfaces that feed `hk validate -- <native command>`. **NOT** turn HK
  into a task runner that chooses and executes checks itself. **BECAUSE** HK 2.0
  should preserve shell-first evidence while still helping agents find the right
  repo-owned commands.

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
| `.agent/skills/hk-pr-sized-dogfood/` | Repo-local skill for PR-sized HK dogfood replay studies |
| `templates/.agent/skills/slice-workflow/` | Skill shipped to generated repos |
| `templates/.ai/plans/AGENTS.md` | Plan artifact contract shipped to generated repos |

<!-- generated-by: context-engineering@2.2.0 | last-updated: 2026-04-30 -->
