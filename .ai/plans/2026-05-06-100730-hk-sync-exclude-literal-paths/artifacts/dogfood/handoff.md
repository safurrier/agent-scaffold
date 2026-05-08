# Handoff

## Summary
- Work: `2026-05-06-101104-sync-exclude-literal`
- Branch: `feat/sync-exclude`
- Git SHA: `3b3dfce`
- Dirty: `true`
- Sync status: `synced`

## Context
- Dogfood repo intentionally has several untracked local-only paths outside .pi/.claude.

## Plan
- Verify hk sync --exclude accepts explicit untracked literal local paths without a hardcoded allowlist.

## Decisions and spec reflection
- Allow literal untracked local paths to be excluded when explicitly recorded and revalidated; tracked/staged/root/pathspec paths remain invalid.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `git status --short`: pass (exit 0) — validates: A direct git status proves the dogfood repo has one tracked edit plus three untracked local paths to exclude. — `/private/tmp/hk-sync-exclude-dogfood.KrcMCh/repo/.harness-local/harness-kit/root/work/2026-05-06-101104-sync-exclude-literal/artifacts/ev_20260506_101108_788162.transcript.log`

## Readiness
- Status: `ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- sync: pass — sync checkpoint fresh

## Review
- dogfood-manual / reviewer-fresh-context (sync-exclusion-ux): No blocking findings: explicit non-allowlisted untracked excludes are recorded and visible. [accepted]

## Sync exclusions
- dist, .cache/tool, src/scratch.py: Dogfood local-only generated output, tool cache, and scratch file intentionally excluded.
