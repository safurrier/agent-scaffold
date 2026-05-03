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

## Final Review Status

All actionable Codex review findings from the first review pass have been addressed. A follow-up validation run passed via `mise run check` captured in local Harness Kit evidence:

```text
.harness-local/harness-kit/root/work/2026-05-03-132345-harness-kit-2-implementation/artifacts/ev_20260503_135034_228031.transcript.log
```
