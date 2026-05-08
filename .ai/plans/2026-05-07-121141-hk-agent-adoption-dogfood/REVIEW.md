---
id: plan-review
title: Review Evidence
description: >
  Review notes for this slice.
---

# REVIEW — hk-agent-adoption-dogfood

## Review Context

- Mode: external
- Reviewer: Codex dogfood worker behavior plus local synthesis
- Backend: codex exec
- Scope: dogfood-skill variant and trial behavior

## Rubrics

- core-quality
- dogfood-validity

## Findings

- The dogfood variant uses a temp repo and checkout-local HK wrapper, so it does not mutate source repos.
- The trial prompt did not mention HK or AGENTS.md, so the observed HK usage is attributable to repo context loading.
- The trial found one actionable HK UX issue: agents may pass profile flags to `hk start` after seeing profile-aware commands.

## Disposition

- Keep the new dogfood variant in the repo-local skill.
- Record the profile-flag confusion as a possible follow-up, not a blocker for this PR.
