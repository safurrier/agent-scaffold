## Summary
- Work: `2026-05-06-101104-sync-exclude-literal` on `feat/sync-exclude` at `3b3dfce`
- Readiness: `ready`; sync: `synced`; dirty: `true`
- Verify hk sync --exclude accepts explicit untracked literal local paths without a hardcoded allowlist.

## Decisions
- Allow literal untracked local paths to be excluded when explicitly recorded and revalidated; tracked/staged/root/pathspec paths remain invalid.

## Validation
- `git status --short`: pass (exit 0) — A direct git status proves the dogfood repo has one tracked edit plus three untracked local paths to exclude.
