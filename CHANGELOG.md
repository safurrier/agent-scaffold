# Changelog

## v0.2.0 - 2026-05-15

### Added

- Added `hk` / `harness-kit`, the portable lifecycle CLI for existing repositories.
- Added ledger-backed lifecycle records for context, plans, decisions, validation evidence, external-enough reviews, sync checkpoints, summaries, and handoff rendering.
- Added configurable HK profile catalogs, target bindings, changed-path check/review suggestions, profile review prompts, and profile resolution across linked Git worktrees.
- Added compact `.ai/hk/<work-id>/` handoff exports with `README.md`, `meta.json`, explicit artifacts, and strict `hk export --check` integrity validation.
- Added artifact attachment support and export metadata suitable for dashboards and review handoffs.
- Added repo-local and generated `harness-kit-profile-authoring` skill guidance for mining validation contracts and avoiding closeout loops.

### Changed

- Made Harness Toolkit’s own workflow HK-native: generated `.ai/hk` exports are the normal committed handoff artifact, while legacy `.ai/plans` remains scaffold/generated-repo compatibility.
- Made active `.ai/hk/<work-id>/` exports lifecycle-neutral for sync, validation/review freshness, readiness changed paths, and profile matching, while preserving non-active export staleness.
- Improved review freshness to track changed-path coverage so targeted follow-up reviews can satisfy readiness after small post-review fixes.
- Updated profile authoring guidance to distinguish focused iteration checks, final closeout gates, heavy/CI parity, handoff/export checks, required reviews, and advisory reviews.
- Updated generated profile templates to discourage broad expensive `required_when = ["*"]` defaults and guide targeted validation/review follow-up.
- Improved CLI/help/docs for install, release, portable workflow adoption, profile reviews, and HK lifecycle design.

### Fixed

- Hardened sync/readiness diagnostics around explicit excludes, source-risk drift, active HK exports, and stale handoff artifacts.
- Tightened export integrity checks for unexpected files, invalid generated text, generated/hash tampering, symlinks, unsafe hash paths, and attached-artifact tampering.
- Preserved user-authored export `Status:` notes while keeping generated export README content stable across export/check cycles.

## v0.1.0 - 2026-05-09

### Added

- Initial GitHub-sourced `agent-scaffold` release before the Harness Toolkit rename and HK portable lifecycle split.
- Provided the original scaffold initializer, generated mise task contract, Python/Go/Rust stack templates, and local development documentation.
