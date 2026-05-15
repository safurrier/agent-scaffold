---
id: agent-adoption
title: Agent Adoption
description: >
  How to make Harness Kit the default agent workflow from a user-level AGENTS.md.
index:
  - id: user-level-agents-md
    keywords: [AGENTS.md, user-level, bootstrap, directive]
  - id: agent-first-steps
    keywords: [hk, install, profile, target, status]
---

# Agent Adoption

Harness Kit works best when implementation agents know to use it before they
start meaningful repo work. The durable instruction should stay small: tell the
agent to use `hk`, give it one starting command, and point it here when it needs
more detail.

## User-level AGENTS.md

Add this block to your user-level `AGENTS.md`:

````markdown
## Harness Kit

For meaningful code changes, use Harness Kit (`hk`) for planning, validation evidence, review, sync, and handoff unless stronger repo-specific instructions supersede it.

Start by resolving the repo/module workflow:

```bash
hk profile resolve --target . --json
```

Use the repo or module that owns the work as `--target`. Profile flags are only for discovery commands such as `hk profile`, `hk checks`, and repo-scope `hk instructions`; do not pass `--profile` or `--profiles-dir` to lifecycle commands unless that command's help shows those options. Then start work with `hk start demo-work --plan "..."`, record validation with `hk validate --why`, and follow `hk status --target .`.

If `hk` is unavailable or you are unfamiliar with the workflow, read the Harness Kit agent adoption guide before proceeding:
https://safurrier.github.io/harness-toolkit/agent-adoption/
````

You can print the current version from the CLI:

```bash
hk instructions
hk instructions --scope user --json
```

## If an agent was pointed here

First check whether `hk` is available:

```bash
hk --version
```

If it is missing, stop and tell the user. Suggest installing Harness Toolkit as a
uv tool:

```bash
uv tool install git+https://github.com/safurrier/harness-toolkit.git
```

After installation, start from the target repo or module:

```bash
hk profile resolve --target . --json
hk start demo-work --plan "Adopted implementation intent" --target .
```

Then work normally in the repository. If you accidentally retry `hk start` with
the same slug while that work item is still active, HK resumes it instead of
creating duplicate retry state. Use a new slug only for a separate work item.
`hk start --plan` is a convenient seed, not a requirement to predict every step
up front; use `hk plan "..."` again as the plan becomes clearer. Use the repo's
own commands for tests, linters, type checks, builds, or other validation.

Record validation evidence with the exact native command:

```bash
hk validate --why "Fast gate passes" --target . -- mise run check
```

Let `hk status` guide the rest:

```bash
hk status --target .
hk ready --target .
hk summary --target .
```

## Choosing `--target`

Use the path that owns the lifecycle state for the work:

- single repo: usually `.`
- monorepo: the module, package, crate, or app directory
- nested work: the smallest stable path whose docs and validation commands apply

Keep the same target across `hk` commands. If you realize the target was wrong,
tell the user and restart or repair the HK work item rather than mixing targets.

Do not carry profile flags into lifecycle commands. Use `hk profile ...`,
`hk checks ...`, or `hk instructions --scope repo ...` to inspect profile guidance,
then continue with plain lifecycle commands such as `hk start`, `hk validate`,
`hk status`, `hk ready`, and `hk handoff`.

## Validation and checks

`hk` does not replace repo-native commands. It records what you ran and why.

To choose validation, inspect:

- repo `AGENTS.md` and nested `AGENTS.md` files
- README and docs
- CI config, task runners, package manifests, and Makefiles
- `hk checks --target . --changed --json`

Run the native command directly, then record it with `hk validate --why`.

## Review

Review is required by default before handoff. Prefer an independent AI/tool
reviewer. A fresh-context subagent is the minimum fallback. Same-context
implementation-agent self-review does not satisfy readiness.

Useful flows:

```bash
# Generic review when no profile-specific review applies.
hk review prompt --target .
# Dispatch the prompt using the current harness if available, then record it.
hk review add --backend subagent --reviewer reviewer-fresh-context --summary "Review summary" --target .

# Profile-named review suggested by hk checks --changed or hk status.
hk review prompt REVIEW_NAME --target .
hk review add --review REVIEW_NAME --backend subagent --reviewer reviewer-fresh-context --summary "Review summary" --target .
hk status --target .
```

If review, validation, or sync cannot be completed, record an explicit exception with a mitigation:

```bash
hk dangerously-skip review --label no-review --reason "Why this is acceptable" --mitigation "How this will be covered" --target .
```

## Commit hygiene

Do not infer that HK or agent-generated local state should be committed. Commit
only files that are part of the requested code, docs, tests, or configuration
change, or files that repo instructions or the user explicitly ask you to commit.

When unsure, ask before adding workflow/state files to git.

## Repo-local snippet

For a repo-local `AGENTS.md`, use the fuller profile-specific snippet:

```bash
hk instructions --scope repo --profile generic
```

Prefer a more specific profile when one exists:

```bash
hk profile resolve --target . --json
hk instructions --scope repo --profile python
```

See [Portable Workflow](portable-workflow.md) for profiles, checks, and the
longer command reference.
