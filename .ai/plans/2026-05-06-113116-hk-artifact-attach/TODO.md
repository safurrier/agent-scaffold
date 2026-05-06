---
id: plan-todo
title: Task List
description: >
  Checkable tasks for this unit of work. Check off as you go.
  See _example/ for a reference.
---

# TODO — hk-artifact-attach

- [x] Document the preference for generic `artifact attach` in `AGENTS.md`.
- [x] Add HK2 artifact attach local primitive that copies or references a source file.
- [x] Record artifact metadata in the lifecycle ledger: kind, label, source path, artifact path, sha256, size, copied flag, redaction.
- [x] Add `hk artifact attach --path ... --kind ...` CLI.
- [x] Render attached artifacts in full and PR handoffs.
- [x] Validate attached artifact event shape when reading ledger JSONL.
- [x] Add unit/CLI coverage for copy, no-copy, missing active work, invalid path/kind, and handoff rendering.
- [x] Update product docs.
- [x] Run Codex review and address findings.
- [x] Dogfood attaching a Codex review transcript and a Pi session transcript reference.
