# HK export: `2026-05-14-155056-foreman-export-status`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-14-155056-foreman-export-status --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-14-155056-foreman-export-status`
- Branch: `foreman-export-status`
- Git SHA: `5d2ab2e`
- Dirty: `true`
- Sync status: `synced`

## Context
- GitHub issue #19 asks Foreman to consume HK handoff export state without parsing stderr or running mutating commands. Foreman should use hk brief --json for cards, hk handoff --json for live previews, and copy explicit export commands.

## Plan
- Expose read-only HK workspace/export status for Foreman: add Git/worktree facts and handoff export status to hk brief --json, and make hk export --format handoff-dir --check --json return structured expected failure states without mutating the repo.

## Decisions and spec reflection
- Expose Foreman-friendly read-only status through existing HK surfaces: hk brief --json gains Git/worktree facts and handoff_export status, hk export --format handoff-dir --check --json returns structured expected failure states, and hk handoff --json remains the live preview path. This avoids mutating repo exports from dashboards.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest tests/unit/test_harness_kit_2.py -k 'brief or export' -q`: pass (exit 0) — validates: Focused tests cover read-only brief Git/worktree facts, handoff export status, and structured export check JSON for missing/fresh/stale states. — `<local HK state not exported>`
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs and SPEC changes satisfy frontmatter/navigation contract tests. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_harness_kit_2.py -k 'brief or export' -q`: pass (exit 0) — validates: Focused tests pass after fixing external-state command hints and structured invalid export JSON behavior. — `<local HK state not exported>`
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs and SPEC changes still satisfy docs contract tests after Foreman export status updates. — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Full quality gate passes for Foreman-oriented brief/export status implementation. — `<local HK state not exported>`
- `env UV_FROZEN=true UV_INDEX_URL=https://pypi.org/simple mise run check`: fail (exit 1) — attempted to validate: Full quality gate passes for Foreman-oriented brief/export status implementation with uv frozen to avoid local private-index lock churn. — `<local HK state not exported>`
- `env UV_INDEX_URL=https://pypi.org/simple mise run check`: pass (exit 0) — validates: Full quality gate passes for Foreman-oriented brief/export status implementation using public PyPI index; uv.lock registry URL churn is reverted after validation. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; uv run pytest tests/unit/test_harness_kit_2.py -k "brief or export" -q; git checkout -- uv.lock'`: pass (exit 0) — validates: Focused tests pass after final external-state hint fix without leaving uv.lock registry churn. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; uv run pytest tests/contract/test_docs_contract.py -q; git checkout -- uv.lock'`: pass (exit 0) — validates: Docs and SPEC changes satisfy docs contract tests after final edits without leaving uv.lock registry churn. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; hk brief --target . --json | jq -e ".git.available == true and (.handoff_export.state | type == \"string\")" >/dev/null; if hk export --format handoff-dir --check --target . --json >/tmp/hk-export-status.json; then :; else test $(jq -r .state /tmp/hk-export-status.json) = missing; fi; git checkout -- uv.lock'`: pass (exit 0) — validates: CLI smoke verifies brief exposes Git/export status and export check JSON reports structured missing state. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; env UV_INDEX_URL=https://pypi.org/simple mise run check; git checkout -- uv.lock'`: pass (exit 0) — validates: Full quality gate passes for Foreman-oriented brief/export status implementation using public PyPI index; command reverts local uv.lock registry churn before exit. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; uv run pytest tests/unit/test_harness_kit_2.py -k "brief or export" -q; git checkout -- uv.lock'`: pass (exit 0) — validates: Focused tests pass after correcting linked-worktree detection to avoid separate-git-dir/submodule false positives. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; env UV_INDEX_URL=https://pypi.org/simple mise run check; git checkout -- uv.lock'`: pass (exit 0) — validates: Full quality gate passes after correcting Git/worktree facts and export status behavior; command reverts local uv.lock registry churn before exit. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; uv run pytest tests/contract/test_docs_contract.py -q; git checkout -- uv.lock'`: pass (exit 0) — validates: Docs and SPEC changes satisfy docs contract tests after final Git/worktree metadata fix. — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail; hk brief --target . --json | jq -e ".git.available == true and (.git.git_dir | type == \"string\") and (.handoff_export.state | type == \"string\")" >/dev/null; if hk export --format handoff-dir --check --target . --json >/tmp/hk-export-status.json; then :; else jq -e ".state | IN(\"missing\", \"stale\", \"invalid\", \"no-active-work\")" /tmp/hk-export-status.json >/dev/null; fi; git checkout -- uv.lock'`: pass (exit 0) — validates: CLI smoke verifies final brief Git/worktree metadata and handoff export status JSON surfaces. — `<local HK state not exported>`

## Readiness
- Status: `ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/portable-workflow.md)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/client.py, +1 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched README.md, SPEC.md, docs/portable-workflow.md, +5 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched SPEC.md, docs/portable-workflow.md, src/harness_toolkit/kit/app/lifecycle.py, +4 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/client.py, +1 more)
- sync: pass — sync checkpoint fresh

## Review
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): Fresh-context lifecycle review found no blockers for read-only brief Git/worktree facts, structured handoff export status, invalid export JSON states, external-state command hints, docs, and tests. paths: README.md, SPEC.md, docs/portable-workflow.md, +6 more. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context (agent-friendly-cli): Agent-friendly CLI review found no blockers after fixes. Verified --no-local-files command hints, generated README freshness command, non-JSON regenerate hint, and structured JSON invalid states. paths: README.md, SPEC.md, docs/portable-workflow.md, +6 more. [accepted]
- codex / codex-cli [codex-review] (code-review): Codex review initially flagged linked-worktree false positives for separate git dirs; implementation was fixed to use git-dir/common-dir worktree metadata. Follow-up Codex review found no blocking bugs. paths: README.md, SPEC.md, docs/portable-workflow.md, +6 more. [accepted]
