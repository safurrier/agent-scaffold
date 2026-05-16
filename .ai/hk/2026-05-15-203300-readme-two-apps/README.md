# HK export: `2026-05-15-203300-readme-two-apps`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-15-203300-readme-two-apps --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-15-203300-readme-two-apps`
- Branch: `readme-improver-20260515195109-harness-toolkit`

## Context
- None recorded.

## Plan
- Rebalance README around hk and harness-scaffold as two separate apps; reduce scaffold-forward framing.

## Decisions and spec reflection
- README structure updated to present harness-toolkit as a monorepo with two separate apps: hk first for existing repos, harness-scaffold second for new repos. No SPEC update needed because this is README positioning only.
  - Spec: not-needed: Spec/docs update not needed.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `bash -lc 'uv run hk --help >/tmp/hk-help.out && uv run harness-scaffold --help >/tmp/harness-scaffold-help.out && git diff --check'`: pass (exit 0) — validates: README-only validation: CLI help for both apps and markdown whitespace checks passed — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Fast gate for README-only change — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Fast gate for README-only change with trusted worktree config — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate for README-only change after syncing local dependencies — `<local HK state not exported>`

## Readiness
- context: info — no context recorded; okay for trivial work, add hk context if it prevents rediscovery
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched README.md)

## Review
- subagent / reviewer-fresh-context [codex-review]: Fresh-context reviewer checked the README-only diff against user feedback. No blockers. README now opens with hk and harness-scaffold as separate apps, gives hk prominence before scaffold docs, and keeps scaffold details scoped. Reviewer suggested showing direct harness-scaffold init; follow-up edit addressed that. paths: README.md. [accepted]
