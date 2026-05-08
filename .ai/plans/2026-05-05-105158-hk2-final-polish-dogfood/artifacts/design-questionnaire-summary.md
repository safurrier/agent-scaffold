# HK2 final polish design questionnaire summary

Date: 2026-05-05

## Accepted scope

One more HK2 polish slice should include:

- One-shot explicit sync exclusions:
  - `hk sync --exclude PATH --reason '...'`.
  - `--exclude` may be repeated only to exclude multiple paths, e.g. `--exclude .pi --exclude .claude/worktrees`.
- Structured spec impact:
  - `hk decide '...' --spec-impact none|updated|not-needed`.
  - optional `--spec-ref PATH` values.
- Review ergonomics:
  - independent review remains preferred;
  - fresh-context subagent review is the minimum acceptable fallback;
  - add `hk review prompt` to print a copy-paste fresh-context reviewer prompt;
  - document future configurable review sources, but do not implement config now.
- Status/help cleanup:
  - add phase labels: `not-started`, `planning`, `implementing`, `finalizing`, `ready`;
  - further demote advanced `work`/`note`/`capture` surfaces in docs/help without removing them.
- Validation dogfood:
  - run a less-guided three-worker PR-sized dogfood: workers should only be told to use HK and begin by exploring the CLI.

## Sync exclusion semantics

Accepted constraints:

- `--reason` is required whenever `--exclude` is used.
- Excluded paths must currently appear in git status, so typos do not produce fake exclusions.
- Sync checkpoint events should store:
  - excluded path list;
  - reason;
  - normal/non-excluded diff hash;
  - excluded status/hash metadata sufficient for handoff.
- Readiness should pass only if non-excluded work stays unchanged.
- Handoff should render exclusions under `## Sync exclusions`, not under `## Dangerous skips`.

## Explicitly deferred

- Persistent `.harnessignore` / `.harness/harness.toml` ignore config.
- Full configurable review-source policy.
- Accepting implementation-agent self-review.
- Removing advanced commands.

## Open clarification resolved

The questionnaire showed `--exclude PATH --exclude PATH` as an example because repeated flags are how multiple paths are passed. The normal single-path command is:

```bash
hk sync --exclude .pi --reason 'Only local agent session state changed after validation.'
```
