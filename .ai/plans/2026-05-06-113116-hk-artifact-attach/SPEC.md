---
id: plan-spec
title: Slice Spec
description: >
  Behavioral envelope for this change.
---

# SPEC — hk-artifact-attach

## Goal

Add a generic HK2 artifact attachment workflow so agents can programmatically attach real files produced by harnesses and tools, including agent session transcripts, Codex review transcripts, HAR files, and raw validation artifacts.

## Requirements

- Provide a shell-first command:

```bash
hk artifact attach --path FILE --kind KIND [--label TEXT] [--redaction none|unknown|external] [--no-copy] --target . --json
```

- Require active HK2 work.
- Require `FILE` to exist and be a file.
- Validate `KIND` as a simple machine-readable token.
- Default to copying the source file into the active work's `artifacts/` directory.
- Support `--no-copy` for sensitive or huge files, recording source path/hash metadata only.
- Compute a streaming sha256 and size for every attached file.
- Append structured metadata to `events.jsonl`.
- Render attached artifact metadata in `hk handoff` and `hk handoff --format pr`.
- Do not ask the agent to narrate its own transcript into HK; HK records real files produced by tools.

## Dogfood goals

- Attach a copied Codex review JSONL transcript.
- Attach the current Pi session JSONL by path/hash only with `--no-copy`, because the current session may contain private content.
