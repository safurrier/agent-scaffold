---
id: harness-kit-what-and-why
title: "Harness Kit: Dumb Tasks, Smart Agents"
description: >
  Product philosophy for Harness Kit: why it uses deterministic checks, explicit
  context, profiles, system maps, skills, and readiness evidence instead of
  replacing repo-native tools.
index:
  - id: thesis
    keywords: [hk, harness-kit, dumb-tasks, smart-agents, context-engineering]
  - id: loop
    keywords: [start, checks, validate, review, status, ready, summary]
  - id: config
    keywords: [profiles, system-maps, diagnostics, harness.toml]
  - id: skills
    keywords: [skills, reviews, checks, agent-runtime]
  - id: dogfood
    keywords: [harness-toolkit, dogfood, profile, system-map]
---

# Harness Kit: Dumb Tasks, Smart Agents

> **Harness Kit uses deterministic checks and explicit context to make the task dumb, so the agent can be smart.**

`hk` / `harness-kit` is the existing-repo side of Harness Toolkit. It is a lifecycle and readiness CLI for meaningful agent-driven changes. `harness-scaffold` is the new-repo side: it generates projects with a stable task contract, docs, CI, and stack defaults wired in from day one.

This page is about `hk`: what it is, why it exists, and why it stays tool-native instead of becoming a task runner.

The shorthand:

> **HK is a flight recorder and readiness checklist for agent work.**

Agent work often fails at handoff for boring reasons. The plan lives in chat. Validation is scattered across shell history. Review happened in the same context that wrote the code. Local files make the final tree ambiguous.

HK gives that work a local evidence trail and readiness gate. It does **not** replace the repo's native tools. Agents still run `pytest`, `ruff`, `cargo`, `pnpm`, `mise`, browser smokes, release checks, or whatever the repo already uses. HK records what happened, why it mattered, who or what reviewed it, and whether the work is safe to hand off.

At the lifecycle level, HK keeps returning to five questions:

1. **What was the plan?**
2. **What changed?**
3. **What proves it works?**
4. **Who or what reviewed it independently?**
5. **Is it safe to hand off?**

The core spine is:

```text
plan → decision/spec reflection → validation evidence → external-enough review → readiness gate → handoff artifact
```

That spine is the product. Profiles, system maps, review prompts, artifacts, sync state, and config diagnostics exist to make those answers less ad hoc.

## The smallest useful loop

For meaningful agent work, the normal loop looks like this:

```bash
hk start my-change --plan "Change intent" --target .
# edit normally
hk checks --target . --changed
hk validate --why "Fast gate passes" --target . -- mise run check
hk review prompt relevant-review --target .
hk review add --review relevant-review --backend fresh-context-subagent --reviewer reviewer-name --summary "No blockers." --target .
hk status --target .
hk ready --target .
hk summary --target .
```

The exact order matters less than the loop. `hk start` records the plan. `hk checks --changed` asks what matters for this diff. `hk validate` records exact native command evidence. `hk review prompt` and `hk review add` handle external-enough review. `hk status` coaches whatever is still missing, then `hk ready` and `hk summary` make the handoff auditable.

The agent is not supposed to memorize a giant checklist. **`hk status` is the coach.** It tells the agent what is missing: context, plan updates, decision/spec reflection, validation evidence, independent review, sync freshness, or an explicit dangerous skip when a lifecycle guarantee cannot be met.

## The progressive model

HK is useful with almost no configuration, but it gets sharper when a repo earns more structure.

The layers are: no config for basic lifecycle evidence, profiles for path-aware checks and reviews, system maps for path-aware component/invariant context, and config diagnostics to explain why that guidance surfaced.

This progression matters. HK should not make a small repo feel like it needs a governance program. A tiny repo can use the basic loop. A complex repo can encode the contract agents otherwise rediscover every session: for these paths, these checks, reviews, docs, and invariants matter.

HK turns context engineering into config the next agent can use. Instead of every agent rediscovering validation rules, architecture boundaries, and review expectations from scratch, the repeatable parts are encoded once in profiles, system maps, and diagnostics. HK then communicates that context at the moment of change, while the agent is deciding what to do.

The goal is not to remove judgment from the agent. It is to remove pointless rediscovery. Deterministic checks and explicit config make the task surface dumb and portable; the agent can spend its cognition on implementation tradeoffs, debugging, and adapting the guidance to the actual change.

That creates a compounding loop:

```text
maintain the config → better agent defaults → better handoffs → lessons feed back into config
```

## How configuration fits in

HK config follows the same ownership pattern as most agent config. It can be a user-level overlay, like Claude Code / Codex / Pi config in dotfiles, or it can be repo/module-level when the team wants the workflow contract to be shared.

A user-level `harness.toml` can bind local repo or module paths to profiles and optional system maps:

```toml
[[targets]]
name = "harness-toolkit"
path = "~/git_repositories/harness-toolkit"
profile = "harness-toolkit-root"
system_map = "system-maps/harness-toolkit-root.toml"
```

That binding lets HK resolve “where am I?” into the right workflow contract without requiring the target repo to commit extra ceremony. That is useful for shared/internal repos, personal overlays, and experimental config that should not become repo truth yet.

The promotion path is the same as other agent setup: start local, dogfood the profile/system map, then commit the stable parts when they become repo truth. Module-level targets keep monorepos sane because the contract can attach to the package, app, or service that actually owns the work.

The separation matters. `harness.toml` routes paths to a profile and optional system map. Profiles own validation and review policy. System maps own architectural context. Config diagnostics explain deterministic joins. The HK ledger records plan, context, decisions, validation, review, sync, artifacts, and handoff state.

## Profiles: how should this change be validated?

Profiles answer:

```text
path → checks/reviews/requiredness
```

A profile is a small workflow contract. It says which checks and reviews exist, what they prove, where they run, and which changed paths make them suggested or readiness-blocking.

Checks are tool-agnostic because each check is just a native command template. In an example Harness Toolkit root profile, the final local gate is still the repo-owned command:

```toml
[[checks]]
name = "fast-gate"
purpose = "Default final quality gate before commit or handoff; not the inner-loop check."
command_template = "mise run check"
run_from = "repo-root"
applies_when = ["*"]
required_when = ["src/**", "tests/**", "docs/**", "README.md", "SPEC.md", "AGENTS.md", "pyproject.toml", "mkdocs.yml"]
```

This is **guidance, not hidden execution**.

After touching docs, an agent might ask:

```bash
hk checks --target . --changed
```

and see guidance like:

```text
Required checks:
- focused-contract-tests
  Purpose: Structural contract checks for docs frontmatter, SPEC, ADRs, and mkdocs nav.
  Command: uv run pytest -m contract

- fast-gate
  Purpose: Default final quality gate before commit or handoff.
  Command: mise run check
```

HK stops there. The agent still runs the command through the shell and records proof:

```bash
hk validate --check focused-contract-tests \
  --why "Docs frontmatter and MkDocs navigation contract pass" \
  --target . \
  -- uv run pytest -m contract
```

That is the harness-engineering idea: **the repo remains tool-native, while HK makes the validation contract discoverable and auditable.**

## System maps: what am I touching, and what must I preserve?

System maps answer:

```text
path → component + invariant context
```

An example Harness Toolkit system map can define components like `hk-lifecycle-ledger`, `profiles-system-context`, `scaffold-task-contract`, and `handoff-sync-artifacts`. Each component can list paths, docs to read before editing, relevant check labels, and must-preserve invariants.

Changing profile or system-map code might match `profiles-system-context` and surface invariants like:

> Profiles own commands, requiredness, reviews, and readiness semantics; system maps only add advisory component and invariant context.

and:

> System map validation checks are profile labels, not command templates or hidden readiness policy.

The system map does **not** decide readiness. It only gives pre-edit context and invariant warnings. The profile owns whether a check or review is required.

This is the governance idea:

> System maps do not prevent architectural change. They prevent accidental architectural change.

If an agent intentionally violates an invariant, record it with `hk decide --kind invariant-supersession` and make the docs/handoff/PR trail loud.

## Config diagnostics: why did HK tell me this?

`hk config inspect|validate|explain|audit` are read-only diagnostics for why targets, profiles, system maps, checks, reviews, and invariants surfaced.

For example:

```bash
hk config explain --target . --changed
```

should explain why a changed doc matched `focused-contract-tests`, `fast-gate`, `codex-review`, or a system-map component. It should not generate config, run validation, or become a hidden readiness gate.

## Where skills fit

HK config does not need to contain all expert judgment. It routes the agent to the right checks, reviews, invariants, and prompts. Skills provide the expert procedure for doing those things well.

A useful stack model:

```text
AGENTS.md        = general repo instructions
HK profile       = path-aware checks and review policy
HK system map    = path-aware architecture/invariant context
HK diagnostics   = why this guidance surfaced
Skills           = expert procedures for authoring, reviewing, debugging, docs, etc.
Agent runtime    = Pi / Claude / Codex actually executes the work
HK ledger        = records plan, validation, review, sync, handoff evidence
```

HK tells the agent *what kind of help this change needs*. Skills tell the agent *how to provide that help well*. This works for both checks and reviews.

### Skills behind checks

A check should stay deterministic. It points at the command that proves something. If the command needs domain procedure, the profile can point the agent at a skill in `notes`.

For Harness Toolkit scaffold/template changes, the generated-project smoke is a good example. The check stays the actual command pattern:

```toml
[[checks]]
name = "generated-stack-smoke"
purpose = "CI-parity generated project smoke for scaffold/template/stack behavior; run in a throwaway copy because init is destructive."
command_template = "tmp=$(mktemp -d) && cp -R . \"$tmp/harness-toolkit\" && cd \"$tmp/harness-toolkit\" && mise run init -- --non-interactive --name <name> --shape single --stack <stack> --no-hooks && mise trust .mise.toml && mise run setup && mise run check"
run_from = "repo-root"
required_inputs = ["name", "stack"]
```

The profile can still point the agent at authoring or debugging skills in `notes` or adjacent review prompts. HK says “template/stack changes need generated-project smoke.” A skill can explain how to choose the stack, debug init failures, or inspect generated task drift. The agent runs the real command and records evidence with `hk validate`.

### Skills behind reviews

Reviews work similarly, except the skill usually lives behind a prompt or dispatch hint. The profile defines the review policy; the prompt tells the fresh reviewer which skill or checklist to load and what to return.

In the Harness Toolkit root profile, the general independent review is:

```toml
[[reviews]]
name = "codex-review"
purpose = "Independent AI review before handoff."
backend = "codex"
dispatch_hint = "codex review --uncommitted. Run broad reviews near handoff after implementation stabilizes; after small fixes, prefer targeted follow-up review for changed paths."
applies_when = ["*"]
required_when = ["src/**", "tests/**", "templates/**", "stacks/**", "docs/**", "SPEC.md", "AGENTS.md"]
```

A skill-backed review can use the same pattern. The profile points to a prompt file or inline prompt that tells the reviewer to load a skill such as `architecture-polish-review`, `harness-kit-profile-authoring`, or a repo-local review skill. HK still does not run Codex, Pi, Claude, or the skill itself. It renders the prompt, records that the review was suggested or required, and later stores review evidence:

```bash
hk review prompt codex-review --target .
# Agent dispatches this through Codex / Pi / Claude using the configured workflow.

hk review add \
  --review codex-review \
  --backend codex \
  --reviewer codex-fresh-context \
  --summary "No blockers." \
  --target .
```

That keeps the boundary clean:

```text
HK config routes the work → skill provides expert procedure → agent runtime executes it → HK records evidence
```

## Dogfood example: changing Harness Toolkit docs

If an agent changes this docs page plus `mkdocs.yml`, HK can surface:

**System context**

- Component: `profiles-system-context` or docs-only profile guidance, depending on the touched paths.
- Read first: `AGENTS.md`, `docs/AGENTS.md`, and adjacent docs.
- Must preserve: profiles own policy; diagnostics explain joins without creating hidden readiness gates.

**Profile checks**

- `uv run pytest -m contract`
- `mise run check`
- `mise run sync-check` if committed `.ai/hk/**` exports are generated or changed

**Profile review**

- `codex-review` required for docs changes under the example Harness Toolkit root profile.
- Review focus: lifecycle correctness, task-runner boundary, config semantics, docs accuracy, and test adequacy.

The agent still runs normal commands, but records exact proof:

```bash
hk validate --check focused-contract-tests \
  --why "Docs and MkDocs contract pass" \
  --target . \
  -- uv run pytest -m contract

hk validate --check fast-gate \
  --why "Fast gate passes" \
  --target . \
  -- mise run check

hk review prompt codex-review --target .
# Dispatch that prompt to an independent tool/model/runtime or fresh-context subagent.

hk review add \
  --review codex-review \
  --backend codex \
  --reviewer codex-fresh-context \
  --summary "No blockers." \
  --target .

hk sync --target .
hk ready --target .
hk summary --target .
```

Review backends are guidance/metadata. HK renders the prompt and records the result; the harness or agent runtime performs the actual review dispatch.

After small follow-up edits, the agent should prefer targeted validation and targeted review coverage for the changed paths instead of rerunning a broad review stack by default. HK records path/content facts for reviews so small post-review fixes do not automatically create an endless closeout loop.

## Ok, but is that a lot of config?

Yes. For serious repos, it can be.

But this should work like context engineering: **AI-bootstrapped and human-reviewed**. An agent mines CI, docs, `AGENTS.md`, tests, task runners, and repeated review comments. It drafts the profile/system map. A human reviews once for correctness, taste, and team intent.

That is the setup cost. After that, later agents start from reviewed context instead of rediscovering the repo from scratch.

```bash
hk brief --target .
hk checks --target . --changed
hk config explain --target . --changed
hk review prompt codex-review --target .
hk status --target .
```

**The config is the reusable artifact produced by context engineering.** The task becomes deterministic at the edges: checks, reviews, invariants, diagnostics. That lets the agent be smarter in the middle.

For a tiny repo, HK can stay light. For a complex repo, rich config is the price of reusable judgment.

## Design tension

The core product tension is:

> **HK is simple at the lifecycle level, but rich at the configuration level.**

That is what makes HK code/tooling agnostic. It does not care whether the repo uses Python, Rust, Bazel, pnpm, Terraform, Datadog, Temporal, browser tests, or something else. The portable abstraction is smaller than “run tests.” Changed paths surface relevant checks. Checks are native commands. HK records the evidence, review, invariants, config explanation, sync state, and handoff readiness around that work.

The config richness only pays off if it reduces repeated rediscovery more than it increases setup and maintenance cost. So the product should keep pushing toward faster profile/system-map generation, clearer `hk status` coaching, better `hk config explain`, smaller minimum useful config, and explicit escape hatches for weird work.

The north star is not “more config.” It is making this loop cheap and reliable:

```text
plan → change → proof → independent review → safe handoff
```
