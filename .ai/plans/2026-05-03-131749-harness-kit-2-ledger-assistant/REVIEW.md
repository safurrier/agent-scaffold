# Review

## External Review

- Backend: Codex CLI 4-pass review
- Review path: `/var/folders/kf/js4h91w14pl7zwfgnvj896b00000gq/T/tmp.eX2D4saAb6/review.md`
- Review date: 2026-05-03

## Findings and Disposition

### P1: `hk sync --check` can falsely pass after staged or untracked changes

Disposition: fixed.

Changes:

- `git_diff_hash()` now hashes unstaged diff, staged diff, and `git status --porcelain`.
- Added regression coverage for untracked and staged changes after a sync checkpoint.

### P1: `hk spec outline --json` crashes

Disposition: fixed.

Changes:

- `spec outline --json` now serializes the `SpecOutline` dataclass through `json_dump_dataclass()`.
- Added CLI-level JSON parse coverage.

### High: captured command metadata can persist secrets

Disposition: fixed baseline.

Changes:

- Evidence metadata now redacts `command_display`, `argv`, and `shell_command` unless `--raw-log` is explicit.
- Existing transcript redaction remains in place.
- Added regression coverage ensuring seeded secret text does not appear in `evidence.jsonl`.

### Medium: `hk capture --json` does not produce parseable stdout JSON

Disposition: fixed.

Changes:

- CLI JSON mode streams wrapped command output to stderr and leaves stdout parseable as JSON.
- Added CLI-level JSON parse coverage.

### Medium: `hk handoff --format` accepts invalid values and ignores `pr`

Disposition: fixed for invalid values; `pr` currently renders the same conservative Markdown body.

Changes:

- `handoff --format` is typed as `Literal["markdown", "pr", "json"]` so invalid values fail.
- Added invalid-format CLI coverage.

### Medium: capture transcripts are accumulated fully in memory

Disposition: fixed.

Changes:

- Capture now streams redacted chunks directly to transcript files.

### Medium: design doc advertises unsupported `hk brief --markdown`

Disposition: fixed.

Changes:

- Added a no-op `--markdown` flag as an explicit alias for default Markdown output.

### Medium: portable workflow docs overstate shared state flags

Disposition: fixed.

Changes:

- Split legacy `--mode`/`--state-root` command documentation from 2.0 `--no-local-files` command documentation.

### Low: external-state test writes under the real user state home

Disposition: fixed.

Changes:

- External state test now sets `XDG_STATE_HOME` to a temp path.

## Follow-up Review

- Backend: Codex CLI 4-pass follow-up review
- Review path: `/var/folders/kf/js4h91w14pl7zwfgnvj896b00000gq/T/tmp.wxzF5SgGDk/review.md`

### High: split-argument secrets in captured metadata

Disposition: fixed.

Changes:

- Added argv-aware redaction for sensitive option names such as `--token`, `--password`, and `--api-key`.
- Extended display/shell redaction to cover whitespace-separated sensitive arguments.
- Added regression coverage that checks `evidence.jsonl` does not contain the seeded split-argument token.

### High: untracked file content freshness

Disposition: fixed.

Changes:

- `git_diff_hash()` now hashes untracked file contents from `git ls-files --others --exclude-standard -z` in addition to unstaged diff, staged diff, and status output.
- Added regression coverage for editing an already-untracked file after a checkpoint.

### Medium: missing executable capture evidence

Disposition: fixed.

Changes:

- `hk capture` now catches `OSError` from process startup, writes failed evidence and transcript, and returns exit code 127.

### Medium: evidence kind validation

Disposition: fixed.

Changes:

- `capture_command()` validates evidence kinds.
- CLI `--kind` is typed as a literal choice.

### Medium: design docs overstate initial brief/handoff behavior

Disposition: fixed.

Changes:

- Design docs now mark evidence summaries, changed-file summaries, manual evidence labels, review focus, and continuation notes as follow-ups rather than claiming current implementation.

### Low: stale plan metadata

Disposition: fixed.

Changes:

- Updated `META.yaml` with source, decision record, review backend, and current in-progress status.

## Final Review Status

All actionable findings from the first and follow-up Codex review passes have been addressed. Follow-up validation passed via `mise run check` captured in local Harness Kit evidence:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_140555_376622.transcript.log
```
