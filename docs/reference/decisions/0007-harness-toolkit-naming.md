---
id: harness-toolkit-adr-0007
title: ADR 0007 — Harness Engineering Toolkit Naming
description: >
  Names the product family, portable CLI, and starter template after the
  Harness Engineering Toolkit boundary.
index:
  - id: decision
    keywords: [harness-toolkit, hk, harness-scaffold, naming, cli]
  - id: consequences
    keywords: [rename, product-boundary, portability, compatibility]
---

# ADR 0007: Harness Engineering Toolkit Naming

**Status**: Accepted
**Date**: 2026-05-02
**Deciders**: Alex Furrier
**Generated from**: Naming brainstorm and implementation slice
**Plan**: `.ai/plans/2026-05-02-083917-harness-kit-naming/`

---

## Context

The repo had grown two related but distinct products:

1. A starter template for new agent-ready repositories.
2. A portable CLI for applying planning, validation, and handoff workflows to
   existing repositories without committing scaffold files.

The old names blurred that boundary. `agent-scaffold` described the template but
not the broader tool family. `agent-workflow` described the portable CLI but felt
generic and did not carry the harness-engineering framing. `agent-harness` or
`harness` fit the theme but conflicted with common usage: Claude Code, Codex, Pi,
Cursor, and similar coding environments are themselves agent harnesses.

## Decision

Adopt **Harness Engineering Toolkit** as the umbrella/product-family name.

Use these names for the two concrete surfaces:

| Surface | Name | Command |
|---|---|---|
| Portable workflow toolkit | `harness-kit` | `hk` and `harness-kit` |
| Starter template | `harness-scaffold` | `harness-scaffold` |

The Python package is named `harness-toolkit` and uses the import package
`harness_toolkit` so both surfaces can ship together while the project is small.

Docs should describe the split as:

> Use `hk` when adding the workflow to an existing repo. Use `harness-scaffold`
> when starting a new repo with the workflow, task contract, docs, and CI already
> wired in.

## Consequences

**Positive:**

- The daily portable CLI is short enough for repeated agent/human use: `hk`.
- The readable long name, `harness-kit`, anchors docs and package metadata.
- `harness-scaffold` keeps the template action clear while fitting the product
  family.
- The naming avoids implying that the project is itself a coding harness runtime.

**Negative / Trade-offs:**

- This is a breaking rename from the earlier `agent-scaffold` and
  `agent-workflow` command names.
- Existing docs, tests, generated snippets, and task wrappers must move together
  to avoid mixed vocabulary.
- Historical ADR IDs may still include `agent-scaffold`; those are treated as
  historical identifiers, not current product names.

## Alternatives Considered

| Alternative | Reason not chosen |
|---|---|
| Keep `agent-scaffold` and `agent-workflow` | Accurate enough but did not express the Harness Engineering Toolkit boundary |
| `agent-harness` / `harness` | Too easy to confuse with Claude Code, Codex, Pi, Cursor, or other agent harness runtimes |
| `harness-eng-toolkit` as the command | Clear as a phrase, too long for a daily CLI |
| `agent-loop` / `agent-plan` / `agent-slice` | Useful descriptors, but weaker product-family framing |
| `baton` / `rig` | Memorable, but less explicit than `hk` / `harness-kit` |
