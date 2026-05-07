---
id: plan-spec
title: Task Specification
description: >
  Requirements and constraints for this unit of work.
---

# Specification — agent-adoption-doc

## Problem

Users need a short user-level `AGENTS.md` directive for Harness Kit adoption, but
current guidance is either too verbose or buried in broader portable-workflow
material. The existing `hk instructions` command already exists and can provide a
better canonical snippet.

## Requirements

### MUST

- Add a focused agent adoption doc for user-level `AGENTS.md` setup.
- Keep the durable AGENTS.md block short enough to live in global/user context.
- Avoid hardcoding `--profile generic` in the user-level directive.
- Tell agents how to handle missing `hk` without trying to continue silently.
- Include generic dotfiles-managed setup steps for adopting the snippet later.
- Update `hk instructions` and tests so the CLI prints the new default snippet.

### SHOULD

- Preserve a repo-local/profile-specific snippet for users who want fuller local
  AGENTS.md guidance.
- Link the new doc from README and existing workflow docs.
- Validate with focused unit tests, docs build, and simple dogfood output.

## Constraints

- Do not add a new top-level command for this pass.
- Do not add file-mutating AGENTS.md installation behavior.
- Keep commit hygiene guidance generic; do not enumerate every possible local
  workflow/state directory.
