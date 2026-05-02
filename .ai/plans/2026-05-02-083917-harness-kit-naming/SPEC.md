---
id: plan-spec
title: Harness Kit Naming Specification
description: >
  Product naming and boundary notes for separating the portable workflow CLI
  from the starter-template repo.
---

# Specification — harness-kit-naming

## Problem

`agent-scaffold` currently contains two related but distinct product ideas:

1. A starter template / scaffold for new agent-ready repositories.
2. A portable workflow CLI for applying planning, validation, and handoff loops
   to existing repositories without committing scaffold files.

The current portable CLI name, `agent-workflow`, is descriptive but bland. Earlier
brainstorming considered `agent-harness` / `harness`, but that creates ambiguity
with coding harnesses such as Claude Code, Codex, Pi, and Cursor. The new naming
should preserve the "harness engineering" framing while making the repo/product
boundaries clearer.

## Proposed Product Boundary

Use **Harness Engineering Toolkit** as the umbrella/category name:

```text
Harness Engineering Toolkit
├── harness-kit / hk        # portable CLI/tooling layer
└── harness-scaffold        # starter template for new projects
```

Definitions:

- **Harness Engineering Toolkit**: the broader philosophy/tool suite for making
  agent work repeatable, inspectable, and handoff-safe across coding harnesses.
- **harness-kit**: the portable toolkit and CLI for existing repos.
- **hk**: the short daily command for `harness-kit`.
- **harness-scaffold**: the batteries-included template repo for new projects.

## Requirements

### MUST

- Preserve a clear distinction between the portable CLI and the starter template.
- Avoid making users think this project is itself an agent harness/runtime.
- Keep the daily CLI short enough for frequent use.
- Keep the long name descriptive enough for docs, package metadata, and search.
- Leave room for future split into separate repos/packages.

### SHOULD

- Prefer `hk` as the daily command.
- Prefer `harness-kit` as the readable CLI/package name for portable workflow
  tooling.
- Consider renaming `agent-scaffold` to `harness-scaffold` if the project will be
  discovered primarily through the Harness Engineering Toolkit brand.
- Keep temporary compatibility aliases only if needed by existing users.

## Open Questions

- Should `agent-scaffold` be renamed immediately to `harness-scaffold`, or should
  docs first introduce the umbrella and CLI split while the repo name remains?
- Should `agent-scaffold` remain as a legacy command after a repo/package rename?
- Should `agent-workflow` remain as a temporary alias for the portable CLI?
- Is the canonical long CLI command `harness-kit`, with `hk` as alias, or is `hk`
  the only documented command?

## Constraints

- This slice only persists the naming direction and decision context. It does not
  perform the rename.
- Existing uncommitted work on branch `spike/portable-workflow` should not be
  disturbed.
- Any later rename should update docs, `pyproject.toml` scripts, generated
  snippets, tests, README/SPEC references, and compatibility guidance together.
