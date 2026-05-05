---
id: plan-implementation
title: Implementation Notes
description: >
  Notes about what changed and why.
---

# IMPLEMENTATION — hk2-review-ux-pr-trial

## Review UX changes

- Generated agent snippets now use a `subagent` backend example and include a
  comment that review must come from a different reviewer or fresh-context
  subagent.
- `hk review add --help` now includes copy-pasteable examples for subagent/Codex
  review records and a fallback dangerous skip example.
- The `review add` docstring explicitly says same-agent implementation review
  does not count.
- New review records with obvious self-review identities are rejected with an
  actionable error that points to fresh-context review or dangerous skip.
- Readiness copy now distinguishes missing review from recorded-but-not-accepted
  review and tells the agent what to do next.

## Docs/context changes

- `AGENTS.md` now records the product rule: review UX should require independent
  or fresh-context review; heuristic detection is not the guarantee.
- `SPEC.md`, `README.md`, and `docs/harness-kit-2-design.md` now describe review
  as independent/fresh-context, not a generic self-entered note.

## Deferred

- `hk ready dangerously-skip ...` command shape remains a follow-up.
- PR-sized Discord/Discord-AI-shaped replay trial remains a follow-up after this
  UX patch lands.
