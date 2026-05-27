# HK export: `2026-05-27-121500-hk-config-diagnostics`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-27-121500-hk-config-diagnostics --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-27-121500-hk-config-diagnostics`
- Branch: `feat/hk-config-diagnostics`

## Context
- Design locked from Obsidian plan: add read-only hk config inspect/validate/explain/audit under guidance/discovery; no top-level draft/generative commands; HK diagnoses/explains deterministically while profile/system-map creation and repair stay skill-led. Preserve invariants: profiles own commands/requiredness/reviews/readiness, system maps add advisory component/invariant context, and HK records shell-first evidence instead of becoming a task runner.

## Plan
- Add deterministic hk config inspect/validate/explain/audit commands and update HK config authoring skills with create/audit/update flows, system-map authoring copy, router skill, validation, dogfood, and reviews.

## Decisions and spec reflection
- Use nested hk config diagnostics commands plus skill-led authoring/audit flows rather than top-level generative profile/system-map draft commands.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m 'not slow' tests/unit/test_hk_config_cli.py tests/unit/test_system_map_validation.py tests/unit/test_system_map_checks_view.py tests/unit/test_system_map_brief.py`: pass (exit 0) — validates: Config diagnostics and existing system-map/profile focused tests pass — `<local HK state not exported>`
- `bash -lc 'scripts/hk-dev config inspect --target . --json >/tmp/hk-config-inspect-self.json && scripts/hk-dev config validate --target . --json >/tmp/hk-config-validate-self.json && scripts/hk-dev config explain --target . --path src/harness_toolkit/kit/profiles/loading.py --json >/tmp/hk-config-explain-self.json && python3 - <<"PY"
import json
inspect=json.load(open("/tmp/hk-config-inspect-self.json"))
validate=json.load(open("/tmp/hk-config-validate-self.json"))
explain=json.load(open("/tmp/hk-config-explain-self.json"))
assert inspect["resolution"]["profile"] == "harness-toolkit-root"
assert inspect["system_map"]["status"] == "valid"
assert validate["ok"] is True
assert "profiles-system-context" in [c["id"] for c in explain["system_context"]["matched_components"]]
print("hk config diagnostics dogfood passed")
PY'`: pass (exit 0) — validates: Local hk-dev config diagnostics inspect/validate/explain resolve this checkout profile and system-map joins — `<local HK state not exported>`
- `bash -lc 'diff -qr .agents/skills/harness-kit-profile-authoring .agent/skills/harness-kit-profile-authoring && diff -qr .agent/skills/harness-kit-profile-authoring templates/.agent/skills/harness-kit-profile-authoring && diff -qr .agents/skills/hk-system-map-author .agent/skills/hk-system-map-author && diff -qr .agent/skills/hk-system-map-author templates/.agent/skills/hk-system-map-author && diff -qr .agents/skills/hk-config-authoring .agent/skills/hk-config-authoring && diff -qr .agent/skills/hk-config-authoring templates/.agent/skills/hk-config-authoring'`: pass (exit 0) — validates: HK config authoring skill mirrors are internally aligned after profile/system-map/router updates — `<local HK state not exported>`
- `bash -lc 'grep -q "fix direction" /tmp/hk-skill-improve.XIJyrK/harness-kit-profile-authoring/SKILL.md && grep -q "advisory warnings, not readiness blockers" /tmp/hk-skill-improve.XIJyrK/hk-system-map-author/SKILL.md && grep -q "not to add a new profile" /tmp/hk-skill-improve.XIJyrK/hk-config-authoring/SKILL.md'`: pass (exit 0) — validates: Skill-improver temp-copy trial passed for profile/system-map/router authoring skills — `<local HK state not exported>`
- `bash -lc 'cd /Users/alex.furrier/git_repositories/dots && DOTS_REPO=$PWD ai-config sync -c config/ai-config/config.yaml --force --fresh --verify'`: pass (exit 0) — validates: Dots ai-config sync verification passes for mirrored HK config authoring skills — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full mise check passes after HK config diagnostics, docs, tests, and skill updates — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full mise check passes after review fixes for config explain contract and default_profile validation — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full mise check passes after enforcing hk config explain option exclusivity — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests pass after docs/spec/skill updates — `<local HK state not exported>`
- `bash -lc 'scripts/hk-dev config inspect --target . --json >/tmp/hk-config-inspect-self.json && scripts/hk-dev config validate --target . --json >/tmp/hk-config-validate-self.json && scripts/hk-dev config explain --target . --path src/harness_toolkit/kit/profiles/loading.py --json >/tmp/hk-config-explain-self.json && python3 - <<"PY"
import json
inspect=json.load(open("/tmp/hk-config-inspect-self.json"))
validate=json.load(open("/tmp/hk-config-validate-self.json"))
explain=json.load(open("/tmp/hk-config-explain-self.json"))
assert inspect["resolution"]["profile"] == "harness-toolkit-root"
assert inspect["system_map"]["status"] == "valid"
assert validate["ok"] is True
assert "profiles-system-context" in [c["id"] for c in explain["system_context"]["matched_components"]]
print("hk config diagnostics dogfood passed")
PY'`: pass (exit 0) — validates: Local hk-dev config diagnostics still resolve this checkout profile/system-map joins after review fixes — `<local HK state not exported>`
- `bash -lc 'tmp=$(mktemp -d) && cp -R . "$tmp/harness-toolkit" && cd "$tmp/harness-toolkit" && mise run init -- --non-interactive --name hk-config-smoke --shape single --stack python --no-hooks && mise trust .mise.toml && mise run setup && mise run check'`: fail (exit 1) — attempted to validate: Generated Python scaffold smoke passes after template skill updates — `<local HK state not exported>`
- `bash -lc 'tmp=$(mktemp -d) && cp -R . "$tmp/harness-toolkit" && cd "$tmp/harness-toolkit" && mise trust .mise.toml && mise run init -- --non-interactive --name hk-config-smoke --shape single --stack python --no-hooks && mise trust .mise.toml && mise run setup && mise run check'`: fail (exit 4) — attempted to validate: Generated Python scaffold smoke passes after template skill updates — `<local HK state not exported>`
- `uv run pytest tests/e2e/test_python.py::TestPythonSingleHappyPath::test_lint_passes tests/e2e/test_python.py::TestPythonSingleHappyPath::test_check_passes -q`: pass (exit 0) — validates: Generated Python scaffold lint/check smoke passes through e2e coverage after template skill updates — `<local HK state not exported>`
- `scripts/hk-dev export --target . --format handoff-dir --output .ai/hk/2026-05-27-121500-hk-config-diagnostics --check --json`: pass (exit 0) — validates: Generated HK handoff-dir export is fresh — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Repo sync-check passes with refreshed HK export — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests pass after strict JSON validator fix — `<local HK state not exported>`
- `bash -lc 'scripts/hk-dev config validate --target . --json >/tmp/hk-config-validate-self.json && python3 - <<"PY"
import json
assert json.load(open("/tmp/hk-config-validate-self.json"))["ok"] is True
print("hk config validate dogfood passed")
PY'`: pass (exit 0) — validates: Local hk-dev config diagnostics still pass after strict JSON validator fix — `<local HK state not exported>`
- `uv run pytest tests/e2e/test_python.py::TestPythonSingleHappyPath::test_lint_passes tests/e2e/test_python.py::TestPythonSingleHappyPath::test_check_passes -q`: pass (exit 0) — validates: Generated Python scaffold lint/check smoke still passes after strict JSON validator fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full mise check passes after strict JSON validator fix — `<local HK state not exported>`
- `uv run pytest tests/unit/test_hk_config_cli.py tests/agent_sim/test_hk_config_diagnostics_agent_sim.py -q`: pass (exit 0) — validates: Focused config diagnostics CLI and agent_sim coverage pass after help/dogfood polish — `<local HK state not exported>`
- `bash -lc 'scripts/hk-dev config validate --help >/tmp/hk-config-validate-help.txt && scripts/hk-dev config explain --help >/tmp/hk-config-explain-help.txt && test -s /tmp/hk-config-diagnostics-dogfood/reports/worker-report.md && test -s /tmp/hk-config-diagnostics-dogfood/hk-commands.jsonl'`: pass (exit 0) — validates: hk config help and seeded fresh-agent dogfood surfaced actionable diagnostics without running profile checks — `<local HK state not exported>`
- `uv run pytest -m contract`: pass (exit 0) — validates: Contract tests still pass after config diagnostics help/dogfood additions — `<local HK state not exported>`
- `uv run pytest tests/e2e/test_python.py::TestPythonSingleHappyPath::test_lint_passes tests/e2e/test_python.py::TestPythonSingleHappyPath::test_check_passes -q`: pass (exit 0) — validates: Generated Python scaffold smoke still passes after skill dogfood scenario reference changes — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full quality gate passes after config diagnostics help, agent_sim, and dogfood scenario additions — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/portable-workflow.md, docs/profile-authoring.md, +1 more)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/config_diagnostics.py)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched AGENTS.md, README.md, SPEC.md, +15 more)
- profile-check:generated-stack-smoke: pass — required profile check recorded: generated-stack-smoke (matched templates/.agent/skills/harness-kit-profile-authoring/SKILL.md, templates/.agent/skills/hk-config-authoring/SKILL.md, templates/.agent/skills/hk-system-map-author/SKILL.md, +5 more)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched AGENTS.md, SPEC.md, docs/portable-workflow.md, +14 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/config_diagnostics.py)

## Review
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Fresh-context HK lifecycle review found one blocker: missing default_profile validation. Fixed with missing-default-profile diagnostic and regression test. Targeted follow-up verified default_profile validation, config explain missing-input guard, and removal of untracked .agents duplicate skill root; no blockers remain. paths: .agent/skills/harness-kit-profile-authoring/SKILL.md, AGENTS.md, README.md, +22 more. [accepted]
- subagent / agent-friendly-cli-reviewer [codex-review]: Agent-friendly CLI review found blockers in config explain input contract. Fixed missing --changed/--path guard and exclusive --changed vs --path guard with regression tests. Second targeted follow-up found no blockers. Non-blocking suggestions around hints/typed summaries deferred. paths: .agent/skills/harness-kit-profile-authoring/SKILL.md, AGENTS.md, README.md, +22 more. [accepted]
- subagent / architecture-polish-review [architecture-polish-review]: Architecture polish review graded B+ and identified .agents scope, config explain contract, and duplicated validator ownership. Removed .agents from branch, fixed config explain contract, and kept standalone skill validator with lint-safe script; remaining typed summary/parity polish is non-blocking. paths: .agent/skills/harness-kit-profile-authoring/SKILL.md, AGENTS.md, README.md, +22 more. [accepted]
- codex / codex-cli [codex-review]: Codex exec review of PR #26 wrote /var/folders/kf/js4h91w14pl7zwfgnvj896b00000gq/T/tmp.IjSX5yZUEj/review.md and found no blocking issues; it also reported focused pytest, ruff, and sync-check passed. paths: .agent/skills/harness-kit-profile-authoring/SKILL.md, .agent/skills/hk-config-authoring/SKILL.md, .agent/skills/hk-system-map-author/SKILL.md, +22 more. [accepted]
- codex / chatgpt-codex-connector [codex-review]: Addressed Codex PR comment 3313809321: strict warning failure now sets JSON ok=false before emitting output in both repo-local and generated-template system-map validator scripts. Verified with a temp warning-only fixture and posted AI follow-up on PR #26. paths: .agent/skills/hk-system-map-author/scripts/validate_system_toml.py, templates/.agent/skills/hk-system-map-author/scripts/validate_system_toml.py. [accepted]
- subagent / agent-friendly-cli: Agent-friendly CLI review found actionable issues in hk config help/error/output behavior. Fixed structured JSON for repo-state/config explain errors, nonzero inspect on error findings, actionable validate human findings, richer explain human output, and explicit audit advisory exit semantics. paths: src/harness_toolkit/kit/cli.py, tests/unit/test_hk_config_cli.py, tests/agent_sim/test_hk_config_diagnostics_agent_sim.py. [accepted]
- codex / codex-cli [codex-review]: Focused Codex exec review after help/dogfood additions reported no concrete issues and ran focused tests (tests/unit/test_hk_config_cli.py and tests/agent_sim/test_hk_config_diagnostics_agent_sim.py: 14 passed). Review transcript at /var/folders/kf/js4h91w14pl7zwfgnvj896b00000gq/T/tmp.I3AXNBcU0K/review.md. paths: .agent/skills/harness-kit-profile-authoring/SKILL.md, .agent/skills/hk-config-authoring/SKILL.md, .agent/skills/hk-pr-sized-dogfood/SKILL.md, +25 more. [accepted]
- subagent / reviewer-fresh-context [hk-lifecycle-review]: Fresh-context lifecycle review found no blockers: hk config diagnostics remain read-only, do not execute profile checks, do not alter readiness semantics, and audit remains advisory while JSON/help behavior improves agent usability. paths: src/harness_toolkit/kit/cli.py. [accepted]

## Attached artifacts
- agent-dogfood-report: `artifacts/artifact_37_agent-dogfood-report_artifact_20260527_164954_053950_agent-dogfood-report_worker-report.md` (copied, redaction=none, 5093 bytes, sha256:0e8e0ed0ce10) — hk-config-diagnostics-seeded-agent
- agent-dogfood-log: `artifacts/artifact_38_agent-dogfood-log_artifact_20260527_164954_705021_agent-dogfood-log_hk-commands.jsonl` (copied, redaction=none, 9482 bytes, sha256:2b94a93e2172) — hk-config-diagnostics-hk-commands
