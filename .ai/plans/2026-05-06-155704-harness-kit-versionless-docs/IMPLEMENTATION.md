---
id: plan-implementation
title: Implementation Notes
description: >
  Design and implementation notes for the docs-only slice.
---

# IMPLEMENTATION — harness-kit-versionless-docs

## Changes

- Renamed:
  - `docs/harness-kit-lifecycle-design.md` → `docs/harness-kit-lifecycle-design.md`
  - `docs/decisions/0008-harness-kit-ledger-first-local-assistant.md` → `docs/decisions/0008-harness-kit-ledger-first-local-assistant.md`
  - `docs/decisions/0009-harness-kit-lifecycle-first-cli.md` → `docs/decisions/0009-harness-kit-lifecycle-first-cli.md`
- Updated `mkdocs.yml` nav and cross-links.
- Reworded README, SPEC, portable workflow docs, design docs, ADR text, source help/docstrings, tests, templates, and repo-local skills to use Harness Kit / lifecycle language.
- Kept command removal facts but stopped framing them as HK1/HK2 migration.
- Replaced migration-guide wording with rollout/implementation wording in lifecycle docs and ADR metadata.
- Updated `AGENTS.md` with the durable rule that docs should not spend product surface on migration docs for the short-lived prototype.

## Scope boundary

The cleanup targets user-facing docs and repo-local agent guidance. Historical `.ai/plans` evidence from prior work can still preserve old terms as historical artifacts.
