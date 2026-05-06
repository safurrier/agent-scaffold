# Profile Mining Reference

## Goal

Extract the validation contract a competent maintainer already follows, then
encode it as `hk` profile checks. A profile should tell an agent what to run and
when, while leaving execution in the normal shell loop.

## Source Authority

1. **CI workflows** — merge-blocking truth. Mine `.github/workflows/*`,
   Buildkite config, GitLab CI, or equivalent.
2. **Hooks** — local commit/push truth. Check `.pre-commit-config.yaml`,
   `lefthook.yml`, Husky config, tracked hook installers, and documented local
   pre-push commands.
3. **Agent/context docs** — fastest useful loop. Read root and nested
   `AGENTS.md`, `CLAUDE.md`, `README.md`, and module docs.
4. **Task runners** — available validation surfaces. Inspect `.mise.toml`,
   `justfile`, `Makefile`, `package.json`, `pyproject.toml`, `tox.ini`, and
   language-specific task definitions.
5. **Recent evidence** — what actually worked. Check recent PR descriptions,
   plan `VALIDATION.md`, release docs, or CI debug docs when available.

When sources conflict, report the conflict and prefer CI for merge parity, then
repo AGENTS for the local fast loop. When a repo spans multiple stacks, preserve
that shape in the profile with separate checks per language, CI job, or task
wrapper instead of forcing the repo into one built-in profile.

## Mining Commands

Use targeted reads and searches; do not run heavy checks just to discover them.

```bash
find .github -maxdepth 3 -type f -print 2>/dev/null | sort
find . -maxdepth 3 \( -name '.pre-commit-config.yaml' -o -name 'lefthook.yml' -o -name 'justfile' -o -name 'Makefile' -o -name 'package.json' -o -name 'pyproject.toml' -o -name '.mise.toml' \) -print
rg -n "mise run|uv run|pytest|cargo test|go test|ruff|mypy|ty|pre-commit|lint|typecheck|verify|validate|test" AGENTS.md README.md docs .github .mise.toml pyproject.toml package.json justfile Makefile 2>/dev/null
```

Add ecosystem-specific searches only when the repo needs them.

## Check Taxonomy

Use names that describe the decision the agent must make.

| Check | Use |
|---|---|
| `fast-gate` | Default pre-handoff validation; should be practical in most sessions. |
| `focused-tests` | Smallest test path/selector for the touched area. |
| `lint` / `format-check` | Static style/format validation. |
| `typecheck` | Static type validation. |
| `ci-parity` | Commands matching merge-blocking CI; may be heavier than fast-gate. |
| `heavy-gate` | Broad confidence before merge, release, or risky runtime changes. |
| `apply` | Applies generated/local config when source changes need deployment. |
| `drift-check` | Detects generated/config drift after template changes. |
| `handoff` | Runs `hk sync && hk ready` for HK2 lifecycle state; verifies recorded evidence, not validation execution. |

## TOML Draft Pattern

```toml
name = "<repo-or-module>-root"
title = "<Repo Or Module> Root"
summary = "Validation contract for <repo/module>."
target_hint = "Use --target <repo-or-module-path>."

instructions = "Use this profile for work under <repo/module>. Run validation commands directly and record exact command/result evidence in VALIDATION.md before handoff."

[[checks]]
name = "fast-gate"
purpose = "Run the repo's fast local validation gate before handoff."
command_template = "<command>"
run_from = "repo-root"
notes = ["Source: <file or CI job>."]

[[checks]]
name = "focused-tests"
purpose = "Run the smallest focused test that covers the change."
command_template = "<command with placeholder>"
run_from = "repo-root"
required_inputs = ["test_path_or_selector"]

[[checks]]
name = "handoff"
purpose = "Validate portable workflow evidence and review state."
command_template = "hk sync --target <target> --json && hk ready --target <target> --json"
run_from = "current-directory"
notes = ["This checks recorded evidence; it does not rerun validation."]
```

## Proposal Guardrails

- Label uncertain commands as proposed and cite why they seem appropriate.
- Do not invent repo-specific wrappers that do not exist.
- Do not choose a language built-in profile as authoritative when repo-specific
  CI or task contracts exist.
- For Python/Rust, Python/Node, or other mixed-stack repos, cite the closest
  built-in profile only as a fallback and draft a repo-specific profile when CI
  or task runners define recurring checks for more than one stack.
- For custom profiles, include `--profiles-dir <profiles-dir>` in handoff commands;
  `hk` only loads built-ins when the flag is omitted.
- Do not silently create profiles. Ask before writing the TOML file.
- If the user declines profile creation, continue with the closest built-in
  profile and note the limitation once.
