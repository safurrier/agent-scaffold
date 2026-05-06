---
id: plan-implementation
title: Implementation Notes
description: >
  Design and implementation notes for the slice.
---

# IMPLEMENTATION — hk-artifact-attach

## Code changes

- Added `ArtifactResult` to `src/harness_toolkit/kit/local.py`.
- Added `attach_artifact()` local primitive:
  - validates active work;
  - validates source path exists and is a file;
  - validates artifact kind token;
  - computes streaming sha256 and file size;
  - copies the file into `work/<work-id>/artifacts/` by default;
  - supports `copy=False` for reference-only attachments;
  - appends an `artifact_attached` lifecycle event.
- Added `ArtifactAttachRequest` and `LifecycleApp.attach_artifact()` in `src/harness_toolkit/kit/app/lifecycle.py`.
- Added `hk artifact attach` CLI in `src/harness_toolkit/kit/cli.py`.
- Added strict JSONL shape validation for `artifact_attached` events in `src/harness_toolkit/kit/ledger/store.py`.
- Added attached artifact sections to full and PR handoff rendering in `src/harness_toolkit/kit/rendering/handoff.py`.

## Test changes

- Added unit coverage for copied artifact attachments and handoff rendering.
- Added unit coverage for `--no-copy` style reference-only attachments.
- Added error coverage for missing active work, missing file, and invalid kind.
- Added CLI JSON coverage for `hk artifact attach`.
- Updated legacy `hk attach` removal tests to distinguish the removed top-level command from the new nested `hk artifact attach` subcommand/help text.

## Pi session discovery note

Pi stores session JSONL files under `~/.pi/agent/sessions/` by default, configurable via `PI_CODING_AGENT_SESSION_DIR`, `--session-dir`, or `settings.json` `sessionDir`. In this environment, the current harness-toolkit session was discoverable as the latest modified JSONL under the repo-scoped session directory. The dogfood records it with `--no-copy` so private session contents are not copied into committed artifacts.
