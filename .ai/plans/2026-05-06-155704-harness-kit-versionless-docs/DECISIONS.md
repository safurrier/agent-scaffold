---
id: plan-decisions
title: Decisions
description: >
  Decision log for the docs-only slice.
---

# DECISIONS — harness-kit-versionless-docs

## What Changed

- Public docs and CLI help now refer to Harness Kit and the Harness Kit lifecycle instead of HK1/HK2 version framing.
- Design and ADR filenames/nav were renamed to versionless lifecycle names.
- Removed-command references now describe portable plan-artifact commands, not a version migration.
- Lifecycle docs use rollout/implementation wording instead of migration-guide framing.

## Why

- The previous workflow was a short-lived prototype, so public docs should not teach a major-version migration story.
- Agents and humans should see one current Harness Kit product surface.
- Versionless naming keeps the README, MkDocs nav, SPEC, and skills aligned with the launch framing.

## Where Reflected

- `AGENTS.md`
- `README.md`
- `SPEC.md`
- `mkdocs.yml`
- `docs/portable-workflow.md`
- `docs/harness-kit-lifecycle-design.md`
- `docs/AGENTS.md`
- `docs/decisions/0008-harness-kit-ledger-first-local-assistant.md`
- `docs/decisions/0009-harness-kit-lifecycle-first-cli.md`
- `.agent/skills/hk-pr-sized-dogfood/SKILL.md`
- `.agent/skills/hk-session-artifacts/SKILL.md`
- `src/harness_toolkit/kit/`
- `tests/`
- `templates/.agent/skills/harness-kit-profile-authoring/`

## Promotion

No ADR needed; this is a naming/framing correction to existing docs.
