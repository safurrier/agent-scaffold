---
id: plan-implementation
title: Implementation Notes
description: >
  Design and implementation notes for the slice.
---

# IMPLEMENTATION — hk-session-artifacts-skill

## Skill files

- `.agent/skills/hk-session-artifacts/SKILL.md`
  - exact-path-first workflow;
  - source-specific attach recipes;
  - safety rules for copy vs `--no-copy`;
  - candidate helper usage.
- `.agent/skills/hk-session-artifacts/references/session-stores.md`
  - Pi session directory precedence and observed repo-scoped layout;
  - Claude stream JSONL and persisted project session layout;
  - Codex review JSONL and persisted date-based session layout.
- `.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py`
  - discovery-only JSON helper for `--source pi|claude|codex`;
  - prints warnings and candidates with path, size, mtime, reason, and confidence;
  - sorts newest-first for inspection but never attaches or chooses a file.

## Design choice

The skill teaches agents to attach exact paths with `hk artifact attach` rather than introducing wrappers around Codex/Claude/Pi or making HK guess latest sessions. A small candidate helper is included because session-store discovery is repetitive and path-shape-specific, but selection remains explicit and auditable.

## Reviewer-driven adjustments

- Changed generic attach example to use source-specific kind placeholders rather than always `pi-session-transcript`.
- Added an explicit kind mapping.
- Added a warning that newest-first helper output is only an inspection aid.
- Added a count/sanity check to the Pi `--session-dir` recipe before attaching.
- Fixed Claude project key normalization so `<USER>` path segments match Claude's hyphenated project directory.
