---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-05-05 — Slice framing

- User wants one more HK2 pass before pausing.
- Sync direction: add one-shot explicit exclusions rather than persisted ignore config. `--exclude` can be repeated for multiple paths; a single `.pi` exclusion uses one flag.
- Spec direction: implement structured spec impact modes plus optional refs.
- Review direction: independent AI/tool review is preferred, fresh-context subagent is the minimum acceptable fallback. Add prompt guidance, but defer configurable review-source policy.
- Dogfood direction: less-guided PR-sized run so workers are not told the exact new features to use.

## 2026-05-05 — Review-default-on rerun

- Less-guided v4 showed 0/3 workers discovered `hk review prompt`.
- Strengthened status/help/docs wording: review required by default; preferred independent AI/tool reviewer; minimum fresh-context subagent; implementation-agent self-review does not count.
- V5 dogfood showed 3/3 workers ran `hk review prompt`, but 0/3 obtained an actual reviewer in the delegated-worker environment. All recorded `dangerously-skip review` explicitly.
- Conclusion: review policy/discovery improved; next gap is reviewer dispatch ergonomics.

## 2026-05-05 — Review dispatch hint smoke

- Added explicit wording: if a fresh-context review mechanism is available, dispatch `hk review prompt` to it now.
- Single-worker v6 foreman dogfood ran `hk review prompt` and recognized the dispatch expectation, but still reported no reviewer mechanism in the delegated-worker environment.
- Conclusion: wording is sufficient; actual review completion requires harness/tooling support for reviewer dispatch.

## 2026-05-05 — Harness review mechanism research

- Claude Code docs: fresh-context subagents are available through the `Agent` tool; older `Task` references remain aliases.
- Correction: Codex `/review` and `/agent` are slash commands, not tools, so they are not appropriate for harness-facing instructions.
- Initial Codex hint used `codex review --uncommitted -`, but dogfood v7 showed this local Codex CLI rejects that combination.
- Updated HK wording to stay harness-agnostic while giving tool-callable examples: Pi `subagent`, Claude Code `Agent`/legacy `Task`, Codex Shell tool running `codex review --uncommitted`.
- Added guidance to re-run `hk status` after review tools because Codex/Pi local state can appear after review and stale the sync checkpoint.

## 2026-05-05 — Documentation journey framing

- Read the vault note `Teach Don't Tell - Technical Documentation.md`: documentation should teach as a journey, not dump disconnected information.
- Reframed HK docs around the agent user story: add basic `AGENTS.md` directives, plan through normal human/agent back-and-forth, then hand the agreed intent to an implementation agent and tell it to use `hk`.
- Promoted the minimal agent loop (`start --plan`, `validate`, `status`, `ready`, `handoff`) and made the longer lifecycle a `hk status`-guided path rather than a memorized checklist.
- Persistent review backend config remains deferred.
