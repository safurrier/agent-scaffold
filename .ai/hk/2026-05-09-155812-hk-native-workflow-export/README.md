# HK export: `2026-05-09-155812-hk-native-workflow-export`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-09-155812-hk-native-workflow-export --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-09-155812-hk-native-workflow-export`
- Branch: `feat/hk-native-workflow`
- Git SHA: `3a03baf`
- Dirty: `true`
- Sync status: `synced`

## Context
- None recorded.

## Plan
- Migrate harness-toolkit repo workflow to HK-native source of truth: add HK handoff-dir exports under .ai/hk, validate exports when present, redirect repo-local mise plan usage toward hk start, and document .ai/plans as legacy scaffold history.

## Decisions and spec reflection
- Make Harness Toolkit repo workflow HK-native: HK ledger is source of truth, .ai/hk exports are generated committed views for meaningful work, and legacy .ai/plans remains scaffold/generated-repo history rather than normal repo workflow.
- Simplify HK handoff-dir exports to a compact review package: README.md is the single human handoff/projection, meta.json is machine freshness metadata, and artifacts/ remains explicit-only rather than mirroring each ledger event type into separate Markdown files.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, docs/portable-workflow.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest tests/contract/test_task_contract.py tests/unit/test_slice_workflow_cli.py -q`: pass (exit 0) — validates: Contract tests cover CI/task contract and generated repo workflow expectations changed by HK export validation. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161320_702793.transcript.log`
- `uv run pytest tests/unit/test_harness_kit_2.py::test_handoff_dir_export_writes_generated_package_and_checks_freshness tests/unit/test_harness_kit_2.py::test_cli_handoff_dir_export_json_is_parseable tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_changed_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_hk_exports_when_present tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_incomplete_hk_exports -q`: pass (exit 0) — validates: Focused unit coverage for handoff-dir exports, export freshness checks, and slice-workflow HK export validation. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161334_615215.transcript.log`
- `uv run pytest tests/e2e/test_plan.py -q`: pass (exit 0) — validates: Validates scaffold copy/generated plan task compatibility after root plan wrapper and slice-workflow export-check changes. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161353_968862.transcript.log`
- `bash -lc 'set -euo pipefail
rm -rf /tmp/hk-native-export-dogfood
scripts/hk-dev export --format handoff-dir --output /tmp/hk-native-export-dogfood --target . --json >/tmp/hk-native-export.json
scripts/hk-dev export --format handoff-dir --output /tmp/hk-native-export-dogfood --target . --check --json >/tmp/hk-native-export-check.json
python3 - <<"PY"
import json
export=json.load(open("/tmp/hk-native-export.json"))
check=json.load(open("/tmp/hk-native-export-check.json"))
assert export["format"] == "handoff-dir"
assert check["checked"] is True
assert check["fresh"] is True
PY'`: pass (exit 0) — validates: Dogfoods this checkout's hk export handoff-dir and freshness check using scripts/hk-dev. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161446_151536.transcript.log`
- `mise run check`: fail (exit 1) — attempted to validate: Full repository quality gate after HK-native export workflow implementation. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161454_061144.transcript.log`
- `mise run check`: fail (exit 1) — attempted to validate: Full repository quality gate after formatting HK-native export workflow implementation. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161500_780237.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after fixing type issues in HK-native export workflow implementation. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_161528_141528.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after addressing review blockers for HK export freshness, .ai/hk root docs, sync-check mode, and shell-safe guidance. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_163226_502962.transcript.log`
- `mise run check`: fail (exit 1) — attempted to validate: Final full quality gate after review-driven shell-safety and export repair-hint fixes. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_170855_202987.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after updating generated golden expectations for shell-safe scaffold guidance. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_171924_851213.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Generated export gate passes in HK-native mode; no legacy .ai/plans slice is required for this repo. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_172345_561969.transcript.log`
- `mise run verify`: pass (exit 0) — validates: Heavy validation gate for CI workflow and repo workflow migration changes. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_172355_317792.transcript.log`
- `hk status --target . --json`: pass (exit 0) — validates: Records HK readiness/status after all required validation and reviews before generating the committed .ai/hk export. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_172759_945209.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Generated .ai/hk export package validates structurally after export. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_172820_698102.transcript.log`
- `uv run pytest tests/unit/test_harness_kit_2.py::test_handoff_dir_export_writes_generated_package_and_checks_freshness tests/unit/test_slice_workflow_cli.py::test_sync_check_requires_changed_hk_export_for_meaningful_changes tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_changed_hk_exports -q`: pass (exit 0) — validates: Regression coverage for source diff freshness, HK export coverage enforcement, and changed export validation after Codex review findings. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_174808_358343.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after addressing Codex review findings on export source freshness and CI coverage enforcement. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_174826_533603.transcript.log`
- `uv run pytest tests/unit/test_harness_kit_2.py::test_handoff_dir_export_writes_generated_package_and_checks_freshness tests/unit/test_harness_kit_2.py::test_cli_handoff_dir_export_json_is_parseable tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_hk_exports_when_present tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_changed_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_incomplete_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_reports_corrupt_hk_export_metadata_with_repair_hint -q`: pass (exit 0) — validates: Regression coverage for compact HK export package shape, meta.json validation, and changed HK export sync-check behavior. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_193354_753231.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after simplifying HK handoff-dir exports to README.md, meta.json, and explicit-only artifacts. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_193416_705221.transcript.log`
- `uv run pytest tests/unit/test_harness_kit_2.py::test_handoff_dir_export_writes_generated_package_and_checks_freshness tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_hk_exports_when_present tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_changed_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_obsolete_hk_export_files tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_metadata_with_wrong_hk_export_files_list tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_incomplete_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_reports_corrupt_hk_export_metadata_with_repair_hint -q`: pass (exit 0) — validates: Regression coverage for compact HK export shape, safe obsolete-file cleanup, metadata files-list validation, and obsolete generated file rejection. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_194426_705212.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after compact export shape hardening and sync-check validation fixes. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_194440_555614.transcript.log`
- `uv run pytest tests/unit/test_harness_kit_2.py::test_handoff_dir_export_writes_generated_package_and_checks_freshness tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_hk_exports_when_present tests/unit/test_slice_workflow_cli.py::test_sync_check_validates_changed_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_obsolete_hk_export_files tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_metadata_with_wrong_hk_export_files_list tests/unit/test_slice_workflow_cli.py::test_sync_check_rejects_incomplete_hk_exports tests/unit/test_slice_workflow_cli.py::test_sync_check_reports_corrupt_hk_export_metadata_with_repair_hint -q`: pass (exit 0) — validates: Regression coverage for compact export shape and safe cleanup hardening, including symlinked artifact directories and obsolete generated file rejection. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_195203_289268.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repository quality gate after safe cleanup hardening for compact HK exports. — `.harness-local/harness-kit/root/work/2026-05-09-155812-hk-native-workflow-export/artifacts/ev_20260509_195216_460694.transcript.log`

## Readiness
- Status: `ready`
- context: info — no context recorded; okay for trivial work, add hk context if it prevents rediscovery
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched .github/workflows/ci.yml, .mise/tasks/plan, .mise/tasks/sync-check, +4 more)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, +2 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .ai/hk/2026-05-09-155812-hk-native-workflow-export/artifacts/README.md, .ai/hk/2026-05-09-155812-hk-native-workflow-export/meta.json, .ai/hk/AGENTS.md, +32 more)
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched SPEC.md, templates/.agent/skills/slice-workflow/cli/src/slice_workflow_cli/checks.py, templates/.agent/skills/slice-workflow/cli/src/slice_workflow_cli/cli.py)
- profile-check:heavy-gate: pass — required profile check recorded: heavy-gate (matched .github/workflows/ci.yml)
- profile-check:generated-stack-smoke: pass — required profile check recorded: generated-stack-smoke (matched templates/.agent/skills/slice-workflow/cli/src/slice_workflow_cli/checks.py, templates/.agent/skills/slice-workflow/cli/src/slice_workflow_cli/cli.py, templates/AGENTS.md.tmpl)
- profile-check:hk-readiness: pass — required profile check recorded: hk-readiness (matched .ai/hk/2026-05-09-155812-hk-native-workflow-export/artifacts/README.md, .ai/hk/2026-05-09-155812-hk-native-workflow-export/meta.json, .ai/hk/AGENTS.md, +32 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched .ai/hk/AGENTS.md, .github/workflows/ci.yml, .mise/tasks/plan, +20 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/local.py, +2 more)
- sync: pass — sync checkpoint fresh

## Review
- pi-subagent / reviewer [hk-lifecycle-review] (core-quality): Fresh-context reviewer found export freshness, .ai/hk path classification, and sync-check mode blockers; fixes added generated-file hashes, skipped root .ai/hk docs as exports, and made harness-toolkit sync-check HK-export-only by default. Re-review accepted these areas. [accepted]
- pi-subagent / agent-friendly-cli [codex-review] (agent-facing-cli): Agent-facing CLI reviewer found shell-safety and repair-hint blockers; fixes made promoted commands shell-safe, quoted migration slugs, required handoff-dir for export --check/--output, and added repair hints for corrupt export metadata. Final re-review accepted. [accepted]
- codex-exec / codex-multi-agent [codex-review] (correctness): Codex review found two high issues: export --check ignored source diff changes and PR CI allowed meaningful changes without an HK export. Fixed by comparing work diff hashes, enforcing changed HK exports for meaningful PR changes when no legacy plan changed, and sanitizing local paths in exports. [accepted]
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (core-quality): Fresh-context re-review accepted compact HK export shape changes: README.md/meta.json/artifacts package, safe obsolete-file cleanup with symlink protection, sync-check shape enforcement, fresh generated export, and META.json to meta.json git rename. [accepted]

## Sync exclusions
- context.md: Pre-existing scratch context from prior profile-catalog research; not part of this HK-native workflow change.
- progress.md: Pre-existing scratch progress note from prior profile-catalog research; not part of this HK-native workflow change.
- context.md: Pre-existing scratch context from prior profile-catalog research; not part of this HK-native workflow change.
- progress.md: Pre-existing scratch progress note from prior profile-catalog research; not part of this HK-native workflow change.
