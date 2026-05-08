# HK 2.0 real-repo dogfood study

## Scope

Ran HK 2.0 lifecycle dogfood trials in temporary clones of real repos:

- `/tmp/hk2-real-trials/dread` cloned from `~/git_repositories/dread`
- `/tmp/hk2-real-trials/foreman` cloned from `~/git_repositories/foreman`

Original repos were not modified. Trial branches were created in temp clones only.

## Trial A — Dread Python CLI

Task chosen by worker: improve pure CLI formatting behavior and tests.

Changed in temp clone:

- `src/dread/formatting.py`
- `tests/test_formatting.py`
- `tests/test_config_favorites.py`

Validation:

```bash
uv run pytest tests/test_formatting.py -q
# 3 passed in 0.01s

uv run ruff check src/ tests/ && uv run ty check && uv run pytest tests/ --ignore=tests/e2e -q
# 168 passed, 1 warning in 1.84s
```

HK result:

```json
{"ready": true, "status": "ready"}
```

Handoff:

```text
/tmp/hk2-real-trials/dread-handoff.md
```

Notable findings:

- HK lifecycle worked on a real Python CLI repo.
- `hk validate --why` was the strongest piece; it captured focused and full
  validation loops with rationale and transcripts.
- The temp clone needed setup (`uv sync --extra dev`) before full validation.
- Freeform context text was shell-fragile: a double-quoted note containing
  backticks triggered shell command substitution before HK saw the text.
- The worker recorded a self-review-ish `manual_external` review; this showed the
  need to tighten review readiness semantics.

Fixes made from this trial:

- Added `hk context --from-file PATH|-` to avoid shell-fragile rich text.
- Updated examples/snippets to prefer single-quoted note text.
- Tightened accepted review readiness to reject obvious self-review reviewer
  tokens.
- Added readiness to handoff output so handoffs show the gate result.

## Trial B — Foreman Rust CLI

Task chosen by worker: add focused assertions to an existing CLI help test.

Changed in temp clone:

- `tests/cli_config.rs`

Validation:

```bash
cargo test help_surfaces_setup_first_run_flow --test cli_config
# 1 passed; 15 filtered out

cargo fmt --check
# pass
```

HK result:

```json
{"ready": true, "status": "ready"}
```

Handoff:

```text
/tmp/hk2-real-trials/foreman-handoff.md
```

Notable findings:

- HK lifecycle worked on a real Rust CLI repo with focused validation.
- The worker respected repo guidance to avoid heavy native E2Es for a small help
  test change.
- The lifecycle felt somewhat ceremonial for a tiny test-only change, especially
  `decide --no-spec-impact` duplicating the decision text.
- `hk handoff` previously did not include readiness output, making the handoff
  less self-validating.
- Top-level `hk dangerously-skip` works but remains a naming follow-up versus the
  desired `hk ready dangerously-skip` phrasing.

Fixes made from this trial:

- `hk decide --no-spec-impact` now records concise `No spec impact declared.`
  rather than duplicating the decision text.
- Handoff rendering now includes a `## Readiness` section with check statuses.
- `hk handoff`/`hk export` no longer append generated-view events by default,
  reducing retry noise in the ledger.

## Cross-trial findings

### What worked

- Agents used the lifecycle commands without bespoke hand-holding when given a
  real task and explicit `--target`.
- `hk validate --why` consistently produced useful evidence.
- `hk ready` provided a clear completion gate.
- Local state stayed out of committed repo files.
- Real repo guidance in `AGENTS.md` remained important for choosing validation.

### Sharp edges found

1. **Target handling with `uv --directory`**
   - When HK is invoked through `uv --directory <harness-toolkit> run hk`, the
     process cwd is harness-toolkit. Dogfood instructions must pass `--target` or
     use an installed binary.

2. **Shell-fragile text input**
   - Backticks and shell metacharacters in double-quoted note/context text can be
     evaluated by the shell before HK sees them.
   - Fixed for context with `--from-file PATH|-`; examples now prefer single
     quotes.

3. **Self-review ambiguity**
   - Workers often used `manual_external` with self-review-ish identities.
   - Readiness now rejects obvious self-review reviewer tokens; docs/help should
     continue to say use a separate reviewer/subagent or dangerous skip.

4. **Handoff did not show readiness**
   - Fixed by adding readiness checks to handoff output.

5. **Generated event noise**
   - Re-running handoff/export appended low-value generated events.
   - Fixed by making handoff/export rendering not append generated events by
     default.

6. **Ceremony for tiny changes**
   - Context and decide are useful, but agents may fill them with boilerplate for
     trivial changes. Future docs should explicitly say to skip context when it
     does not prevent rediscovery and use concise no-spec-impact decisions.

## Remaining follow-ups

- Consider moving dangerous skip under `hk ready dangerously-skip` or document the
  top-level command clearly.
- Consider `hk finish` or `hk close` to run sync/ready/handoff in one
  agent-friendly sequence.
- Consider correction/supersede events for bad notes so rendered handoffs can hide
  superseded context while preserving audit history.
- Consider warning when `hk handoff --write` points inside the target repo.
- Revisit profile/`.harness` design for setup/check discovery after lifecycle UX
  stabilizes.
