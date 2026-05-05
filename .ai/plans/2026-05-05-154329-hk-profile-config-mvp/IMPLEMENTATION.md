---
id: plan-implementation
title: Implementation Plan
description: >
  Step-by-step approach for this unit of work.
---

# Implementation — hk-profile-config-mvp

## Approach

Add a small user-level config layer that feeds the existing profile/check system. Keep it explicit and shell-first: config resolves a profile and profiles describe validation/review guidance, but HK still does not choose or run validation commands automatically.

## Shape

User config path lookup:

1. `$HARNESS_KIT_CONFIG`
2. `$XDG_CONFIG_HOME/harness-toolkit/harness.toml`
3. `~/.config/harness-toolkit/harness.toml`

MVP schema:

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
For CLI config behavior, inspect tests/cli_config.rs first.
For review, use Pi/Claude fresh-context review if available, or Codex via `codex review --uncommitted`.
"""

[[profiles.foreman.checks]]
name = "cli-config-tests"
purpose = "Run CLI config tests."
command_template = "cargo test --test cli_config"
run_from = "repo-root"
notes = ["Use this for CLI/config changes before broader cargo tests."]

[[profiles.foreman.checks]]
name = "format"
purpose = "Check Rust formatting."
command_template = "cargo fmt --check"
run_from = "repo-root"

[[profiles.foreman.reviews]]
name = "core-quality"
purpose = "Fresh-context review before handoff."
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt = "Focus on correctness, regression risk, and whether the focused tests prove the changed behavior."
# Optional: prompt_file = "prompts/foreman-core-review.md"
```

Inline `[profiles.<name>]` is intentionally the old profile primitive embedded in the config file. The section key supplies the profile name; the section body carries the important part: instructions, check guidance, and lightweight review guidance.

Review definitions are also guidance. HK should surface them to agents and include prompt file content when configured, but it should not dispatch reviews itself. If a profile lists multiple reviews, agents should dispatch them independently/in parallel when their harness supports it, then record accepted reviews with `hk review add`.

## Steps

1. Add config dataclasses/parser, probably in `src/harness_toolkit/kit/config.py`.
2. Reuse existing profile parsing by adapting inline profile tables into the existing profile schema.
3. Add profile catalog loading from built-ins + user inline profiles.
4. Add target resolution by normalized longest path prefix.
5. Add `hk profile resolve --target PATH --json`.
6. Update `hk checks --target PATH` to use the resolved profile if `--profile` was omitted.
7. Add docs and sample config covering harness-toolkit, dread, and foreman profiles.
8. Add tests for config path lookup, inline profile loading, resolution, checks defaulting, and no-config fallback.
9. Dogfood in temp dread and foreman clones with `HARNESS_KIT_CONFIG` pointing at a temp config.
10. Validate and review.

## Deferred

- Repo-level `.harness/harness.toml` precedence.
- Structured review backend config.
- Persistent sync ignore config.
- Auto-detection / scoring / command execution.
