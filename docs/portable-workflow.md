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

Harness Kit currently exposes two related workflows during the 2.0 migration.

Use the HK 2.0 local assistant loop for new agent work that needs local memory,
exact command evidence, and a generated handoff without committing ceremony:

```bash
hk brief --target . --json
hk init --target . --json
hk work start <slug> --target . --json
hk note --kind plan "..." --target .
hk note --kind background|learning|decision|gap|spec-impact "..." --target .
hk capture --kind test --target . -- <native validation command>
hk sync --target .
hk handoff --target . --format markdown
```

Use the plan-artifact workflow when a repo or user needs the existing durable
plan package and handoff-readiness contract:

```bash
hk plan <slug> --target . --profile <profile> --json
hk checks --target . --profile <profile> --json
hk sync-check --target . --profile <profile> --json
```

The plan-artifact workflow is not deprecated yet. It remains the compatibility
path for deterministic readiness checks over TODO, decisions/spec impact,
validation evidence, review records, and artifact manifests. HK 2.0 should close
those readiness gaps before the plan-artifact workflow is demoted.

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
- Run validation directly and record exact command/result evidence in `VALIDATION.md`.
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
hk profile list --target . --json
# choose the closest profile yourself and tell the user once why you chose it
hk status --target . --json
hk plan <slug> --target . --profile <profile> --json
# update the returned plan files as work progresses
hk checks --target . --profile <profile> --json
hk sync-check --target . --profile <profile> --json
```

For monorepos, pass `--target` as the subdirectory that should own the workflow
state. Use `--mode overlay` only when you need workflow files visible inside the
checkout; overlay state lives under `.ai-local/harness-kit/` and is ignored
through `.git/info/exclude`.
````

## Modes

### External state

External mode stores workflow state outside the target repository:

```bash
hk plan add-cache-layer --target /path/to/repo --state-root ~/.local/share/harness-toolkit/workflows --json
hk status --target /path/to/repo --json
hk sync-check --target /path/to/repo --json
```

The target repository stays clean because plans, templates, and workflow metadata
live under the external state root. Set `HARNESS_KIT_WORKFLOW_HOME` to change the
default external root; `--state-root` remains the explicit per-command override.

### Overlay state

Overlay mode stores workflow state inside the target checkout under
`.ai-local/harness-kit/`, then adds a local-only ignore rule to the checkout's
Git exclude file:

```bash
hk attach --target /path/to/repo --mode overlay --json
hk plan add-cache-layer --target /path/to/repo --mode overlay --json
```

This makes files visible to editors and agents while avoiding committed
`.gitignore` changes. The implementation uses `git rev-parse --git-path
info/exclude`, so linked worktrees and `.git` file checkouts are handled.

## Commands

| Command | Purpose |
|---|---|
| `hk brief` | Print a read-only repo brief without choosing validation commands |
| `hk init` | Initialize ignored local or external Harness Kit 2 state |
| `hk work start` | Start a ledger-backed local work unit |
| `hk note` | Append typed plan, background, learning, decision, gap, or spec-impact notes |
| `hk sync` | Record or check a freshness checkpoint for the active work snapshot |
| `hk capture` | Run a native command and record exact evidence |
| `hk handoff` | Render a conservative handoff from the work ledger |
| `hk spec` | Manage optional local/external spec drafts |
| `hk instructions` | Print the minimal `AGENTS.md` snippet, optionally profile-specific |
| `hk profile list` | List built-in/custom profile contracts and model-directed selection guidance |
| `hk profile show <name>` | Show one profile's instructions and checks |
| `hk profile create <name>` | Create an editable custom profile TOML template |
| `hk checks --profile <name>` | Show named verification loops without executing them |
| `hk attach` | Prepare external or overlay workflow state for a target repo |
| `hk plan <slug>` | Create a plan directory in the workflow state |
| `hk status` | Show active plan and validation status |
| `hk sync-check` | Run local handoff checks without requiring tracked artifacts |

Profiles are small workflow contracts for agentic engineering checks. They
describe the checks that exist for an environment; they do **not** run those
checks. Agents should run the suggested validation command directly so the raw
output stays visible in the normal shell loop, then record the exact
command/result in `VALIDATION.md` for plan artifacts or with `hk capture` for
ledger-backed work.

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

Legacy portable workflow stateful commands (`attach`, `plan`, `status`, and
`sync-check`) accept:

- `--target PATH` — target repo or scoped path, defaulting to the current directory
- `--mode external|overlay` — state placement strategy
- `--state-root PATH` — external state root override
- `--json` — machine-readable output

2.0 local-assistant commands (`init`, `work`, `note`, `sync`, `capture`,
`handoff`, and `spec`) use local overlay state by default and accept
`--no-local-files` when the user wants external state instead of checkout-local
ignored files.

Discovery commands that take `--target` (`profile list` and `checks`) also
accept `--mode` and `--state-root` for legacy command-shape consistency, but
they do not read or write workflow state. Commands that need custom profiles
accept `--profiles-dir`; this keeps profile catalogs explicit and avoids hidden
repo-local adoption.

Agent-friendly properties in the current spike:

- non-interactive by default; every input is an argument or flag
- idempotent `attach`; re-running preserves the same local exclude rule
- `attach --dry-run` previews state paths without writing files
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
