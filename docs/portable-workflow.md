---
id: portable-workflow
title: Portable Workflow
description: >
  Harness Kit CLI for attaching portable planning workflow state to an existing
  repository without committing scaffold files.
index:
  - id: overview
    keywords: [portable, attach, workflow, shared-repo, external, overlay]
  - id: harness-instruction-model
    keywords: [AGENTS.md, harness, instructions, minimal]
  - id: modes
    keywords: [external, overlay, git-info-exclude, local-state]
  - id: commands
    keywords: [hk, plan, status, sync-check, instructions]
---

# Portable Workflow

`hk` is the Harness Kit CLI for using portable planning and local-assistant
workflow state in a repository that was not initialized from harness-scaffold. It
is meant for shared codebases where committing `.ai/`, `.agent/`, `.mise/`,
`.harness/`, or `.gitignore` changes is not appropriate. The readable command is
`harness-kit`; the daily short command is `hk`.

Harness Kit 2.0 is migrating `hk` toward a ledger-first local assistant: read-only
repo briefs, ignored/external work ledgers, typed learning/decision/gap notes,
sync checkpoints, captured command evidence, generated handoffs, and optional
local specs. See [Harness Kit 2.0 Design](harness-kit-2-design.md).

The CLI uses Cyclopts so command signatures carry Python type information (for
example `Literal["external", "overlay"]` for mode choices) while still producing
focused help for agents.

## Install

Install `hk` from GitHub as a uv tool:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

For a pinned release:

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
```

## Overview

Harness Kit keeps workflow state separate from target repository ownership:
`--target` identifies the repo or module that owns the work, while `--profile`
identifies the workflow/check contract to follow.

## Which workflow should I use?

Harness Kit now exposes the HK2 lifecycle for agent work that needs local
memory, exact command evidence, review records, readiness checks, and a generated
handoff without committing ceremony:

```bash
hk brief --target . --json
hk start <slug> --plan 'Adopted implementation intent' --target . --json
hk validate --why 'What this proves' --target . -- <native validation command>
hk status --target . --json
hk ready --target . --json
hk handoff --target . --format markdown
```

The old HK1 plan-artifact commands were removed from `hk`: there is no `hk
attach`, `hk legacy plan`, or `hk legacy sync-check`. Scaffolded repos still keep
the durable plan-package workflow through `mise run plan` and `mise run
sync-check`, backed by the separate slice-workflow CLI.

Conceptually, the intended agent/human lifecycle is:

```text
research → plan → implement → validate → review → handoff
```

Planning can happen outside HK in chat, issues, or scratch docs. Once the plan is
stable enough to implement, agents should translate the agreed intent into a
compact HK plan note, for example:

```bash
hk note --kind plan --from-file /tmp/adopted-plan.md --target .
```

HK records the explicit plan; it does not parse conversations or infer plans.
Today, plan artifacts represent that lifecycle as Markdown/YAML files. HK 2.0's
target is to represent it as ledger events and generate the Markdown/YAML views
when needed.

## Harness instruction model

The intended adoption path is a tiny durable instruction in a user's global or
repo-level `AGENTS.md`, not a pile of committed scaffold files in every shared
repo. Print the snippet with:

```bash
hk instructions
hk instructions --json
```

### User-level AGENTS.md bootstrap

If you want agents to default to Harness Kit across arbitrary repos, append a
compact instruction block to your user-level `AGENTS.md`. Keep it short and point
to a fuller reference or skill so every session does not load the entire workflow
manual.

Example:

````markdown
## Harness Kit Workflow

For meaningful code changes, use Harness Kit (`hk`) as the default planning and
handoff loop unless stronger repo-specific instructions supersede it.

If the current session is not already familiar with the `hk` workflow, it MUST:

1. Print the current instructions:
   ```bash
   hk instructions --profile generic --json
   ```
2. Read the local Harness Kit workflow reference if one is available.

If already familiar with the workflow, do not reload the full reference just for
ceremony. Still use the managed profile catalog when selecting profiles:

```bash
hk profile list --target <repo-or-module> --profiles-dir ~/.config/harness-toolkit/profiles --json
```

Rules to remember:

- `hk` manages planning/handoff state; it does not run validation commands.
- Run validation directly and record exact command/result evidence with `hk validate --why`.
- Keep `--target`, `--profile`, and `--profiles-dir` consistent across `hk` commands.
- If no good profile exists, use the profile-authoring workflow to propose one;
  do not create profiles silently.
````

For repo-local adoption, `hk instructions` prints a smaller target-specific
snippet:

````markdown
## Portable agent workflow

Use `hk` for meaningful work in this repo or scoped path. Do not
create or commit `.ai/`, `.agent/`, `.mise/`, or `.gitignore` workflow files
unless the user explicitly asks to adopt harness-scaffold in this repository.

Standard loop:

```bash
hk start <slug> --plan 'Adopted implementation intent' --target .
hk checks --target . --json
hk validate --why 'What this proves' --target . -- <native command>
hk status --target .
hk ready --target .
hk handoff --target .
```

For monorepos, pass `--target` as the subdirectory that owns the lifecycle state.
HK stores local state under `.harness-local/`, ignored via `.git/info/exclude`.
````

## Local state

HK2 state is local to the target checkout by default. It lives under
`.harness-local/` and HK adds a local-only ignore rule to `.git/info/exclude`.
There is no external/overlay HK1 plan-artifact mode in `hk` anymore.

## Agent journey

`hk` is mostly an agent-facing lifecycle CLI. Humans usually add a small
`AGENTS.md` directive, shape the work in chat/issues/scratch docs, then hand the
agreed intent to an implementation agent and tell it to use `hk`.

The minimal path is:

```bash
hk start <slug> --plan 'Adopted implementation intent'
hk validate --why 'What this command proves' -- <native command>
hk status
hk ready
hk handoff
```

`hk status` is the journey guide. It tells the agent when to record context,
decisions/spec impact, review, sync, or explicit dangerous skips.

## User config and profiles

For cross-repo use, HK can load a user-level config from:

1. `$HARNESS_KIT_CONFIG`
2. `$XDG_CONFIG_HOME/harness-toolkit/harness.toml`
3. `~/.config/harness-toolkit/harness.toml`

The config is explicit routing plus inline profile guidance. It does not auto-run
checks and does not silently ignore sync paths.

```toml
version = 1
default_profile = "generic"

[[targets]]
name = "foreman"
path = "~/git_repositories/foreman"
profile = "foreman"

[profiles.foreman]
title = "Foreman"
summary = "Rust CLI/TUI project."
target_hint = "~/git_repositories/foreman"
instructions = """
Use focused cargo tests while iterating.
Use `cargo fmt --check` before handoff.
For review, use Codex via `codex review --uncommitted` when available.
"""

[[profiles.foreman.checks]]
name = "cli-config-tests"
purpose = "Run CLI config tests."
command_template = "cargo test --test cli_config"
run_from = "repo-root"

[[profiles.foreman.reviews]]
name = "core-quality"
purpose = "Fresh-context review before handoff."
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt = "Focus on correctness, regression risk, and test adequacy."
# Optional for longer prompts, resolved relative to harness.toml:
# prompt_file = "prompts/foreman-core-review.md"
```

Use:

```bash
hk profile resolve --target . --json
hk checks --target . --json
```

Resolution uses explicit longest path-prefix matching. If a profile has multiple
review entries, the agent should dispatch them independently/in parallel when the
harness supports it, then record accepted reviews with `hk review add`.

Repo-level `.harness/harness.toml`, structured review backend adapters, and
persistent sync ignore config are deferred.

## Commands

| Command | Purpose |
|---|---|
| `hk brief` | Print a read-only repo brief without choosing validation commands |
| `hk init` | Initialize ignored local Harness Kit 2 state |
| `hk start <slug> --plan <text>` | Start a lifecycle work item and optionally seed context/plan records |
| `hk work start` | Advanced compatibility surface for ledger-backed local work units |
| `hk note` | Advanced: append typed plan, background, learning, decision, gap, or spec-impact notes |
| `hk status` | Show active work, readiness checks, and next-action guidance |
| `hk sync` | Record or check a freshness checkpoint for the active work snapshot; use `--exclude PATH --reason TEXT` for explicit one-shot local-state exclusions |
| `hk capture` | Advanced: run a native command and record exact evidence |
| `hk review prompt` | Print a reviewer prompt to dispatch to an independent AI/tool or fresh-context reviewer, e.g. Pi `subagent`, Claude Code `Agent`/`Task` alias, or Codex via Shell tool running `codex review --uncommitted`; re-run `hk status` after review tools run |
| `hk handoff` | Render a conservative handoff from the work ledger |
| `hk spec` | Manage optional local/external spec drafts |
| `hk instructions` | Print the minimal `AGENTS.md` snippet, optionally profile-specific |
| `hk profile list` | List built-in/custom/user-config profile contracts and model-directed selection guidance |
| `hk profile resolve` | Resolve the configured profile for a target using explicit user config bindings |
| `hk profile show <name>` | Show one profile's instructions, checks, and review guidance |
| `hk profile create <name>` | Create an editable custom profile TOML template |
| `hk checks [--profile <name>]` | Show named verification loops and review guidance without executing them; resolves user config when `--profile` is omitted |
| `hk plan <text>` | Record or refine the lifecycle implementation plan for active HK2 work |
| `hk dangerously-skip sync --reason <text>` | Explicitly mark sync freshness as dangerously skipped for the current snapshot |

HK1 plan-artifact commands have been removed from `hk`. Use scaffold `mise run
plan` and `mise run sync-check` for committed plan packages.

Profiles are small workflow contracts for agentic engineering checks. They
describe the checks that exist for an environment; they do **not** run those
checks. Agents should run the suggested validation command directly so the raw
output stays visible in the normal shell loop, then record the exact
command/result with `hk validate --why` for HK2 lifecycle work.

Initial built-in profiles:

- `generic`
- `python`
- `go`
- `rust`
- `rust-mise`

Example discovery:

```bash
hk profile list --target /path/to/repo --json
hk checks --profile python --target /path/to/python-project --json
```

`profile list --target` does not score, rank, or implicitly choose a profile. It
prints available profile contracts plus few-shot selection guidance for the
agent. Agents inspect the target scope, choose the closest profile, tell the user
once why they chose it, and then use that profile consistently. In monorepos,
`--target` should usually be the module/package/crate directory that owns the
work, not the repo root.

The selection order is conceptual, not algorithmic:

1. exact target/module profile, for example `my-project-api`
2. repo-specific profile, for example `foreman-root`
3. stack/task-runner profile, for example `python` or `rust-mise`
4. `generic`

For example, a mixed repo root with a Python manifest under a module such as
`packages/api` should use `--target packages/api` and choose `python` unless a
custom profile like `my-project-api` exists. A Rust repo or crate with `.mise.toml` and repo guidance
naming mise gates should choose `rust-mise` unless an exact module/repo profile
exists.

Custom profiles are explicit TOML files loaded with `--profiles-dir`:

```bash
hk profile create my-project-api \
  --target my_project/api \
  --preset python \
  --output ~/.config/harness-toolkit/profiles/my-project-api.toml

hk profile list \
  --target my_project/api \
  --profiles-dir ~/.config/harness-toolkit/profiles \
  --json

hk checks \
  --target my_project/api \
  --profile my-project-api \
  --profiles-dir ~/.config/harness-toolkit/profiles \
  --json
```

`profile create` creates an editable template only. It does not modify the target
repo, does not infer commands as facts, and refuses to overwrite an existing file
unless `--force` is passed.

Generated harness-scaffold repos include a `harness-kit-profile-authoring` skill
that agents can load when no exact profile exists. It guides agents to mine CI,
hooks, task runners, and repo docs, then propose TOML for user approval before
writing a custom profile.

HK2 lifecycle commands accept:

- `--target PATH` — target repo or scoped path, defaulting to the current directory
- `--json` — machine-readable output where useful
- `--no-local-files` — use external state instead of checkout-local ignored files
  for commands that write lifecycle state

Commands that need custom profiles accept `--profiles-dir`; this keeps profile
catalogs explicit and avoids hidden repo-local adoption.

Agent-friendly properties in the current spike:

- non-interactive by default; every input is an argument or flag
- local state is ignored through `.git/info/exclude`
- profile/check discovery does not execute commands
- JSON output for every command agents need to compose
- actionable errors with a suggested retry command
- focused per-subcommand help with examples

## Current limitations

This is intentionally an early implementation:

- It does not install global mise tasks yet.
- It does not render `slice-plan` prompts from portable state yet.
- `sync-check` is local-only and does not replace committed-plan CI.
- External state is keyed by git remote URL when available, otherwise by target path.

The spike proves that the workflow can be attached to an arbitrary repo without
making that repo dirty.
