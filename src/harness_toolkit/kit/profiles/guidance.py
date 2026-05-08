"""Profile selection guidance text."""

PROFILE_SELECTION_GUIDANCE = """Choose the closest available profile yourself unless user config explicitly resolves one; the CLI does not use heuristic auto-selection.

Match the profile to the target scope, not just the repository root. In monorepos,
pass `--target` as the module/package/crate directory that owns the work, then
inspect that module's files first and repo-level AGENTS.md/README guidance second.
Prefer profiles in this order:
1. exact target/module profile
2. repo-specific profile
3. stack/task-runner profile
4. generic fallback

Tell the user once which profile you chose and why, then use that profile
consistently for plan, checks, and readiness.

Examples:
- --target my_project/api and profile my-project-api exists -> my-project-api
- --target my_project/api and no module profile exists, but pyproject.toml exists -> python
- --target crates/tui and profile foreman-tui exists -> foreman-tui
- --target crates/tui and no module profile exists, but Cargo.toml exists -> rust
- Rust repo with mise task contract but no exact module profile -> rust-mise
- no close target/module match -> generic
"""
