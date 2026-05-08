---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-06 — Generic artifact attach is the right abstraction

The user agreed that artifact attachment should be generic rather than `transcript attach`. Implemented `hk artifact attach` so HK records real tool-produced files with hashes and handoff metadata.

## 2026-05-06 — Pi session transcript should usually be reference-only

Pi sessions are JSONL files under `~/.pi/agent/sessions/`, but current sessions can contain private conversation and tool output. Dogfood used `--no-copy` for the Pi session path so HK recorded source path, size, and sha256 without copying the contents into committed artifacts.

## 2026-05-06 — Codex review caught a real test gap

The first Codex review found that e2e legacy-removal tests still rejected any `attach` text in root help. The new nested `hk artifact attach` help text made those tests fail. Updated e2e checks to assert absence of the removed top-level `hk attach` command instead of banning the word globally, then reran Codex and got no blocking findings.
