# HK export: `2026-05-11-161048-worktree-profile-resolution`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-11-161048-worktree-profile-resolution --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-11-161048-worktree-profile-resolution`
- Branch: `hk-worktree-profile-resolution`
- Git SHA: `9af0147`
- Dirty: `true`
- Sync status: `synced`

## Context
- External Git docs indicate linked worktrees share a common Git directory; HK profile resolution now reuses canonical configured target bindings only across that Git worktree family, preserving monorepo subpaths by projecting repo-relative target paths into the active worktree.
- GitHub Codex review found that  inside a linked worktree fell back because Git was invoked with  on a file path. The fix probes the nearest existing directory for Git metadata while keeping the original target path for prefix matching.
- GitHub Codex review found that hk profile resolve --target <file> inside a linked worktree fell back because Git was invoked with git -C on a file path. The fix probes the nearest existing directory for Git metadata while keeping the original target path for prefix matching.
- Architecture skill run: GitClient is worthwhile if it is a medium-width semantic module, not a generic subprocess pass-through. It should concentrate env scrubbing, file-target probing, Git error behavior, text/binary output policy, pathspec helpers, and worktree metadata; domain hashing/sync/profile semantics stay in snapshot/local/profiles modules.

## Plan
- Make HK profile resolution Git-worktree-aware so canonical configured targets apply inside linked worktrees. Keep direct path matching first, preserve monorepo subpath specificity by projecting configured target paths across worktree roots, avoid remote-URL auto-matching, add unit/CLI/agent-simulation coverage, validate with real worktree dogfood, update docs/spec as needed, then open PR.
- Extend the active workstream to add a narrow internal GitClient seam. Architecture review supports a medium-width semantic Git module: centralize trusted internal Git subprocess calls behind src/harness_toolkit/kit/git/client.py, keep hk validate command capture separate in capture/process.py, preserve direct behavior via TDD characterization, migrate repo identity/profile worktree resolution/snapshot/local Git calls, add a contract test for kit subprocess usage, rerun agent-sim/contract/check/sync-check, dogfood profile resolution, and run fresh agent-friendly CLI plus lifecycle reviews before updating PR #16.

## Decisions and spec reflection
- Worktree-aware profile resolution is safe when keyed by shared git-common-dir plus repo-relative path projection; separate clones with matching remotes remain default-profile fallback to avoid surprising profile inheritance.
- Centralize internal trusted Git subprocess calls in kit.git.client.GitClient rather than adding a generic subprocess framework. Command evidence capture remains in kit.capture.process; domain-level diff hashing, sync safety, profile resolution, and readiness stay in their existing modules and call the Git client seam.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests cover SPEC/docs/frontmatter and profile contract invariants after worktree-resolution docs changes. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_162313_069680.transcript.log`
- `bash -lc 'set -euo pipefail
parent=$(mktemp -d -t hk-worktree-profile-dogfood.XXXXXX)
wt="$parent/harness-toolkit-linked"
cleanup() {
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  rmdir "$parent" >/dev/null 2>&1 || true
}
trap cleanup EXIT
git worktree add --detach "$wt" HEAD >/dev/null
json=$(scripts/hk-dev profile resolve --target "$wt" --json)
printf "%s\n" "$json"
python3 -c '"'"'import json,sys; p=json.load(sys.stdin); assert p["profile"] == "harness-toolkit-root", p; assert "worktree" in p["reason"], p; assert p["matched_target"] == ".", p'"'"' <<< "$json"
'`: pass (exit 0) — validates: Dogfood this checkout's hk profile resolution against a temporary linked Git worktree and require it to resolve the canonical harness-toolkit profile through worktree-family projection. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_162328_393338.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after adding worktree-aware profile resolution, docs, unit tests, and agent simulation. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_162335_386290.transcript.log`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests cover SPEC/docs/frontmatter and profile contract invariants after worktree-resolution docs changes. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_164716_074824.transcript.log`
- `bash -lc 'set -euo pipefail
parent=$(mktemp -d -t hk-worktree-profile-dogfood.XXXXXX)
wt="$parent/harness-toolkit-linked"
cleanup() {
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  rmdir "$parent" >/dev/null 2>&1 || true
}
trap cleanup EXIT
git worktree add --detach "$wt" HEAD >/dev/null
json=$(scripts/hk-dev profile resolve --target "$wt" --json)
printf "%s\n" "$json"
python3 -c '"'"'import json,sys; p=json.load(sys.stdin); assert p["profile"] == "harness-toolkit-root", p; assert "worktree" in p["reason"], p; assert p["matched_target"] == ".", p'"'"' <<< "$json"
'`: pass (exit 0) — validates: Dogfood this checkout's hk profile resolution against a temporary linked Git worktree and require it to resolve the canonical harness-toolkit profile through worktree-family projection. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_164739_485033.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after adding worktree-aware profile resolution, docs, unit tests, and agent simulation. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_164746_328613.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK handoff export is fresh and repo sync-check accepts all HK export packages. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_165557_812884.transcript.log`
- `bash -lc 'set -euo pipefail
parent=$(mktemp -d -t hk-worktree-profile-file-dogfood.XXXXXX)
wt="$parent/harness-toolkit-linked"
cleanup() {
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  rmdir "$parent" >/dev/null 2>&1 || true
}
trap cleanup EXIT
git worktree add --detach "$wt" HEAD >/dev/null
json=$(scripts/hk-dev profile resolve --target "$wt/README.md" --json)
printf "%s\n" "$json"
uv run python -c '"'"'import json,sys; p=json.load(sys.stdin); assert p["profile"] == "harness-toolkit-root", p; assert "worktree" in p["reason"], p; assert p["matched_target"] == ".", p'"'"' <<< "$json"
'`: pass (exit 0) — validates: Dogfood this checkout's hk profile resolution against a temporary linked Git worktree file target, proving file-scoped targets resolve through nearest-directory Git metadata and still match the canonical profile. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_173241_615333.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after addressing GitHub Codex file-target worktree feedback. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_173252_532878.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK handoff export remains fresh after addressing GitHub Codex feedback, and repo sync-check accepts all HK export packages. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_173756_734986.transcript.log`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests remain green after regenerating the HK export and addressing GitHub Codex feedback. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_173807_434448.transcript.log`
- `bash -lc 'set -euo pipefail
parent=$(mktemp -d -t hk-gitclient-worktree-dogfood.XXXXXX)
wt="$parent/harness-toolkit-linked"
cleanup() {
  git worktree remove --force "$wt" >/dev/null 2>&1 || true
  rmdir "$parent" >/dev/null 2>&1 || true
}
trap cleanup EXIT
git worktree add --detach "$wt" HEAD >/dev/null
json=$(scripts/hk-dev profile resolve --target "$wt/README.md" --json)
printf "%s\n" "$json"
uv run python -c '"'"'import json,sys; p=json.load(sys.stdin); assert p["profile"] == "harness-toolkit-root", p; assert "worktree" in p["reason"], p; assert p["matched_target"] == ".", p'"'"' <<< "$json"
rg -n "subprocess\\.(run|Popen)|import subprocess" src/harness_toolkit/kit | tee /tmp/hk-gitclient-subprocess-sites.txt
uv run python - <<'"'"'PY'"'"'
from pathlib import Path
allowed = {"src/harness_toolkit/kit/git/client.py", "src/harness_toolkit/kit/capture/process.py"}
for line in Path("/tmp/hk-gitclient-subprocess-sites.txt").read_text().splitlines():
    path = line.split(":", 1)[0]
    assert path in allowed, line
PY
'`: pass (exit 0) — validates: Dogfood this checkout's GitClient-backed profile resolution against a temporary linked Git worktree file target. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_181627_617161.transcript.log`
- `uv run pytest -m contract -q`: pass (exit 0) — validates: Contract tests cover SPEC/docs/frontmatter and the new GitClient subprocess-centralization contract. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_181636_953651.transcript.log`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate passes after adding GitClient and migrating internal kit Git subprocess calls. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_181700_214428.transcript.log`
- `mise run sync-check`: pass (exit 0) — validates: Generated HK handoff export remains fresh after extending the workstream to cover GitClient refactor, and repo sync-check accepts all HK export packages. — `.harness-local/harness-kit/root/work/2026-05-11-161048-worktree-profile-resolution/artifacts/ev_20260511_182924_312926.transcript.log`

## Readiness
- Status: `ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- profile-check:focused-contract-tests: pass — required profile check recorded: focused-contract-tests (matched SPEC.md, docs/harness-kit-lifecycle-design.md, docs/portable-workflow.md)
- profile-check:hk-dev-dogfood: pass — required profile check recorded: hk-dev-dogfood (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/__init__.py, src/harness_toolkit/kit/git/client.py, +5 more)
- profile-check:fast-gate: pass — required profile check recorded: fast-gate (matched .ai/hk/2026-05-11-161048-worktree-profile-resolution/README.md, .ai/hk/2026-05-11-161048-worktree-profile-resolution/artifacts/README.md, .ai/hk/2026-05-11-161048-worktree-profile-resolution/meta.json, +15 more)
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched .ai/hk/2026-05-11-161048-worktree-profile-resolution/README.md, .ai/hk/2026-05-11-161048-worktree-profile-resolution/artifacts/README.md, .ai/hk/2026-05-11-161048-worktree-profile-resolution/meta.json)
- profile-review:codex-review: pass — required profile review recorded: codex-review (matched SPEC.md, docs/harness-kit-lifecycle-design.md, docs/portable-workflow.md, +11 more)
- profile-review:hk-lifecycle-review: pass — required profile review recorded: hk-lifecycle-review (matched src/harness_toolkit/kit/cli.py, src/harness_toolkit/kit/git/__init__.py, src/harness_toolkit/kit/git/client.py, +5 more)
- sync: pass — sync checkpoint fresh

## Review
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): No blockers. Verified direct-match precedence, git-common-dir worktree projection, projected specificity for mixed configured-target origins, separate-clone fallback, CLI/JSON metadata, and test/docs coverage. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context [codex-review] (correctness-regression-test-adequacy): No blockers. CLI-facing review found additive JSON fields, readable human output, safe fallback behavior, no remote-URL auto-match, and adequate docs/tests; noted only that non-existent/file targets safely fall back. [accepted]
- github-codex / chatgpt-codex-connector [codex-review] (correctness-regression-test-adequacy): GitHub Codex reported a P1 file-target worktree metadata issue; addressed by probing nearest existing directory for git metadata while preserving original target matching, with regression coverage for linked-worktree file targets. [accepted]
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): No blockers on the Codex feedback fix. Verified nearest-directory git probing, preserved original target path matching, and linked-worktree file-target regression coverage. [accepted]
- pi-subagent / reviewer-fresh-context [hk-lifecycle-review] (hk-lifecycle-readiness-safety): No blockers on GitClient refactor. Verified seam is semantic enough, command evidence capture remains separate, domain hashing/sync/profile logic stays in place, subprocess usage in kit is centralized, and tests cover file-target worktree behavior and env cleanup. Non-blocking note: exact digest fixtures could further harden future hash refactors. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context [codex-review] (correctness-regression-test-adequacy): No blockers from agent-friendly CLI review. Public profile resolve JSON shape remains additive/stable, CLI behavior stays read-only/discoverable, worktree profile safety remains explicit, and docs/spec explain the GitClient vs command-capture subprocess split. Noted behavior change: internal Git queries now consistently clear ambient Git env vars. [accepted]
- codex-cli / codex-exec [codex-review] (correctness-regression-test-adequacy): Codex CLI review found no code defects in the GitClient refactor but flagged the generated HK export as not-ready because handoff-sync-check evidence was missing from the committed handoff view. Fixed by regenerating the HK export after handoff-sync-check evidence so README/meta report ready. [accepted]
