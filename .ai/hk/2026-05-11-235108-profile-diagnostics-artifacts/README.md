# HK export: `2026-05-11-235108-profile-diagnostics-artifacts`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-11-235108-profile-diagnostics-artifacts --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-11-235108-profile-diagnostics-artifacts`
- Branch: `hk-profile-diagnostics-artifacts`
- Git SHA: `6186242`
- Dirty: `true`
- Sync status: `synced`

## Context
- Plan follow-up HK improvements after PR #16: profile diagnostics UX and artifact attachment productization/dogfood. Artifact attach already exists as an MVP skeleton; this work should first characterize current behavior and dogfood the hk-session-artifacts skill before expanding scope.
- Current baseline from reconnaissance:  already exists with --path/--kind/--label/--redaction/--copy/--no-copy and examples for agent sessions, Codex review, and HAR files. Repo-local  already teaches agents to attach Pi/Claude/Codex transcripts, so the next slice should dogfood and harden that workflow rather than design artifact attach from scratch.
- Current baseline from reconnaissance:

- `hk artifact attach` already exists with `--path`, `--kind`, `--label`, `--redaction`, `--copy/--no-copy`, JSON output, and examples for agent sessions, Codex review, and HAR files.
- Repo-local `.agent/skills/hk-session-artifacts` already teaches agents to attach Pi/Claude/Codex transcripts.
- Therefore the artifact work should harden/productize and dogfood the existing workflow rather than design artifact attach from scratch.
- The profile diagnostics work should focus on making existing `hk profile resolve` and `hk checks --changed` outputs answer “why this profile/check/review?” before adding any new command surface.

## Plan
- Explore and implement HK profile diagnostics UX plus artifact attachment productization with full HK validation/review/dogfood gates.
- # Plan: HK profile diagnostics UX + artifact attachment dogfood

## Intent

Improve the day-to-day HK agent workflow in two connected areas:

1. Make profile/check resolution easier to explain when an agent asks "why is HK requiring this?".
2. Productize `hk artifact attach` through real dogfooding with the repo-local `hk-session-artifacts` skill so agents reliably attach tool-produced evidence instead of writing prose summaries.

This should be implemented with the same safety bar as the lifecycle/profile work: characterize current behavior first, keep CLI and JSON compatibility additive, run focused tests plus full gates, dogfood against real HK work, and get fresh-context review before PR handoff.

## Product principles

- Keep HK lifecycle commands opinionated and singular; avoid adding duplicate command surfaces unless the existing surface cannot explain itself.
- Prefer additive diagnostics in existing commands before creating new commands.
- Preserve machine-readable JSON compatibility: new fields are additive; existing fields/meanings stay stable.
- Diagnostics should explain decisions, not infer correctness magically.
- `hk artifact attach` should copy/hash/record real files produced by tools and render durable metadata; agents should not hand-author transcript prose.
- The artifact workflow must be dogfooded with the actual skill (`.agent/skills/hk-session-artifacts`) and realistic agent/review transcript files.

## Phase 0 — Baseline + design reconnaissance

1. Inventory current profile diagnostics and artifact surfaces:
   - `hk profile resolve --target . --json`
   - `hk checks --target . --changed --json`
   - `hk review prompt ...`
   - `hk artifact attach --help`
   - `hk handoff` / `hk export --format handoff-dir`
   - `.agent/skills/hk-session-artifacts/SKILL.md`
2. Characterize current behavior with tests before changing semantics:
   - profile resolution direct match vs worktree-projected match
   - changed-path check/review matching and required/suggested status
   - artifact copy vs `--no-copy`, hash/size/path metadata, handoff rendering, export rendering
3. Decide whether the first PR should be one combined slice or two smaller PRs:
   - diagnostics UX can be independent;
   - artifact attach dogfood may reveal UX changes in help/output/rendering.

## Phase 1 — Profile diagnostics UX

Target outcome: an agent can inspect HK output and answer:

- Which profile resolved for this target?
- Was the match direct, default, or linked-worktree projected?
- Which configured target/path/pattern caused the match?
- Which changed files triggered each check/review?
- Which checks/reviews are required vs suggested?
- What exact command or review action satisfies each required item?

Likely implementation shape:

1. Add an internal explanation model close to profile/check resolution, not scattered print formatting:
   - profile resolution explanation already has some metadata; preserve it and extend only if needed.
   - check/review matching should expose matched path rules and changed files in a structured way.
2. Improve existing command output first:
   - `hk profile resolve --json`: additive explanation fields only if the current fields are insufficient.
   - `hk profile resolve` human output: show direct/default/worktree reason and matched/projected target succinctly.
   - `hk checks --changed --json`: include per-check/per-review matched files/patterns/required status/satisfying command hints if missing.
   - `hk checks --changed` human output: group required vs suggested and show concise “because … matched …” lines.
3. Avoid a new `hk explain`/`hk diagnose` command unless the existing commands become too noisy.
4. Update docs/examples where agent loops currently say “run `hk checks --changed --json`” so they point to the clearer output.

Tests/validation:

- Unit tests for direct/default/worktree resolution explanation stability.
- Unit tests for check/review path-rule explanation, including negated patterns and target-relative matching.
- Golden or snapshot-style tests for human-readable `hk checks --changed` output if formatting changes are meaningful.
- Agent simulation: fake agent runs `hk profile resolve`, `hk checks --changed`, then records the right named validations/reviews without guessing.
- Validation commands:
  - `uv run pytest tests/unit/test_portable_workflow.py -k "profile_resolution or checks" -q`
  - `uv run pytest -m agent_sim -q`
  - `uv run pytest -m contract -q`
  - `mise run check`
  - `mise run sync-check`

Fresh-context review:

- HK lifecycle/readiness reviewer: verify diagnostics do not change readiness semantics.
- Agent-friendly CLI reviewer: verify output is discoverable, noninteractive, stable, and parsable.

## Phase 2 — Artifact attach productization + dogfood

Target outcome: `hk artifact attach` is obviously useful to agents and naturally used by the `hk-session-artifacts` skill for real review/session evidence.

Current baseline: `hk artifact attach` already exists with `--path`, `--kind`, `--label`, `--redaction`, `--copy/--no-copy`, JSON output, hash/size metadata, and handoff/export rendering. Treat this as an MVP skeleton to harden/productize, not as greenfield.

Explore/dogfood questions:

- Can an agent find the correct transcript path without accidentally attaching the wrong latest session?
- Does `hk artifact attach --json` return enough information for an agent to verify what was copied/referenced?
- Does `hk handoff` make attached artifacts visible enough for reviewers?
- Does exported `.ai/hk/<work-id>/artifacts/` contain only explicit attachments and enough metadata to audit them?
- Are `kind`, `label`, and `redaction` choices clear enough in help text and skill guidance?
- Do we need an `hk artifact list`/`hk artifact show` read-only surface, or is handoff/evidence inspection enough for now?

Implementation candidates, gated by dogfood findings:

1. Strengthen existing output/help:
   - clearer examples for Codex/Pi/Claude transcripts;
   - JSON includes copied/reference path, sha256, byte size, redaction status, and event seq;
   - errors explain invalid kind/path/copy behavior.
2. Improve handoff/export rendering:
   - show attached artifact table with kind, label, redaction, size, sha256 prefix, copied/reference path;
   - export copied artifacts into explicit-only `artifacts/`, preserving metadata.
3. Add read-only inspection only if dogfood shows a real gap:
   - `hk artifact list --json` or reuse `hk evidence list` if artifact events already appear clearly.
   - Avoid broad artifact lifecycle management or deletion in the MVP.
4. Improve `.agent/skills/hk-session-artifacts` based on observed agent mistakes:
   - prefer producer-provided exact paths;
   - use candidate helper only as inspection aid;
   - require timestamp/repo/prompt/session-id confirmation before attaching discovered latest sessions;
   - include examples that capture Codex output to known files before attachment.

Dogfood rounds:

1. Synthetic fixture round:
   - create temp transcript/summary/HAR-like files;
   - attach copy and no-copy artifacts;
   - verify `hk handoff`, `hk export`, and metadata.
2. Skill dry-run round:
   - invoke or manually follow `.agent/skills/hk-session-artifacts` against known temp files;
   - check whether instructions lead to correct `hk artifact attach` usage.
3. Real review transcript round:
   - run a fresh-context review or Codex CLI review with stdout saved to known files;
   - attach transcript + final summary via the skill;
   - verify reviewers can understand the artifact from handoff/export without opening local-only state.
4. Agent simulation round:
   - add `tests/agent_sim` coverage where a fake agent attaches a tool-produced transcript and reaches readiness/export.

Tests/validation:

- Unit tests for artifact attach validation, copy/no-copy metadata, and handoff/export rendering.
- Agent simulation for transcript attachment workflow.
- Contract tests if public help/docs/spec examples change.
- Validation commands:
  - `uv run pytest tests/unit -k "artifact" -q`
  - `uv run pytest -m agent_sim -q`
  - `uv run pytest -m contract -q`
  - `mise run check`
  - `mise run sync-check`

Fresh-context review:

- HK lifecycle/readiness reviewer: verify artifact attachments are evidence aids and do not weaken validation/review/readiness gates.
- Agent-friendly CLI reviewer: verify `artifact attach` and any read-only artifact inspection are safe for agents, deterministic, noninteractive, and JSON-friendly.
- Optional Codex review: focus on file-copy safety, path traversal, hash correctness, and export integrity.

## Phase 3 — Handoff/export and docs polish

1. Update `README.md`, `SPEC.md`, `docs/portable-workflow.md`, and `docs/harness-kit-lifecycle-design.md` only where behavior/product intent changes.
2. Keep public docs generic; keep personal/dotfiles-specific adoption notes out of public docs.
3. Export `.ai/hk/<work-id>/` after validations/reviews and require `hk ready` + `mise run sync-check` before PR.

## Acceptance criteria

- Existing public CLI behavior remains compatible; JSON changes are additive.
- Profile diagnostics answer “why required?” without changing readiness semantics.
- Artifact attachment dogfood demonstrates at least one realistic transcript attachment workflow through the skill.
- Attached artifacts are copied or referenced intentionally, hashed, rendered in handoff, and included/represented in export.
- Agent simulations cover the intended workflows.
- Fresh-context reviews report no blockers.
- `mise run check`, `mise run sync-check`, and `hk ready --target . --json` pass before handoff.

## Initial risk register

- Diagnostics output could become too noisy. Mitigation: keep terse human output, put full detail in JSON.
- Artifact attachment could encourage copying sensitive raw sessions. Mitigation: redaction metadata, skill warnings, exact-path preference, and `--no-copy` for sensitive/large files.
- A read-only artifact list command could overexpand scope. Mitigation: add only if dogfood proves handoff/evidence list is insufficient.
- Combining diagnostics and artifact work may be too large. Mitigation: split into two PRs after Phase 0 if implementation touches diverge.
- Scope update: fold practical review freshness into this PR rather than splitting it out. Preserve deterministic facts, but avoid whole-diff review thrash. Implement path/content-aware review coverage: `hk review add` records hashes for reviewed changed paths, optional `--path` supports targeted follow-up reviews, readiness reports uncovered changed paths instead of only saying stale diff hash, and active generated `.ai/hk/<work-id>/` export refreshes are review-neutral and validated by export/sync checks instead of forcing another broad review.

## Decisions and spec reflection
- Treat profile diagnostics and artifact attach as workflow/CLI product work: prefer additive improvements to existing commands, keep readiness semantics unchanged, and use dogfood/agent simulation before adding new surfaces.
- Implemented as one PR per user request. Profile diagnostics stayed additive on existing commands; artifact work kept attach as the MVP, added read-only artifact list for verification, and hardened handoff-dir artifact export/check path integrity.
- Review freshness should use deterministic path/content facts plus model-guided targeted follow-up review, not exact whole-diff hash matching as the only product-level gate. Generated active HK exports are review-neutral and must be covered by export/sync validation.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, docs/harness-kit-lifecycle-design.md, docs/portable-workflow.md
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, README.md, docs/portable-workflow.md, docs/harness-kit-lifecycle-design.md
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md, README.md, docs/portable-workflow.md, docs/harness-kit-lifecycle-design.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests cover public docs/spec examples and profile/artifact CLI shape. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"fast-gate\" and (.matched_patterns | length > 0))"
printf "%s" "$checks_json" | jq -e "any(.suggested_reviews[]; .name == \"hk-lifecycle-review\" and (.matched_patterns | index(\"src/harness_toolkit/kit/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"validation-transcript\" and .copied == true and .redaction == \"external\")"
out=$(mktemp -d)
scripts/hk-dev export --format handoff-dir --output "$out/handoff" --target . --json | jq -e ".format == \"handoff-dir\""
jq -e "any(.attached_artifacts[]; .kind == \"validation-transcript\" and .export_path != \"\")" "$out/handoff/meta.json"
artifact_path=$(jq -r ".attached_artifacts[] | select(.kind == \"validation-transcript\") | .export_path" "$out/handoff/meta.json" | head -1)
test -f "$out/handoff/$artifact_path"
'`: fail (exit 4) — attempted to validate: Dogfood hk profile diagnostics and artifact attachment/list/export surfaces through this checkout's hk-dev CLI. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"fast-gate\" and (.matched_patterns | length > 0))"
printf "%s" "$checks_json" | jq -e "any(.suggested_reviews[]; .name == \"hk-lifecycle-review\" and (.matched_patterns | index(\"src/harness_toolkit/kit/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"validation-transcript\" and .copied == true and .redaction == \"external\")"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
jq -e "any(.attached_artifacts[]; .kind == \"validation-transcript\" and .export_path != \"\")" "$out/meta.json"
artifact_path=$(jq -r ".attached_artifacts[] | select(.kind == \"validation-transcript\") | .export_path" "$out/meta.json" | head -1)
test -f "$out/$artifact_path"
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics and artifact attachment/list/export surfaces through this checkout's hk-dev CLI. — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Full repo quality gate passes after profile diagnostics and artifact attach/export changes. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after profile diagnostics and artifact attach/export changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests cover public docs/spec examples and profile/artifact CLI shape after artifact export hardening. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"fast-gate\" and (.matched_patterns | length > 0))"
printf "%s" "$checks_json" | jq -e "any(.suggested_reviews[]; .name == \"hk-lifecycle-review\" and (.matched_patterns | index(\"src/harness_toolkit/kit/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"validation-transcript\" and .copied == true and .redaction == \"external\")"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
scripts/hk-dev export --format handoff-dir --output "$out" --target . --check --json | jq -e ".fresh == true"
jq -e "any(.attached_artifacts[]; .kind == \"validation-transcript\" and .export_path != \"\")" "$out/meta.json"
artifact_path=$(jq -r ".attached_artifacts[] | select(.kind == \"validation-transcript\") | .export_path" "$out/meta.json" | head -1)
test -f "$out/$artifact_path"
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics and artifact attachment/list/export surfaces through this checkout's hk-dev CLI after export hardening. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after profile diagnostics, artifact attach/list/export, and export hardening changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after profile diagnostics, artifact attach/list/export, and export path-safety hardening. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"fast-gate\" and (.matched_patterns | length > 0))"
printf "%s" "$checks_json" | jq -e "any(.suggested_reviews[]; .name == \"hk-lifecycle-review\" and (.matched_patterns | index(\"src/harness_toolkit/kit/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"validation-transcript\" and .copied == true and .redaction == \"external\")"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
scripts/hk-dev export --format handoff-dir --output "$out" --target . --check --json | jq -e ".fresh == true"
jq -e "any(.attached_artifacts[]; .kind == \"validation-transcript\" and .export_path != \"\")" "$out/meta.json"
artifact_path=$(jq -r ".attached_artifacts[] | select(.kind == \"validation-transcript\") | .export_path" "$out/meta.json" | head -1)
test -f "$out/$artifact_path"
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics and artifact attachment/list/export/check surfaces after export path-safety hardening. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after final profile diagnostics, artifact attach/list/export, and export path-safety hardening changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after final artifact export freshness hardening for copied attachments. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"fast-gate\" and (.matched_patterns | length > 0))"
printf "%s" "$checks_json" | jq -e "any(.suggested_reviews[]; .name == \"hk-lifecycle-review\" and (.matched_patterns | index(\"src/harness_toolkit/kit/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"codex-review-summary\" and .copied == true and .redaction == \"external\")"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
scripts/hk-dev export --format handoff-dir --output "$out" --target . --check --json | jq -e ".fresh == true"
jq -e "any(.attached_artifacts[]; .kind == \"codex-review-summary\" and .export_path != \"\")" "$out/meta.json"
artifact_path=$(jq -r ".attached_artifacts[] | select(.kind == \"codex-review-summary\") | .export_path" "$out/meta.json" | head -1)
test -f "$out/$artifact_path"
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics and artifact attachment/list/export/check surfaces after final artifact export freshness hardening. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after final artifact export freshness hardening. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after allowing HK exports to include explicit attached artifacts. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -k hk_export -q`: pass (exit 0) — validates: Focused slice-workflow CLI tests cover the generated sync-check export validator change for HK exports with attached artifacts. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"handoff-sync-check\" and (.matched_patterns | index(\".ai/hk/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"codex-review-summary\" and .copied == true)"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
scripts/hk-dev export --format handoff-dir --output "$out" --target . --check --json | jq -e ".fresh == true"
jq -e "any(.attached_artifacts[]; .kind == \"codex-review-summary\" and .export_path != \"\")" "$out/meta.json"
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics, artifact attach/list, and handoff-dir export/check after sync-check accepts explicit attached artifacts. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after final profile diagnostics, artifact attach/list/export, export safety, and sync-check changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after tightening sync-check validation for HK exports with attached artifacts. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -k hk_export -q`: pass (exit 0) — validates: Focused slice-workflow CLI tests cover sync-check validation for HK exports with explicit attached artifacts and missing artifact hashes. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
profile_json=$(scripts/hk-dev profile resolve --target . --json)
printf "%s" "$profile_json" | jq -e ".profile == \"harness-toolkit-root\" and .match_kind == \"direct\""
checks_json=$(scripts/hk-dev checks --target . --changed --json)
printf "%s" "$checks_json" | jq -e "any(.suggested_checks[]; .name == \"handoff-sync-check\" and (.matched_patterns | index(\".ai/hk/**\")))"
artifact_json=$(scripts/hk-dev artifact list --target . --json)
printf "%s" "$artifact_json" | jq -e "any(.artifacts[]; .kind == \"codex-review-summary\" and .copied == true)"
out=<local HK state not exported>
rm -rf "$out"
scripts/hk-dev export --format handoff-dir --output "$out" --target . --json | jq -e ".format == \"handoff-dir\""
scripts/hk-dev export --format handoff-dir --output "$out" --target . --check --json | jq -e ".fresh == true"
mise run sync-check >/dev/null
'`: pass (exit 0) — validates: Dogfood hk profile diagnostics, artifact attach/list, and handoff-dir export/check after final sync-check attached-artifact integrity validation. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after final profile diagnostics, artifact attach/list/export, export safety, and sync-check attached-artifact validation. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after adding path/content-aware review freshness and targeted follow-up review support. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
scripts/hk-dev review add --help | rg -- "--path"
uv run pytest tests/unit/test_harness_kit_2.py -k "review_remains_fresh or review_reports_source or targeted_follow_up" -q
scripts/hk-dev profile resolve --target . --json | jq -e ".match_kind == \"direct\""
scripts/hk-dev artifact list --target . --json | jq -e "any(.artifacts[]; .kind == \"codex-review-summary\")"
'`: pass (exit 0) — validates: Focused dogfood checks cover review freshness diagnostics, targeted follow-up review behavior, artifact attach/list, and export/check surfaces. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -k hk_export -q`: pass (exit 0) — validates: Focused slice-workflow CLI tests cover sync-check validation for HK exports with explicit attached artifacts after review freshness changes. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after profile diagnostics, artifact attach/list/export, sync-check, and path-aware review freshness changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests pass after path-aware review freshness, targeted follow-up review, artifact export safety, and sync-check updates. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -k hk_export -q`: pass (exit 0) — validates: Focused slice-workflow CLI tests cover sync-check validation for HK exports with explicit attached artifacts, local path rejection, and metadata symlink checks. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
scripts/hk-dev review add --help | rg -- "--path"
uv run pytest tests/unit/test_harness_kit_2.py -k "review_remains_fresh or review_reports_source or targeted_follow_up or review_add_path_normalizes" -q
scripts/hk-dev profile resolve --target . --json | jq -e ".match_kind == \"direct\""
scripts/hk-dev artifact list --target . --json | jq -e "any(.artifacts[]; .kind == \"codex-review-summary\")"
'`: pass (exit 0) — validates: Focused dogfood checks cover review add --path, review freshness diagnostics, profile diagnostics, artifact attach/list, and export/check surfaces. — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Full repo quality gate passes after profile diagnostics, artifact attach/list/export, sync-check, and path-aware review freshness changes. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after profile diagnostics, artifact attach/list/export, sync-check, and path-aware review freshness changes. — `<local HK state not exported>`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Final contract tests pass for profile diagnostics, artifact attach/list/export, sync-check attached-artifact validation, and path-aware review freshness. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_slice_workflow_cli.py -k hk_export -q`: pass (exit 0) — validates: Final focused slice-workflow CLI tests cover sync-check validation for HK exports with explicit attached artifacts, missing hashes, local-only metadata paths, and metadata symlink checks. — `<local HK state not exported>`
- `bash -lc '
set -euo pipefail
scripts/hk-dev review add --help | rg -- "--path"
uv run pytest tests/unit/test_harness_kit_2.py -k "review_remains_fresh or review_reports_source or targeted_follow_up or review_add_path_normalizes" -q
scripts/hk-dev profile resolve --target . --json | jq -e ".match_kind == \"direct\""
'`: pass (exit 0) — validates: Final dogfood checks cover review add --path UX, review freshness diagnostics, profile diagnostics, artifact attach/list, and export/check surfaces. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Final full repo quality gate passes after profile diagnostics, artifact attach/list/export, sync-check, and path-aware review freshness changes. — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK handoff export is structurally valid, including attached artifacts. — `<local HK state not exported>`

## Readiness
- Status: `ready-with-dangerous-skips`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/harness-kit-lifecycle-design.md, docs/portable-workflow.md)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/snapshot.py, +9 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .agent/skills/hk-session-artifacts/SKILL.md, AGENTS.md, README.md, +21 more)
- profile-check:generated-stack-smoke: pass — required profile check recorded: generated-stack-smoke (matched templates/.agent/skills/slice-workflow/cli/src/slice_workflow_cli/checks.py)
- profile-review:codex-review: pass — review dangerously skipped: codex-review; reason: Final Codex CLI review attempt was unavailable/aborted due Codex transport/auth/stdin errors after earlier Codex review rounds had been addressed.; mitigation: Final fresh-context lifecycle and agent-friendly reviews covered the current changed paths, and final validation bundle passed focused tests plus mise run check; rerun codex review before merge if the Codex connector is healthy.
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/app/lifecycle.py, src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/snapshot.py, +9 more)
- sync: pass — sync checkpoint fresh

## Review
- codex-cli / codex-exec [codex-review] (correctness-regression-test-adequacy): Codex review initially found an artifact export freshness bypass when exported artifacts and meta.json file_hashes were both edited; fixed by requiring copied artifact file_hash metadata and comparing exported artifact bytes to ledger hashes. Final Codex rerun found no blocking issues. paths: .agent/skills/hk-session-artifacts/SKILL.md, README.md, SPEC.md, +14 more. [accepted]
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): Fresh-context lifecycle review found no blockers after export path-safety fixes. Verified symlinked work artifact dirs are rejected, copied artifact sources stay inside work artifacts, export --check rejects symlinked files and unsafe file_hash paths, and readiness semantics are unchanged. paths: .agent/skills/hk-session-artifacts/SKILL.md, README.md, SPEC.md, +14 more. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context (agent-friendly-cli): Fresh-context CLI review found no blockers. Profile diagnostics are additive, artifact attach/list help and JSON are usable, and hk-session-artifacts now guides attach/list/handoff with --json examples. paths: .agent/skills/hk-session-artifacts/SKILL.md, README.md, SPEC.md, +14 more. [accepted]
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): Final targeted fresh-context review found no blockers. Verified path/content-aware review freshness, hk review add --path, generated active HK export review-neutral behavior, artifact export/check safety, and sync-check attached-artifact validation. paths: .agent/skills/hk-session-artifacts/SKILL.md, AGENTS.md, README.md, +24 more. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context (agent-friendly-cli): Final targeted agent-friendly CLI review found no blockers. Verified hk review add --path UX/path normalization, additive profile diagnostics, artifact attach/list JSON/help, and docs/help. paths: .agent/skills/hk-session-artifacts/SKILL.md, AGENTS.md, README.md, +24 more. [accepted]

## Attached artifacts
- validation-transcript: `artifacts/artifact_11_validation-transcript_artifact_20260512_101527_895802_validation-transcript_artifact-attach-dogfood.md` (copied, redaction=external, 305 bytes, sha256:57ad4cf97a31) — Artifact attach dogfood transcript
- codex-review-transcript: `artifacts/artifact_23_codex-review-transcript_artifact_20260512_112706_866446_codex-review-transcript_codex-events.jsonl` (copied, redaction=external, 205838 bytes, sha256:0ebd94445029) — Codex review JSONL
- codex-review-summary: `artifacts/artifact_24_codex-review-summary_artifact_20260512_112707_593445_codex-review-summary_codex-last.md` (copied, redaction=external, 117 bytes, sha256:8076b78db84c) — Codex review final message

## Dangerous skips
- review: codex-review — reason: Final Codex CLI review attempt was unavailable/aborted due Codex transport/auth/stdin errors after earlier Codex review rounds had been addressed.; mitigation: Final fresh-context lifecycle and agent-friendly reviews covered the current changed paths, and final validation bundle passed focused tests plus mise run check; rerun codex review before merge if the Codex connector is healthy.
