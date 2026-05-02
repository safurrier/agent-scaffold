# Review

## Review Context

- Mode: external
- Backend: pi-subagent-reviewer
- Reviewer: reviewer subagent

## Rubrics

- core-quality

## Findings

- Addressed: Quickstart now shows both built-in-only discovery and explicit `--profiles-dir ~/.config/harness-toolkit/profiles` discovery so agents do not miss custom profiles.
- Addressed: Skill now warns agents to check for an existing TOML destination and ask before overwrite; it also points to `hk profile create` overwrite protection.
- Addressed: Rust mise example no longer tells agents to blindly trust `.mise.toml`; it says to inspect and ask the user before `mise trust`.
- Addressed: Bundled skill index now lists `harness-kit-profile-authoring`.

## Disposition

- Ready for PR.
- External review notes were addressed with targeted edits.
- Skill validation and docs/context checks pass.

## Codex Feedback Follow-up

- Addressed Codex inline feedback on `profile-mining.md`: custom-profile handoff templates now include `--profiles-dir <profiles-dir>` because custom profiles are not loaded without an explicit catalog.
- Aligned custom-profile examples in `examples.md` with the same `--profiles-dir <profiles-dir>` handoff pattern.

## User-Level Guidance Follow-up

- Added a generic `harness-kit-workflow.md` reference to the generated skill.
- Added portable workflow docs showing a compact user-level `AGENTS.md` bootstrap that avoids loading full workflow details every session.
- Linked README to the user-level AGENTS bootstrap docs.
