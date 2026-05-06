---
id: plan-decisions
title: Decisions
description: >
  Decision log for the slice.
---

# DECISIONS — hk-session-artifacts-skill

## What Changed

- Added a repo-local `hk-session-artifacts` skill for finding and attaching Pi, Claude Code, and Codex transcripts with `hk artifact attach`.
- Added a discovery-only candidate helper script for session stores.
- Added dogfood evidence showing exact-path transcript attachment for all three sources.

## Why

- The user preferred a skill-guided workflow over shell wrappers around Codex, Claude, and Pi.
- The desired integration boundary is: harness/tool produces an exact transcript path, then agent attaches it with HK.
- Latest-session heuristics are risky when multiple agents or tools run concurrently, so helper output should only assist inspection.

## Where Reflected

- `.agent/skills/hk-session-artifacts/SKILL.md`
- `.agent/skills/hk-session-artifacts/references/session-stores.md`
- `.agent/skills/hk-session-artifacts/scripts/find_session_candidates.py`
- `.ai/plans/2026-05-06-140442-hk-session-artifacts-skill/artifacts/dogfood/`

## Promotion

- No ADR; this is repo-local skill/product workflow guidance plus dogfood evidence.
