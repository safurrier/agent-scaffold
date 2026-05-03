# Decisions

## What Changed

- Added a generated `harness-kit-profile-authoring` skill under `templates/.agent/skills/`.
- Added reference material for mining validation contracts from CI, hooks, repo docs, task runners, and recent evidence.
- Added generic examples for scaffolded repos, Rust mise repos, and dotfiles repos.
- Updated portable workflow docs and the bundled skill index to mention the new skill.

## Why

- Agents need reusable guidance for deciding when built-in `hk` profiles are only fallbacks.
- Agents need a safe workflow for proposing custom profile TOML without silently writing user config.
- The generic workflow belongs in Harness Toolkit, while user-specific managed profiles can live in dots.

## Where Reflected

- `templates/.agent/skills/harness-kit-profile-authoring/SKILL.md`
- `templates/.agent/skills/harness-kit-profile-authoring/references/profile-mining.md`
- `templates/.agent/skills/harness-kit-profile-authoring/references/examples.md`
- `templates/.agent/skills/README.md`
- `docs/portable-workflow.md`

## Promotion

- No ADR needed; this is generated skill guidance for an existing Harness Kit profile workflow.
