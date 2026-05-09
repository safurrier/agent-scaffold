# Review Summary — profile-dir-relative-paths

## Initial review

Two Pi subagents reviewed the uncommitted diff:

- `reviewer` focused on parser/loading precedence, path matching semantics, tests, and docs.
- `agent-friendly-cli` focused on help/error/actionability for agents.

Initial blockers:

1. Mixed-coordinate negation could be bypassed because `_matched_paths()` used `any(spec.match_file(candidate))` across repo-root and target-relative candidates. Fixed by applying patterns sequentially across candidate paths and adding regression coverage.
2. Help still over-emphasized `--profiles-dir`, and missing configured profile dirs could block `hk profile create`. Fixed by describing configured dirs as automatic, framing `--profiles-dir` as ad hoc, improving missing-dir errors, and making `profile create` avoid catalog loading.

## Re-review

Both reviewers accepted the updated diff with no blockers. They verified:

- `profiles_dir` / `profiles_dirs` parsing, normalization, loading, and precedence.
- target-relative matching while preserving repo-root output.
- mixed root/target include-negation regression coverage.
- actionable configured-dir errors.
- `hk profile create` bootstrap behavior.
- aligned CLI help, README/SPEC/docs, and profile-authoring skill guidance.

## Disposition

Accepted.
