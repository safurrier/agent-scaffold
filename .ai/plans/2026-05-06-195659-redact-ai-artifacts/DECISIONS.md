---
id: plan-decisions
title: Decisions
description: >
  Decision log for this redaction pass.
---

# DECISIONS — redact-ai-artifacts

## What Changed

- `.ai` plan/evidence artifacts were redacted for personal paths, personal identifiers, and requested work/org terms.
- High-signal secret scans were added as validation evidence.
- Review was handled as a deterministic local audit rather than external LLM review.

## Why

- `.ai` artifacts are committed handoff evidence and can contain raw command transcripts, temp paths, or dogfood notes.
- The user explicitly asked for a final sensitive-info pass before merge.
- Sending raw artifacts to an external reviewer would conflict with the redaction goal.

## Where Reflected

- `.ai/plans/`
- `.ai/plans/2026-05-06-195659-redact-ai-artifacts/artifacts/redaction-audit.log`

## Promotion

No ADR needed; this is a privacy cleanup of plan/evidence artifacts.
