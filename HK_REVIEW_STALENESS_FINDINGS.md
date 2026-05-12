# HK Review Staleness Findings

Date: 2026-05-12

## Why this note exists

During the `profile-diagnostics-artifacts` workstream, the implementation entered an expensive review/fix/review cycle. The reviews were useful — they found real artifact export integrity bugs — but HK kept marking previous reviews stale after every small diff change. That made the workflow feel like it could keep asking for fresh review indefinitely.

This note captures what happened and what to reconsider before hardening the review freshness model further.

## What happened

The workstream added:

- additive profile diagnostics:
  - `ProfileResolution.match_kind`
  - `ProfileSuggestion.matched_patterns`
- `hk artifact list`
- handoff-dir export of copied attached artifacts
- artifact export/check path-safety hardening
- sync-check support for HK exports containing explicit attached artifacts

Review rounds found concrete issues in the artifact export path:

1. Copied artifact export filenames could be influenced by tampered ledger `kind` values.
2. Copied artifact sources could be tampered to point outside the active work artifact directory.
3. Symlinked `work_dir/artifacts` directories could move copied artifact state outside HK’s intended local-state boundary.
4. `hk export --check` could follow symlinked exported files.
5. `hk export --check` trusted unsafe `file_hashes` paths from tampered `meta.json`.
6. `hk export --check` could pass after an exported artifact and `file_hashes` metadata were edited together.
7. `mise run sync-check` initially rejected the new export shape, then accepted attached artifact paths without requiring their file/hash linkage.

Each fix changed the diff. Because HK review freshness is tied to current diff state, those changes made earlier review evidence stale, even when the new change only addressed a review finding or regenerated handoff metadata.

## Observed failure mode

HK’s current model is intentionally conservative: accepted reviews are fresh only for the current diff hash. That is safe, but it creates a loop when review-driven fixes are incremental:

```text
review finds issue
→ fix issue
→ review becomes stale because diff changed
→ rerun review
→ review finds smaller follow-up issue
→ fix issue
→ review becomes stale again
```

This is especially visible for safety-sensitive generated/export code, where each reviewer can find one more edge case after the previous one is fixed.

The problem is not that HK asks for review. The problem is that HK has no way to distinguish:

- a large unreviewed product/code change,
- a small fix directly responding to review feedback,
- a generated handoff/export metadata refresh,
- validation evidence updates,
- attached review transcript artifacts,
- docs/notes that summarize review findings.

All of those can affect the diff hash and make review stale.

## Questions to answer

1. Should review freshness be based on the entire current diff, or on a subset of review-relevant paths?
2. Should HK ignore generated HK export paths, attached transcript artifacts, and other evidence-only paths when determining review staleness?
3. Should there be a notion of “review-addressed delta” where a prior review remains acceptable if the only new changes are linked to fixing that review’s findings?
4. Should `hk review add` record the changed paths and diff hash it reviewed, while readiness reports the precise unreviewed delta rather than simply “review stale”?
5. Should profile-required reviews use path-specific freshness, so a docs-only or export-only change does not stale a source-code review?
6. Should HK support an explicit finalization mode for generated handoff updates, e.g. “review remains fresh except for regenerated `.ai/hk/**` export files produced after the review”?

## Possible product directions

### 1. Path-scoped review freshness

Track review freshness against the paths that triggered the profile review, not necessarily the entire work diff.

Example:

- `hk-lifecycle-review` triggered by `src/harness_toolkit/kit/**`.
- A later `.ai/hk/**` export refresh should not stale that review.
- A later `src/harness_toolkit/kit/local.py` change should stale it.

This matches how profile checks already have path rules.

### 2. Evidence/export exclusions for review freshness

Define a conservative set of review-freshness-neutral paths, likely including:

- `.ai/hk/<active-work-id>/**` generated export files
- local transcript attachment metadata once the source code has already been reviewed
- possibly validation transcript artifacts

Caution: this must not hide meaningful source changes inside exported artifacts or docs. The exclusion should apply only to generated HK export paths and perhaps only when `hk export --check` / `mise run sync-check` passes.

### 3. Reviewed-delta accounting

Instead of a binary stale/fresh result, readiness could say:

```text
review stale: 3 paths changed since review
- src/.../local.py
- templates/.../checks.py
- tests/unit/...
```

Then, after a review-driven fix, HK could support recording a follow-up review that covers only those changed paths. Readiness would pass when every current changed path is covered by at least one accepted review record.

### 4. Review-response records

Add a structured way to say “this commit/diff chunk was made in response to review X,” with a required final verification. This may be too complex for HK’s desired simplicity, but it captures the actual workflow better than repeatedly invalidating the whole review.

### 5. Separate code review freshness from handoff readiness freshness

Treat review freshness and generated handoff freshness as separate gates:

- source/product changes require fresh external review;
- generated `.ai/hk` export changes require `handoff-sync-check` / `sync-check`, not another external review.

This likely gives the best UX/safety tradeoff.

## Recommendation

Start with a practical improvement:

1. Keep deterministic path/content facts for reviewed paths instead of relying only on a whole-diff hash.
2. Exclude generated active HK export files from review freshness when they are under `.ai/hk/<active-work-id>/`; validate those with export/sync checks instead.
3. Make stale review diagnostics path-specific, so agents see exactly which paths need fresh review.
4. Support targeted follow-up review records for the paths changed after earlier review instead of requiring a full broad review every time.
5. Do **not** add a broad self-attestation path. If meaningful source risk remains uncovered, require independent/fresh-context review or an explicit dangerous review skip.

This preserves deterministic evidence while avoiding review churn caused only by generated handoff/export refreshes or small review-response deltas.

## Related observed behavior from this workstream

- The review loop was not arbitrary; reviewers found real defects.
- The expensive part was the repeated invalidation after follow-up fixes and handoff/export updates.
- `hk artifact attach` dogfood worked and was useful once `hk artifact list --json` existed.
- Artifact export safety needs to be treated as security-sensitive because HK copies files into shareable handoff packages.
- Sync-check and HK export validation must evolve together when export shape changes.

## Follow-up candidate

Create a separate HK work item for review freshness semantics:

```bash
hk start review-freshness-path-scoping \
  --plan "Make HK review freshness path-aware and ignore verified generated HK export refreshes without weakening source-change review requirements."
```

Validation should include:

- tests where `.ai/hk/<active-work-id>/**` changes after review do not stale source review when export check passes;
- tests where source changes after review still stale review;
- tests where generated export changes fail readiness if export check is stale;
- agent simulation showing final export regeneration does not force another external review loop.
