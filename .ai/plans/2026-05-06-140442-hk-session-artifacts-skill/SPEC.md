---
id: plan-spec
title: Slice Spec
description: >
  Behavioral envelope for this change.
---

# SPEC — hk-session-artifacts-skill

## Goal

Create an agent-facing skill that helps agents find and attach Pi, Claude Code, and Codex session/review transcripts to active HK2 work using `hk artifact attach`.

## Requirements

- Teach agents to prefer exact transcript paths produced by the harness/tool invocation.
- Avoid making HK infer or attach the latest Pi/Claude/Codex session by default.
- Provide source-specific recipes for:
  - Pi child sessions with explicit `--session-dir`;
  - Claude headless stream JSONL capture;
  - Codex review/session JSONL capture.
- Provide fallback candidate discovery that is explicitly heuristic and discovery-only.
- Candidate helper must not mutate files or call `hk artifact attach` automatically.
- Instruct agents to confirm candidates by repo scope, timestamp, prompt, session id, or file contents before attaching.
- Dogfood must attach copied transcript files for Pi, Claude, and Codex using exact paths.

## Non-goals

- No HK core latest-session detection.
- No shell wrappers that replace Codex/Claude/Pi invocation patterns.
- No agent-written pseudo-transcripts.
