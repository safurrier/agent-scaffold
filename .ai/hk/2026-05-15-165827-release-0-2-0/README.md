# HK export: `2026-05-15-165827-release-0-2-0`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-15-165827-release-0-2-0 --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-15-165827-release-0-2-0`
- Branch: `release-v0.2.0`

## Context
- None recorded.

## Plan
- Cut v0.2.0 GitHub release after the initial v0.1.0: update project version and changelog for the accumulated HK lifecycle/profile/export improvements, validate release checklist, tag main, publish GitHub release notes, and reinstall the pinned latest tag.
- Release v0.2.0 as the first post-0.1.0 GitHub release: bump package version, add CHANGELOG.md, refresh pinned install/release docs, run release checklist, tag main, publish GitHub release, and verify pinned install.

## Decisions and spec reflection
- Use v0.2.0 rather than v0.1.1 because the accumulated changes include new HK lifecycle/profile/export semantics and command behavior, not just bug fixes.
  - Spec: not-needed: Spec/docs update not needed.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m contract`: pass (exit 0) — validates: Release docs/changelog/version metadata remain structurally valid — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Full quality gate before v0.2.0 release tag — `<local HK state not exported>`
- `uv run pytest tests/unit/test_cli.py::test_version_flag -q`: pass (exit 0) — validates: Version flag test updated for v0.2.0 — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate before v0.2.0 release tag after version test update — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Release checklist sync-check before v0.2.0 tag — `<local HK state not exported>`
- `uv build`: pass (exit 0) — validates: Release checklist source distribution and wheel build for v0.2.0 — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests after v0.2.0 release docs and changelog updates — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests after release review fixes to changelog and release checklist docs — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests after updating remaining pinned install docs to v0.2.0 — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate after release review fixes and remaining pinned install doc updates — `<local HK state not exported>`

## Readiness
- context: info — no context recorded; okay for trivial work, add hk context if it prevents rediscovery
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/getting-started.md, docs/portable-workflow.md, docs/release.md)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched README.md, docs/getting-started.md, docs/portable-workflow.md, +4 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched docs/getting-started.md, docs/portable-workflow.md, docs/release.md, +1 more)

## Review
- subagent / reviewer-fresh-context [codex-review]: Release review accepted after fixes. v0.2.0 metadata, README/docs pinned installs, version test, uv.lock, CHANGELOG, and release checklist docs are consistent; v0.1.0 is represented only as the historical pre-rename agent-scaffold release; no blockers remain. paths: README.md, docs/getting-started.md, docs/portable-workflow.md, +5 more. [accepted]
