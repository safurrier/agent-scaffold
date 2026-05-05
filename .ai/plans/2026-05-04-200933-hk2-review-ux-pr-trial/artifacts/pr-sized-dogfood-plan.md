# PR-sized HK 2.0 dogfood trial plan

## Goal

Run a more realistic HK 2.0 trial than tiny/toy changes by replaying an actual
recent PR-sized change in a temporary clone. The agent should receive a good
implementation directive, not a vague product prompt, so the study measures HK's
ability to support real execution, evidence, review, readiness, and handoff.

## Candidate repos

- Discord / Discord AI shaped scoped checkout, if available and safe.
- Foreman, using a recent merged PR that is larger than a test-only tweak.
- Dread, using a recent merged PR that touches CLI behavior, tests, and docs.

## Setup method

1. Pick a recent merged PR with a clear before/after and manageable local
   validation.
2. Clone to a temp directory, never operate on the original repo.
3. Checkout the parent commit immediately before the PR landed.
4. Create a new trial branch.
5. Remove or hide forward history/reference material enough that the worker
   cannot simply inspect the later commit. Practical options:
   - clone/fetch only up to the parent commit when possible;
   - create a detached worktree at the parent commit and do not provide PR diff
     paths;
   - give the worker a directive/spec generated from the PR outcome, not the git
     diff itself.
6. Ask a subagent to implement the directive using HK 2.0 lifecycle commands with
   `--target` pointed at the temp clone.
7. Require the worker to run native validation appropriate for the repo and record
   it with `hk validate --why`.
8. Require a fresh-context review subagent or external tool review; do not accept
   same-agent self-review.
9. Collect HK handoff, ledger, command transcripts, git diff, and worker notes.

## What to measure

- Did the agent use context only when useful, or create filler?
- Did the plan/decision/spec reflection capture the real directive concisely?
- Did validation evidence explain what the commands proved?
- Did review come from a genuinely separate/fresh context?
- Did `ready` fail usefully when something was missing?
- Did handoff explain enough for a human reviewer?
- Did HK remain shell-first rather than becoming a task runner?
- Did target handling, sync freshness, and handoff readiness stay clear?

## Output artifacts

- `/tmp/hk2-pr-sized-trials/<repo>-handoff.md`
- `/tmp/hk2-pr-sized-trials/<repo>-worker-report.md`
- `/tmp/hk2-pr-sized-trials/<repo>-diff.patch`
- A synthesis report committed under the active plan's `artifacts/` directory.
