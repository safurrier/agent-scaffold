# Agent-Scaffold × Leverage Engineering Context

## What Agent-Scaffold Is

Clone-and-init starter repo for agent-driven engineering. Run `mise run init` → transforms into a fully configured project with a stable 11-task command surface (fmt, lint, typecheck, test, build, check, dev, ci, verify). Python and Go stacks working. Rust and Web planned.

**Core insight**: Both AI agents and humans benefit from a stable, language-agnostic command contract. `mise run check` always works, regardless of stack.

## Why This Matters for Leverage Engineering

### Cap's #1 Problem: Command Validation on Fresh Coder Instances

From the Leverage Eng Technical Roadmap:
> "Cap M1: Coder machines provision reliably in <2 minutes"
> "Multi-project support (web, API, mobile, rust, elixir)"

Cap generates PRs. To validate those PRs, it needs to run commands. On a fresh Coder instance, which commands work? Agent-scaffold's task contract answers this definitively:

| Agent-scaffold task | Cap equivalent |
|---------------------|----------------|
| `mise run check` | Pre-PR validation (fmt + lint + typecheck + test) |
| `mise run ci` | CI entrypoint (same as check, single command) |
| `mise run verify` | Heavier gates (integration, e2e, docker, security) |
| `mise run setup` | Coder machine bootstrap |

This directly addresses Alex's review feedback on Avi's PR:
> "The bar should be: can an agent on a fresh Coder instance run these successfully?"

Agent-scaffold IS that bar.

### AI Native Engineering RFC Implementation

Agent-scaffold is the **concrete implementation** of the AI Native Engineering RFC doctrine:
- "The Repository Is the System of Record" → agent-scaffold puts everything in-repo
- "Progressive Disclosure via AGENTS.md" → template generates AGENTS.md with WHY/WHAT/HOW
- "CI-First Validation" → `mise run ci` is the single entrypoint, GHA calls exactly this
- "Worktree Safety" → all tasks run from clean checkouts
- "Skills (Plugin-Style)" → templates include `.agent/skills/` scaffold
- "docs/architecture.md" → template generates full architecture doc with invariants, principles, ADR registry

### Standardizing New Projects at Discord

From the Leverage Eng roadmap:
> "Vibe-Coded Internal Applications — idea → secure web app → deploy"
> "Support for at least 3 different project types (web, API, Android)"

Every new project Cap creates (or vibe-codes) needs a predictable structure. Agent-scaffold provides:
- Deterministic project layout per stack
- Pre-configured CI that works out of the box
- AGENTS.md that tells agents how to work in this repo
- Pre-commit hooks mirroring CI (no surprises)

### Workflow Platform: Template for Agent-Generated Projects

Workflows M0 describes "opinionated agent skills/capabilities for Temporal workflows." When an agent generates a new workflow project, agent-scaffold is the starting point. The `workspace.toml` module registry for apps-shape repos is exactly what multi-service workflows need.

## Key Architecture Decisions That Align

| Agent-scaffold | Leverage Eng Need |
|----------------|-------------------|
| Stack Protocol (structural interface) | Adding new project types (Rust, TS, Elixir) for Cap |
| `mise run ci` = single entrypoint | Cap's CI generation needs one command to validate |
| Apps workspace shape + `workspace.toml` | Multi-service projects (Cap M3: web, API, Android) |
| `check` (fast, deterministic) vs `verify` (heavier) | Cap's two-tier validation: quick check before PR, full verify in CI |
| Generated AGENTS.md + docs/architecture.md | Every Cap-created project is immediately agent-navigable |
| Golden output tests (deterministic) | Template changes don't break existing projects |

## What's Missing / Future Work for Leverage Eng Alignment

1. **Rust stack** — planned but not built. Cap M3 needs Rust support ("multi-project support: rust, elixir").
2. **Web/TS stack** — planned but not built. Cap M3 needs web support.
3. **Elixir stack** — not even planned. Discord is heavily Elixir.
4. **Discord monorepo integration** — agent-scaffold is for greenfield repos. Need a variant (or module template) that works within the discord/discord monorepo's Bazel build system.
5. **Coder image bundling** — agent-scaffold's `mise run setup` should work in Cap's Coder environment. Need to test/adapt.

## Vault Context

- `staging/agent scaffold.md` — Full SPEC.md (exported from Claude Desktop). Defines all 11 tasks, shapes, acceptance criteria.
- `AI Native Engineering RFC.md` — The doctrine that agent-scaffold implements. Tagged `practitioner`, `high-quality`.
- `Repo Registry.md` — Lists agent-scaffold as `safurrier/agent-scaffold`
- `Personal Tasks.md` — "Write AI Native Engineering post" references the RFC and agent-scaffold as concrete example
- `AGENTS.md Initial Modules PR Review.md` — Command validation section directly informs agent-scaffold's design

## Connection to Groundskeeper

Agent-scaffold provides the **repo structure and task contract**. Groundskeeper provides the **skill definition and workflow orchestration**. Together:

1. `agent-scaffold init` → new project with `mise run check` contract
2. Groundskeeper skills define what agents do in that project
3. `gk generate` → GHA workflows that call `mise run ci`
4. Cap orchestrates via Temporal, using Groundskeeper skills on agent-scaffold projects

This is the full stack for Cap's "Spec-Driven Development" vision.
