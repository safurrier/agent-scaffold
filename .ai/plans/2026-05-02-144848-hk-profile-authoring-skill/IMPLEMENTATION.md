---
id: plan-implementation
title: Implementation Notes
description: >
  Notes for the Harness Kit profile-authoring skill slice.
---

# Implementation — hk-profile-authoring-skill

Added a new generated skill under `templates/.agent/skills/`:

- `harness-kit-profile-authoring/SKILL.md`
- `harness-kit-profile-authoring/references/profile-mining.md`
- `harness-kit-profile-authoring/references/examples.md`

The skill is generic and public-facing. It avoids user-specific absolute paths and
frames examples as scaffolded repo, Rust mise repo, and dotfiles repo patterns.

Also updated `docs/portable-workflow.md` to point agents at the generated skill
when no exact custom profile exists.
