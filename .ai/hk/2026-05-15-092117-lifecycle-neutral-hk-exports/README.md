# HK export: `2026-05-15-092117-lifecycle-neutral-hk-exports`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-15-092117-lifecycle-neutral-hk-exports --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-15-092117-lifecycle-neutral-hk-exports`
- Branch: `lifecycle-neutral-hk-exports`

## Context
- Feedback from Foreman dogfood: final handoff export can create a freshness loop because generated .ai/hk/<work-id>/ files and export/check metadata affect readiness/export metadata. Foreman must stay read-only; HK should make ready + exported stable.

## Plan
- Make active HK handoff-dir exports lifecycle-neutral and idempotent: generated .ai/hk/<active-work-id>/ packages should not make readiness/sync/validation/review freshness stale, while export --check and sync-check continue to strictly validate package integrity. Preserve non-active HK exports as normal changed files. Validate with focused tests, docs/spec contracts, full check, HK dogfood finalization, fresh-context docs/context review, agent-friendly CLI review, architecture polish review, and PR CI.

## Decisions and spec reflection
- Active .ai/hk/<work-id> exports are generated derived artifacts: HK excludes only the active export package from validation/review/sync freshness and readiness changed-path checks, while export --check and sync-check remain strict integrity gates for generated files and attached artifacts.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, docs/decisions/0012-lifecycle-neutral-active-hk-exports.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout: scripts/hk-dev finalization remains ready after active export generation and exact export check — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_sync_stale or review_remains_fresh_for_active_hk_export_changes or handoff_dir_export_writes_generated_package_and_checks_freshness' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests cover ready/sync stability and non-active export staleness — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts for lifecycle-neutral active HK exports — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate for lifecycle-neutral active HK exports — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'handoff_dir_export_check_rejects_missing_artifact_file_hash or handoff_dir_export_writes_generated_package_and_checks_freshness or active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_freshness_stale or legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests cover active neutrality, non-active staleness, legacy sync compatibility, and strict export hash diagnostics — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts for lifecycle-neutral active HK exports after review fixes — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate after lifecycle-neutral export review fixes — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout after review fixes: scripts/hk-dev finalization remains ready after active export generation and exact export check — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'handoff_dir_export_check_rejects_modified_attached_artifact or handoff_dir_export_check_rejects_missing_artifact_file_hash or handoff_dir_export_writes_generated_package_and_checks_freshness or active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_freshness_stale or legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests after strict check diagnostic fixes — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts after lifecycle-neutral export review fixes — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate after strict export check and lifecycle-neutral fixes — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout after strict export check fixes: scripts/hk-dev finalization remains ready after active export generation and exact export check — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'handoff_dir_export_writes_generated_package_and_checks_freshness or handoff_dir_export_check_rejects_modified_attached_artifact or handoff_dir_export_check_rejects_missing_artifact_file_hash or active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_freshness_stale or legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests after README hash integrity fixes — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts after README hash integrity fixes — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout after README hash integrity fixes — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'handoff_dir_export_preserves_user_status_bullets or handoff_dir_export_check_rejects_invalid_utf8_generated_file or handoff_dir_export_writes_generated_package_and_checks_freshness or handoff_dir_export_check_rejects_modified_attached_artifact or handoff_dir_export_check_rejects_missing_artifact_file_hash or active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_freshness_stale or legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests after stable export README scoping fix — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts after stable export README scoping fix — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout after stable export README scoping fix — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate after stable export README scoping fix — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'handoff_dir_export_check_rejects_unexpected_export_files or handoff_dir_export_preserves_user_status_bullets or handoff_dir_export_check_rejects_invalid_utf8_generated_file or handoff_dir_export_writes_generated_package_and_checks_freshness or handoff_dir_export_check_rejects_modified_attached_artifact or handoff_dir_export_check_rejects_missing_artifact_file_hash or active_hk_export_does_not_make_ready_or_sync_stale or non_active_hk_export_changes_still_make_freshness_stale or legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade' -q`: pass (exit 0) — validates: Focused lifecycle-neutral export tests after unexpected export file integrity fix — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Docs/spec/ADR contracts after unexpected export file integrity fix — `<local HK state not exported>`
- `bash -lc 'set -euo pipefail
repo=$(mktemp -d /tmp/hk-lifecycle-neutral-dogfood.XXXXXX)/repo
mkdir -p "$repo"
git -C "$repo" init -q
git -C "$repo" checkout -q -b feature/dogfood
git -C "$repo" config user.email test@example.com
git -C "$repo" config user.name Test
printf "# Dogfood\n" > "$repo/README.md"
git -C "$repo" add README.md
git -C "$repo" commit --no-verify -q -m initial
cd "$repo"
HK=scripts/hk-dev
$HK start lifecycle-neutral-export --target . --plan "Dogfood lifecycle-neutral active export finalization" --json >/tmp/hk-dogfood-start.json
$HK decide "Active HK exports are generated derived artifacts for this dogfood." --spec-impact not-needed --target . --json >/tmp/hk-dogfood-decide.json
printf "# Dogfood\n\nchanged\n" > README.md
$HK validate --target . --why "Dogfood validation for changed README" -- python3 -c "print(\"validation ok\")" >/tmp/hk-dogfood-validate.out
$HK review add --target . --backend subagent --reviewer reviewer-fresh-context --summary "Dogfood review passed." --json >/tmp/hk-dogfood-review.json
$HK sync --target . --json >/tmp/hk-dogfood-sync.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-before.json
$HK export --target . --format handoff-dir --json > /tmp/hk-dogfood-export.json
$HK export --target . --format handoff-dir --check --json > /tmp/hk-dogfood-export-check.json
$HK ready --target . --json > /tmp/hk-dogfood-ready-after.json
python3 - <<"PY"
import json
before=json.load(open("/tmp/hk-dogfood-ready-before.json"))
check=json.load(open("/tmp/hk-dogfood-export-check.json"))
after=json.load(open("/tmp/hk-dogfood-ready-after.json"))
assert before["ready"] is True, before
assert check["fresh"] is True and check["state"] == "fresh", check
assert after["ready"] is True, after
print("dogfood ready_before=", before["status"])
print("dogfood export_check=", check["state"])
print("dogfood ready_after=", after["status"])
PY'`: pass (exit 0) — validates: Dogfood rollout after unexpected export file integrity fix — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate after unexpected export file integrity fix — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK export validates for lifecycle-neutral active export slice — `<local HK state not exported>`
- `uv run --frozen pytest tests/unit/test_harness_kit_2.py -k 'dangerously_skip_sync_satisfies_readiness_and_handoff or handoff_dir_export_check_rejects_unexpected_export_files or active_hk_export_does_not_make_ready_or_sync_stale' -q`: pass (exit 0) — validates: Focused tests after Devin sync-skip implicit-exclude fix — `<local HK state not exported>`
- `bash -lc 'trap "git checkout -- uv.lock" EXIT; env UV_NO_CONFIG=1 UV_INDEX_URL=https://pypi.org/simple mise run check'`: pass (exit 0) — validates: Full quality gate after Devin sync-skip implicit-exclude fix — `<local HK state not exported>`
- `uv run --frozen pytest -m contract -q`: pass (exit 0) — validates: Contract docs/spec checks after PR-comment fix — `<local HK state not exported>`
- `env UV_FROZEN=true scripts/hk-dev brief --target . --json`: pass (exit 0) — validates: Dogfood remains covered after PR-comment fix; change is sync skip metadata only — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK export validates after PR-comment fix — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/AGENTS.md, docs/decisions/0011-path-aware-review-freshness.md, +4 more)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/local.py)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched README.md, SPEC.md, docs/AGENTS.md, +7 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched SPEC.md, docs/AGENTS.md, docs/decisions/0011-path-aware-review-freshness.md, +5 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/local.py)

## Review
- subagent / docs-context-reviewer: Docs/context review found no blockers. Lifecycle-neutral active HK export docs are consistent across README, SPEC, portable workflow, lifecycle design, ADR 0011/0012, docs index, and mkdocs. paths: README.md, SPEC.md, docs/portable-workflow.md, +5 more. [accepted]
- subagent / agent-friendly-cli: Agent-friendly CLI review found no blockers. Verified active-only lifecycle-neutral boundary, non-active export staleness, exact export check generated/artifact diagnostics, committed active export stability, JSON compatibility, and no uv.lock churn. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, README.md, +2 more. [accepted]
- subagent / architecture-polish-reviewer [architecture-polish-review]: Architecture polish review found no blockers. Verified active export exclusion abstraction, two-pass export stability, strict generated/artifact integrity, committed export stability, active/non-active boundary, and conservative source freshness. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, docs/decisions/0012-lifecycle-neutral-active-hk-exports.md. [accepted]
- subagent / agent-friendly-cli: Final agent-friendly CLI review found no blockers. Verified active lifecycle-neutral export behavior, unexpected export file rejection, generated/artifact hash diagnostics, stable export README scoping, dogfood evidence, and no uv.lock churn. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, README.md, +3 more. [accepted]
- subagent / architecture-polish-reviewer [architecture-polish-review]: Final architecture-polish review found no blockers. Verified active/non-active export boundary, strict export integrity, source freshness conservatism, legacy sync compatibility, and ADR alignment. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, docs/decisions/0012-lifecycle-neutral-active-hk-exports.md. [accepted]
- subagent / hk-lifecycle-reviewer [hk-lifecycle-review]: HK lifecycle review found no blockers. Verified validation/review/sync safety, lifecycle-neutral active export scope, strict export integrity gates, and HK remains guidance/evidence rather than a task runner. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, SPEC.md, +1 more. [accepted]
- subagent / codex-style-bug-review [codex-review]: Codex-style bug review found no blockers after fixes. Checked export integrity false-fresh cases, path/symlink/hash safety, sync freshness regressions, and test coverage. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py, SPEC.md, +2 more. [accepted]
- subagent / codex-style-bug-review [codex-review]: Codex-style docs follow-up found no blockers for docs index, ADR 0011 lifecycle-neutral wording, and lifecycle design/portable workflow consistency. paths: docs/AGENTS.md, docs/decisions/0011-path-aware-review-freshness.md, docs/harness-kit-lifecycle-design.md, +3 more. [accepted]
- subagent / agent-friendly-cli: PR-comment fix review found no blockers. Verified dangerous sync skips record implicit_excluded_paths additively and preserve CLI/JSON compatibility. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py. [accepted]
- subagent / hk-lifecycle-reviewer [hk-lifecycle-review]: Lifecycle review for PR-comment fix found no blockers. Verified sync dangerous-skip hashing now records implicit active-export excludes like checkpoints while preserving legacy compatibility. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py. [accepted]
- subagent / codex-style-bug-review [codex-review]: Codex-style review for PR-comment fix found no blockers. Checked implicit_excluded_paths event shape, sync skip freshness matching, and regression test. paths: src/harness_toolkit/kit/local.py, tests/unit/test_harness_kit_2.py. [accepted]
