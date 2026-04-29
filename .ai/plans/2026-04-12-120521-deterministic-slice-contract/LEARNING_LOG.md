---
id: plan-learning-log
title: Learning Log
description: >
  Dev diary. Append timestamped entries for problems, adaptations,
  user feedback, and surprises. See _example/ for a reference.
---

# Learning Log

## 2026-04-12 12:20 — Design converged on "hard contract, soft execution"

The key simplification from the interview was to stop treating skills and
checks as the same thing. The scaffold should enforce outputs
(plan/spec/evidence/review) with `mise`, while skills remain workflow helpers
that can vary by harness.

## 2026-04-12 12:25 — Keep ADRs available but no longer the default

The user still wants readable decision flow, but not "ADR fluff." The design
direction is now:
- plan-local `DECISIONS.md` as the staging area
- repo-level append-only decision ledger for most durable changes
- ADRs reserved for larger invariants or boundary changes

## 2026-04-12 14:05 — Freshly initialized repos produce non-slice noise

The first generated-repo `sync-check` surfaced `uv.lock`, `test-results/`, and
`scripts/__pycache__/` as false positives when no active slice existed. The
contract needed to distinguish bootstrap/runtime noise from meaningful work.

## 2026-04-12 14:15 — Generated-repo validation needed a full reviewer leg

The worker subagent completed the Rust slice cleanly, but `sync-check` could
not pass until a second reviewer context updated `REVIEW.md` and
`META.yaml review_backend`. That confirmed the split between implementer output
and external review output is doing real work.

## 2026-04-12 15:30 — Stacked branches need explicit review scope capture

This branch sits on older Rust-stack commits, so a stock `main...HEAD`
codex-review would have reviewed unrelated history. The safe pattern for
external review here is to capture a `HEAD -> current working tree` patch under
the active plan artifacts and review that exact patch.

## 2026-04-12 15:55 — External review found validator loopholes

The first Codex review run turned up three real enforcement gaps:
- unchecked placeholder TODO items still counted as meaningful content
- any fenced validation block counted as proof, even without commands
- artifact manifest paths could escape the active plan directory with `..`

Those holes all lived in the shared contract layer, so tightening the helpers
and adding focused unit coverage was a better response than adding more process.

## 2026-04-12 17:10 — Codex CLI review artifacts are safer when the scope is captured first

The reliable part of the Codex review flow here was not the CLI writing its own
report every time. The reliable part was persisting `changed-files.txt`,
`commits.txt`, `diff.patch`, and the review prompt under the active plan
before invoking Codex. That made the external review auditable even when the
CLI needed multiple attempts to finish cleanly under this harness.

## 2026-04-12 18:05 — Final scaffold validation should happen after review-driven hardening

The branch was not really done when the generated repo proof passed. The last
useful step was validating the scaffold repo itself after the external Codex
review had forced tighter TODO, validation, and reviewer checks. That sequence
proved the new contract on both the generated repo and the scaffold that emits
it.
