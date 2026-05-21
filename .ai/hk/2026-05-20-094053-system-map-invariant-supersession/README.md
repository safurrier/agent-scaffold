# HK export: `2026-05-20-094053-system-map-invariant-supersession`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-20-094053-system-map-invariant-supersession --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-20-094053-system-map-invariant-supersession`
- Branch: `feat/system-map-invariant-supersession`

## Context
- None recorded.

## Plan
- Add .harness/system.toml system map support and loud invariant supersession decisions through hk decide --kind invariant-supersession.

## Decisions and spec reflection
- Use repo-root .harness/system.toml as the v1 system-map source of truth; profile checks remain authoritative for commands/readiness.
- Represent invariant overrides as hk decide --kind invariant-supersession rather than a new top-level hk invariant command.
  - Spec: updated: Spec/docs updated or verified.; refs: docs/system-map-authoring.md
  - Spec: updated: Spec/docs updated or verified.; refs: docs/system-map-authoring.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after system-map and invariant-supersession implementation plus invalid-map checks-view fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood full quality gate passes after lifecycle/status/checks changes — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood full quality gate passes after addressing PR review findings — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Fast gate/full quality gate passes after PR review fixes — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after target-level system_map support — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract docs/tests pass after target-level system_map docs updates — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood full quality gate passes after target-level system_map support — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after rebasing target-level system_map PR on main — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract docs/tests pass after rebase — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood/full quality gate passes after rebase — `<local HK state not exported>`
- `mise run sync-check -- --changed-hk-exports main...HEAD`: pass (exit 0) — validates: HK export sync-check passes after rebase — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after brief missing-profile resilience fix — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract docs/tests pass after brief resilience fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood/full quality gate passes after brief resilience fix — `<local HK state not exported>`
- `mise run sync-check -- --changed-hk-exports main...HEAD`: pass (exit 0) — validates: HK export sync-check passes after brief resilience fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after profile override target-map fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: HK dogfood/full quality gate passes after profile override target-map fix — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after profile override target-map fix — `<local HK state not exported>`
- `mise run sync-check -- --changed-hk-exports main...HEAD`: pass (exit 0) — validates: HK export sync-check passes after profile override target-map fix — `<local HK state not exported>`

## Readiness
- context: info — no context recorded; okay for trivial work, add hk context if it prevents rediscovery
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched docs/portable-workflow.md, docs/system-map-authoring.md)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/profiles/__init__.py, +11 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .ai/hk/2026-05-15-203300-readme-two-apps/README.md, .ai/hk/2026-05-15-203300-readme-two-apps/artifacts/README.md, README.md, +21 more)
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched .ai/hk/2026-05-15-203300-readme-two-apps/README.md, .ai/hk/2026-05-15-203300-readme-two-apps/artifacts/README.md, .ai/hk/2026-05-15-203300-readme-two-apps/meta.json)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched docs/portable-workflow.md, docs/system-map-authoring.md, src/harness_toolkit/kit/cli.py, +18 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/profiles/__init__.py, +11 more)

## Review
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers. Reviewer verified system-map checks integration and invariant supersession status/ready/handoff/review-prompt flow; noted invalid system maps should not emit authoritative matched invariants, which was fixed by surfacing findings without matches. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/profiles/applicability.py, tests/unit/test_system_map_checks_view.py, +34 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Accepted/no blockers. Fresh-context reviewer verified invariant-supersession decision validation, advisory checks output, invalid-map handling, and status/ready/handoff/review-prompt loudness; focused validation passed. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/profiles/applicability.py, tests/unit/test_system_map_checks_view.py. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers. Targeted follow-up verified PR bot fixes for status handoff action, decide help example, pathspec glob validation, and normalized supersession docs. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/readiness/policy.py, +4 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Accepted/no blockers. Targeted lifecycle follow-up verified invariant supersession readiness/status behavior and normalized docs path handling after PR review fixes. paths: src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/readiness/policy.py, +4 more. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers. Fresh-context reviewer verified target-level system_map parsing/resolution, target-config precedence over repo-local maps, brief/checks source consistency, repo-root-relative external map matching, invalid-map safety, and external supersession doc readiness behavior. paths: README.md, docs/portable-workflow.md, docs/system-map-authoring.md, +18 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Accepted/no blockers. Fresh-context lifecycle review verified target-level maps integrate with checks/brief and invariant-supersession readiness handles external docs without false failures. paths: README.md, docs/portable-workflow.md, docs/system-map-authoring.md, +18 more. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers after rebase. Prior fresh-context review covered target-level system_map behavior; rebase resolved README only and no code behavior changed. paths: .ai/hk/2026-05-15-203300-readme-two-apps/README.md, .ai/hk/2026-05-15-203300-readme-two-apps/artifacts/README.md, .ai/hk/2026-05-15-203300-readme-two-apps/meta.json, +21 more. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers. Targeted follow-up verified hk brief tolerates missing configured profiles while still loading target-level system_map. paths: src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/profiles/resolution.py, src/harness_toolkit/kit/profiles/__init__.py, +1 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Accepted/no blockers. Targeted lifecycle follow-up verified brief resilience and target-level map resolution independent of profile validity. paths: src/harness_toolkit/kit/local.py, src/harness_toolkit/kit/profiles/resolution.py, src/harness_toolkit/kit/profiles/__init__.py, +1 more. [accepted]
- subagent / reviewer-fresh-context [codex-review]: Accepted/no blockers. Targeted follow-up verified explicit --profile checks tolerate missing target profile while preserving target-level system_map use. paths: src/harness_toolkit/kit/profiles/catalog.py, src/harness_toolkit/kit/profiles/resolution.py, tests/unit/test_system_map_checks_view.py. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Accepted/no blockers. Targeted lifecycle follow-up verified checks_view no longer performs full profile resolution for system_map lookup. paths: src/harness_toolkit/kit/profiles/catalog.py, src/harness_toolkit/kit/profiles/resolution.py, tests/unit/test_system_map_checks_view.py. [accepted]
