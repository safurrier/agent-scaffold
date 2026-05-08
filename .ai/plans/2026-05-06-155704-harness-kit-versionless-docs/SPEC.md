---
id: plan-spec
title: Slice Spec
description: >
  Behavioral envelope for this docs-only change.
---

# SPEC — harness-kit-versionless-docs

## Goal

Remove public HK1/HK2 product framing from Harness Kit docs. The shipped workflow should read as Harness Kit, not as a second major version replacing a short-lived prototype.

## Requirements

- User-facing docs and CLI help should say Harness Kit / lifecycle workflow rather than Harness Kit 2, HK2, HK1, or HK 1.0.
- Do not add an HK1 migration guide.
- Keep factual removed-command guidance where useful, but frame it as removed portable plan-artifact commands.
- Rename public design/ADR filenames and MkDocs nav away from `harness-kit-2` / `hk-2`.
- Remove migration-guide framing from lifecycle docs; use rollout/implementation wording where historical design notes need it.
- Leave unrelated version strings alone, such as generated context-engineering version comments or GitHub Action versions.

## Non-goals

- No source behavior changes.
- No rewrite of historical `.ai/plans` evidence directories.
