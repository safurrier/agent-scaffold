---
id: plan-spec
title: Slice Spec
description: >
  Behavioral envelope for this redaction pass.
---

# SPEC — redact-ai-artifacts

## Goal

Redact potentially sensitive content from committed `.ai` plan/evidence artifacts before merge.

## Requirements

- Replace personal absolute paths with placeholders such as `<USER_HOME>`, `<REPO_ROOT>`, `<OLD_REPO_ROOT>`, `<PRIVATE_VAULT_PATH>`, and `<TMPDIR>`.
- Replace explicitly requested work/org terms with `<REDACTED_ORG>`.
- Replace personal identifiers found in `.ai` artifacts with placeholders.
- Search for high-signal secret/token patterns and confirm no unredacted matches remain.
- Preserve plan-contract validity.

## Non-goals

- Do not rewrite product source behavior for redaction.
- Do not send potentially sensitive artifact contents to external reviewers.
- Do not rewrite historical plan directory slugs unless required by a check.
