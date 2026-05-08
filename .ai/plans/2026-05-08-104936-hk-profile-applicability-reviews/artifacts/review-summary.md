# Review Summary — hk-profile-applicability-reviews

Fresh-context review used two subagents:

1. `reviewer` for correctness, readiness policy, compatibility, and shell-first boundaries.
2. `agent-friendly-cli` for the new command UX around `hk checks --changed`, `hk validate --check`, `hk review prompt REVIEW_NAME`, and `hk review add --review`.

## Initial findings

Blocking findings:

- Path glob matching was too broad: `*.md` matched nested docs and `github/**` matched `.github/**` because matching used `fnmatch` over full paths and stripped leading dots.
- `hk checks --changed --profile/--profiles-dir` could advertise required items that lifecycle commands would not enforce because lifecycle profile resolution uses user config, not discovery-only profile flags.
- `hk checks --changed` reminder still showed generic `hk validate --why` / `hk review add` forms even when required named items needed `--check` / `--review`.
- Named review prompt hardcoded `--backend subagent` even when the profile review declared another backend.

Non-blocking findings:

- Check/review names should be durable shell-safe identifiers and unique within a profile.
- `docs/agent-adoption.md` made generic and named review prompt flows look cumulative instead of either/or.
- `prompt_file_text` should not be included in normal checks/profile JSON output.

## Fixes applied

- Replaced path matching with segment-aware glob semantics where `*` stays within a path segment and `**` crosses directories; stopped stripping leading dots except literal `./` prefixes.
- Added tests proving `*.md` does not match `docs/foo.md` and `github/**` does not match `.github/**`.
- Added unique, shell-safe validation for profile check/review names.
- Added `enforced` plus `record_command` / `prompt_command` fields to suggestions.
- `hk checks --changed` now marks required items from discovery-only profile inspection as `enforced=false`; readiness-enforced required items come from the target's resolved user-config profile.
- `hk checks --changed` text output now shows copyable record/prompt follow-ups for suggested checks/reviews.
- Named review prompt now uses the profile review backend/rubric in its copyable `hk review add --review ...` hint.
- Removed `prompt_file_text` from normal `hk checks --json` / `hk profile show --json` output; named review prompt still renders the file content.
- Clarified generic vs named review prompt flows in `docs/agent-adoption.md`.

## Disposition

Accepted after fixes. No known blocking review findings remain.
