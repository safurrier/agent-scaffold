# HK 2.0 lifecycle implementation plan

## Product target

HK 2.0 should be a cleaner, simpler HK 1.0 lifecycle backed by the current
ledger/capture foundation.

Canonical headline workflow:

```bash
hk start <slug>
hk context "..."
hk plan "..."
hk decide "..."
hk validate --why "..." -- <command>
hk review add --summary "..."
hk ready
hk handoff
```

Important nuance: the normal human/agent workflow often starts outside HK. The
human and agent discuss, design, and converge on an approach in chat/docs. HK is
where the agent distills the durable handoff state after that discussion:

```text
human/agent discussion → HK records → implementation → validation → review → ready → handoff
```

HK should not force the user to fill every blank. It should make it easy for the
agent to record the parts that prevent rediscovery and prove handoff readiness.

## Command semantics

### `hk start <slug>`

Purpose: create/select the active local work unit.

Behavior:

- Initializes local HK state if needed, or tells the user to run `hk init` only
  when explicit setup is required.
- Creates a ledger-backed work directory.
- Records target repo, branch, git SHA, and timestamp.
- Prints the next likely commands without pretending every command is required.

Open design question:

- Whether `hk start` should auto-init by default. Recommendation: yes for local
  state, because `hk start` is the first real workflow command; keep explicit
  `hk init` for configuration/adoption details.

Validation:

- Unit: starts cleanly in a temp git repo.
- Unit: repeated slug fails or resumes intentionally, not silently duplicates.
- Unit: JSON output includes active work ID/path/slug.
- Regression: existing `hk work start` either delegates to `hk start` or is
  marked advanced/legacy.

### `hk context "..."`

Purpose: capture useful context-engineering material for the next human/agent.

Definition:

- Stable framing.
- Constraints.
- Relevant files.
- Assumptions.
- Discovered repo facts.
- Prior decisions or gotchas that would otherwise be rediscovered.

Not intended for:

- Full transcripts.
- Boilerplate filler.
- Every obvious fact.
- A required template for tiny changes.

Initial shape:

```bash
hk context "This repo uses Cyclopts for agent-facing CLIs; do not add Click."
hk context "Relevant files: src/harness_toolkit/kit/local.py and tests/unit/test_harness_kit_2.py."
```

Future optional flags, only if useful:

```bash
hk context --file src/harness_toolkit/kit/local.py "Main local state implementation."
hk context --constraint "Preserve old hk plan/checks/sync-check until readiness parity."
hk context --assumption "No committed SPEC.md is required for arbitrary existing repos."
```

Readiness policy:

- HK itself should not try to infer whether context is required.
- `hk ready` should not fail merely because there is no context.
- Instead, docs/agent guidance should say: record context when it prevents
  rediscovery or explains why the plan is shaped this way.
- A future strict mode may allow `hk context --none "trivial typo fix"`, but do
  not build that until the need appears.

Validation:

- Unit: freeform context records render in handoff.
- Unit: empty context is rejected.
- Unit: optional category flags can be deferred; no schema over-design in slice 1.

### `hk plan "..."`

Purpose: record the agreed implementation intent after human/agent planning.

Behavior:

- Writes a plan lifecycle record.
- Supports `--from-file` for longer adopted plans.
- Handoff renders the plan near the top.
- Replaces the generic `hk note --kind plan` as the primary UX.

Validation:

- Unit: text and `--from-file` work.
- Unit: text plus `--from-file` fails clearly.
- Unit: `hk ready` fails without plan.

### `hk decide "..."`

Purpose: capture durable decision/spec reflection, replacing the useful part of
`DECISIONS.md` without forcing a multi-section file.

Mental model:

- This is not HK making a decision.
- This is the user/agent recording a decision already made during planning or
  implementation.
- It maps to ADR/decision-log/spec-reflection concepts.

Initial examples:

```bash
hk decide "Use lifecycle-first CLI over generic note-ledger UX." \
  --spec-impact "SPEC.md and docs/harness-kit-lifecycle-design.md updated."

hk decide "No product behavior change; internal refactor only." --no-spec-impact
```

Behavior:

- Writes a decision lifecycle record.
- Requires either `--spec-impact TEXT`, `--no-spec-impact`, or equivalent
  explicit reflection.
- Handoff renders decisions/spec impact.

Validation:

- Unit: decision with spec impact passes.
- Unit: decision with no-spec-impact passes.
- Unit: decision without spec reflection causes `hk ready` failure.

### `hk validate --why "..." -- <command>`

Purpose: primary validation/evidence command.

Behavior:

- Wraps current capture implementation.
- Runs the native command exactly as provided.
- Records command argv/display, cwd, branch/SHA, dirty state, timestamps,
  duration, exit code, transcript path, redaction metadata, and `why` rationale.
- Failed commands still produce evidence.
- In JSON mode, command stdout/stderr must not corrupt JSON stdout.

Examples:

```bash
hk validate --why "Focused regression coverage for lifecycle CLI." -- uv run pytest tests/unit/test_harness_kit_2.py -q
hk validate --why "Full repo gate before handoff." -- mise run check
```

Compatibility:

- Keep `hk capture` as a lower-level/advanced evidence primitive, but promote
  `validate` in docs and agent guidance.

Validation:

- Unit: validate records rationale.
- Unit: missing `--why` fails clearly.
- Unit: failed wrapped command returns non-zero while still recording evidence.
- Unit: `--json` stdout remains parseable.
- Unit: redaction behavior inherited from capture.

### `hk review add ...`

Purpose: record external-enough review evidence.

Accepted review sources for readiness:

- Codex/Claude/Gemini subagent review with named rubric.
- Manual human review note with reviewer identity.
- PR review from GitHub comments.

Not sufficient by itself:

- Automated lint/type/test only.
- Self-review, unless represented as an explicit waiver/gap and accepted by
  readiness policy.

Initial shape:

```bash
hk review add \
  --backend codex \
  --reviewer bug-hunter \
  --rubric correctness \
  --summary "No blocking findings." \
  --disposition accepted
```

Possible PR review import later:

```bash
hk review add --backend github-pr --reviewer alice --rubric human-review --summary "Approved in PR #12."
```

Validation:

- Unit: review record renders in handoff.
- Unit: missing reviewer/backend/rubric/summary fails.
- Unit: accepted backend values include manual_external, codex, claude, gemini,
  github-pr, and other explicit strings if documented.
- Unit: `hk ready` fails without review unless explicit waiver exists.

### `hk ready`

Purpose: binary handoff-readiness gate over explicit lifecycle records.

Default policy: strict, with explicit waivers/gaps for skipped lifecycle parts.

Checks:

- Active work exists.
- Plan exists.
- Decision/spec reflection exists.
- Validation evidence exists and each readiness-counting evidence item has a
  `why` rationale.
- External-enough review exists, or explicit waiver/gap exists.
- Sync checkpoint is fresh.
- Handoff can render.

Context handling:

- Do not require context globally.
- Do not infer context need from repo complexity.
- Surface guidance when no context exists: "No context records. This is okay for
  trivial work; add `hk context` if the next agent would need repo facts,
  constraints, assumptions, or relevant files."
- This guidance should be informational, not a failure, unless a future profile
  opts into stricter context requirements.

Output:

Human:

```text
not ready
- missing validation rationale: evidence 3
- missing external review record
- sync checkpoint stale: diff changed since last sync
```

JSON:

```json
{
  "ready": false,
  "checks": [
    {"id": "plan", "status": "pass"},
    {"id": "validation", "status": "fail", "message": "missing --why"}
  ]
}
```

Validation:

- Unit: all required records -> ready true and exit 0.
- Unit: missing plan -> ready false and non-zero.
- Unit: missing validation -> ready false and non-zero.
- Unit: validation without rationale -> ready false and non-zero.
- Unit: missing review -> ready false and non-zero.
- Unit: stale sync -> ready false and non-zero.
- Unit: no context -> warning/info, not failure by default.

### `hk handoff`

Purpose: render lifecycle-oriented handoff, not generic note dumps.

Sections:

1. Target and git state.
2. Context.
3. Plan.
4. Decisions/spec reflection.
5. Validation evidence.
6. Review.
7. Readiness/sync status.
8. Gaps/waivers/follow-ups.

Validation:

- Unit: handoff includes lifecycle sections in stable order.
- Unit: absence of optional context is represented cleanly.
- Unit: failed validation commands are clearly marked.
- Unit: review findings/disposition render.

## Profiles, dumb scripts, and validation guidance

HK 1.0's profiles/checks and the script-contract prototype still matter, but
they should sit beside the lifecycle rather than becoming the lifecycle.

### Dumb scripts

Dumb scripts are repo-owned stable command surfaces, such as:

```text
scripts/check
scripts/test
scripts/lint
mise run check
```

HK should not wrap these as `hk run check`. Instead, HK should help agents find
or document them, then capture them through validation evidence:

```bash
hk validate --why "Full repo quality gate." -- mise run check
hk validate --why "Script-contract smoke test." -- scripts/check
```

This preserves the shell-first rule: the command identity remains the repo's
native command.

### Profiles

Profiles are guidance/catalogs, not execution engines and not the same thing as
`.harness/harness.toml`.

- A profile is a named bundle of validation/workflow guidance: suggested native
  commands, expected evidence kinds, repo-shape notes, and handoff expectations.
- `.harness/harness.toml` is the optional committed repo adoption/config root:
  it can select defaults, policies, local profile locations, and future adopted
  workflow settings.
- Built-in/user profiles can work with no committed `.harness/` config.
- Repo-specific profiles may live under `.harness/profiles/` when a repo opts in.

Profiles can answer:

- What validation commands usually matter for this repo shape?
- What evidence kinds should a good handoff include?
- Which scripts or mise tasks are the stable entrypoints?
- What should an agent read before choosing commands?

They should not silently choose and run commands. A good flow is:

```bash
hk profile show python
hk validate --why "Focused unit coverage for changed CLI." -- uv run pytest tests/unit/test_harness_kit_2.py -q
hk validate --why "Full fast gate from repo contract." -- mise run check
```

A future `hk ready` may use profile guidance to explain missing evidence kinds,
but it should still check explicit evidence records, not infer quality.

### Checks

The old `hk checks` can remain until parity, but the 2.0 direction should avoid a
second promoted way to run validation. If retained, it should be a discovery or
suggestion surface, not a runner:

```bash
hk checks --profile python   # prints suggested native commands / evidence kinds
```

Then the agent runs the chosen native command with `hk validate`.

## Compatibility and deprecation stance

Preference: one obvious way to do each common task.

Keep only compatibility/advanced surfaces that serve a real purpose:

- `hk capture`: lower-level raw command evidence, because command capture itself
  is a valuable primitive.
- `hk status`: keep/promote; CLIs need status.
- `hk work materialize`: likely keep as secondary/export surface, but consider
  renaming to `hk export` later.
- Old `hk plan/checks/sync-check`: keep until `hk ready` reaches parity, then
  mark deprecated and remove as the last step.

Questionable:

- `hk note --kind ...`: useful for implementation/substrate testing, but may be
  too redundant for public UX. Recommendation: keep temporarily as advanced or
  hidden-ish, but do not promote in docs.
- `hk work start`: redundant with `hk start`; keep only as migration alias or
  remove before public 2.0 if feasible.

## Dogfood rollout

The implementation should dogfood HK 2.0 on real work before public cutover. The
minimum rollout is not just unit tests; it should prove the human/agent workflow:

```text
human/agent planning → hk context/plan/decide → implementation → hk validate → subagent review → hk ready → hk handoff/export
```

### Dogfood stage A — Current harness-toolkit branch

Use the lifecycle commands to implement the lifecycle commands.

Process:

1. Start a real HK work item for the lifecycle CLI implementation.
2. Record context only where it prevents rediscovery, e.g. command namespace
   conflicts, existing `hk plan` behavior, and old `sync-check` semantics.
3. Record the adopted implementation plan with `hk plan`.
4. Record design/spec decisions with `hk decide`.
5. Capture focused and full validation with `hk validate --why`.
6. Run external-enough subagent reviews and record them with `hk review add`.
7. Run `hk ready` and render `hk handoff` / `hk export`.
8. Compare the generated handoff against the current plan-artifact
   `mise run sync-check` output to find parity gaps.

Subagent review roles:

- **Diff reviewer**: does the implementation match the lifecycle design?
- **Bug hunter**: edge cases in JSON output, command parsing, failed evidence,
  sync freshness, and dangerous skips.
- **Convention reviewer**: CLI naming, Cyclopts style, repo docs, test style.
- **Readiness parity reviewer**: compare `hk ready` against old
  plan/spec/evidence/review expectations.

Exit criteria:

- Full lifecycle can be completed on harness-toolkit without editing plan files by
  hand except for current compatibility requirements.
- `hk ready` catches the same obvious missing handoff pieces as old
  `mise run sync-check` for this work.
- Handoff output is useful enough for a human reviewer to understand the work.

### Dogfood stage B — Independent subagent build trial

At the end of the lifecycle implementation, dispatch a small subagent team to use
HK 2.0 on a simple real coding task in a fresh/synthetic repo. This is the main
product dogfood test: give agents a basic plan, tell them to implement using HK
2.0, and observe whether the lifecycle works without hand-holding.

Trial shape:

1. Create a small repo, e.g. a Python CLI/library with a few tests and a simple
   native validation command.
2. Give the subagent team a basic product plan, not detailed HK instructions.
3. Tell them to use HK 2.0 for the work lifecycle:
   `hk start`, `hk context` when useful, `hk plan`, `hk decide`,
   `hk validate`, `hk review add`, `hk ready`, and `hk handoff/export`.
4. Let one or more agents implement the feature.
5. Use separate review agents to inspect both the code and the HK-produced
   records/handoff.
6. Record where agents got confused, skipped commands, over-produced context,
   failed readiness, or found the workflow helpful.

Scenarios:

- No `.harness/`, no `SPEC.md`, no existing HK state.
- Simple Python/uv project.
- Repo with dumb `scripts/check`.
- Optional module-like layout if cheap to fixture.

Exit criteria:

- Agents can complete a real small coding task using HK 2.0 without bespoke
  intervention from us.
- `hk brief` is read-only.
- `hk start` works without committed config.
- Lifecycle records remain local/ignored.
- `hk validate` records native command evidence.
- `hk ready` gives actionable failures and then passes after records are added.
- The generated handoff/export is good enough for a human to understand what was
  done, why, how it was validated, and what review happened.
- The trial produces a short UX findings report with concrete fixes before
  public cutover.

### Dogfood stage C — Adopted/configured repo fixture

After the profile/`.harness` design is revisited, add a fixture with committed
`.harness/harness.toml` and target/check definitions.

Exit criteria:

- `hk checks --target <target>` or equivalent shows configured native commands.
- `hk validate --target <target> --check <check>` only exists if command expansion
  is explicit and recorded.
- `hk ready --target <target>` uses target policy without becoming a task runner.

### Dogfood evidence requirements

For every lifecycle implementation slice, capture:

- focused unit test evidence;
- full `mise run check` evidence before handoff;
- subagent review record(s);
- `hk ready` output once available;
- generated `hk handoff` or `hk export` artifact once available.

If a lifecycle piece is not implemented yet, use the current plan-artifact
workflow to record the gap explicitly rather than pretending parity exists.

## Implementation slices

### Slice 0 — Reframe current PR before merge

Goal: update PR #12 so it is not landing a ledger-first product shape as the
public 2.0 UX.

Tasks:

- [ ] Update docs/ADR/SPEC to lifecycle-first language.
- [ ] Add or adjust tests to describe lifecycle target.
- [ ] Decide whether initial lifecycle aliases must exist before merge. Current
  product choice: yes, reshape PR #12 before merge.

Validation:

- `mise run check`
- `mise run sync-check -- --changed-plans main...HEAD`

### Slice 1 — Start/status and lifecycle record commands

Goal: add the low-risk lifecycle facade.

Tasks:

- [ ] Add `hk start <slug>`.
- [ ] Keep/promote `hk status` for active work overview.
- [ ] Add `hk context "..."` freeform.
- [ ] Add `hk plan "..."` and `hk plan --from-file`.
- [ ] Add `hk decide "..." --spec-impact/--no-spec-impact`.
- [ ] Render lifecycle records in handoff.
- [ ] Demote generic note docs.

Tests:

- Unit tests for each command's text/json output.
- Unit tests for invalid combinations and empty input.
- Snapshot-ish handoff tests for section ordering.

Validation:

- Focused: `uv run pytest tests/unit/test_harness_kit_2.py -q`
- Full: `mise run check`

### Slice 2 — Validate command

Goal: make evidence capture lifecycle-native.

Tasks:

- [ ] Add `hk validate --why ... -- <command>`.
- [ ] Store rationale in evidence schema.
- [ ] Update evidence list/handoff rendering.
- [ ] Keep `hk capture` as advanced compatibility.
- [ ] Update redaction tests to cover validate path.

Tests:

- Parseable JSON stdout.
- Failed command evidence.
- Missing `--why` failure.
- Split-arg secret redaction still applies.

Validation:

- Focused unit tests.
- Dogfood: `hk validate --why "focused lifecycle tests" -- uv run pytest tests/unit/test_harness_kit_2.py -q`

### Slice 3 — Review records

Goal: replace `REVIEW.md` with ledger-backed review records.

Tasks:

- [ ] Add `hk review add` subcommand.
- [ ] Store backend, reviewer, rubric(s), summary, findings, disposition.
- [ ] Render review section in handoff.
- [ ] Define external-enough review policy.

Tests:

- Required field validation.
- Multiple rubrics.
- Manual external review.
- Subagent review.
- PR review record.

Validation:

- Focused unit tests.
- Manual dogfood with a Codex review summary or manual_external review record.

### Slice 4 — Ready gate

Goal: close readiness parity enough that HK 2.0 can replace old sync-check for
local assistant work.

Tasks:

- [ ] Implement readiness check engine.
- [ ] Add `hk ready` human output.
- [ ] Add `hk ready --json` machine output.
- [ ] Integrate sync freshness.
- [ ] Add explicit waiver/gap path for skipped lifecycle parts.
- [ ] Keep context as informational by default.

Tests:

- Ready pass.
- Missing plan.
- Missing decision/spec reflection.
- Missing validation.
- Validation without rationale.
- Missing review.
- Stale sync.
- Handoff render failure.
- No context emits info/warning but does not fail.

Validation:

- Focused readiness tests.
- `mise run check`.
- Dogfood entire lifecycle on harness-toolkit branch.

### Slice 5 — Export and deprecation plan

Goal: make ledger state useful outside the local machine and plan removal of
legacy redundancy.

Decision: prefer `export` as the public verb. `materialize` describes the
implementation detail, not the user-facing job.

Tasks:

- [ ] Add `hk export` for handoff packages / generated files.
- [ ] Keep `hk work materialize` only as advanced/legacy alias if still needed.
- [ ] Add handoff package export if needed.
- [ ] Optionally export legacy plan-dir shape from ledger.
- [ ] Mark old `hk plan/checks/sync-check` as deprecated only after parity.
- [ ] Update profile-authoring / agent guidance docs.

Tests:

- Exported files are stable and reviewable.
- Legacy plan-dir export can pass current `sync-check`, if implemented.

Validation:

- `mise run sync-check` on exported/materialized plan if applicable.
- Full `mise run check`.

## Open questions to keep visible

1. Should `hk start` auto-init local state? Recommendation: yes.
2. Should `hk note --kind ...` remain public? Recommendation: advanced/temporary;
   do not promote.
3. Should `hk context --file/--constraint/--assumption` ship immediately?
   Recommendation: no; start freeform and add flags when proven useful.
4. What command should exist for skipped review/validation? Prefer intentionally
   scary language over bland waiver language. Candidates:
   `hk ready dangerously-skip review --reason "..."`,
   `hk yolo review --reason "..."`, or
   `hk gap "..." --dangerously-skips review`.
5. Should `hk work materialize` be renamed to `hk export`? Current answer: yes,
   prefer `export` as the product verb and keep materialize only as legacy or
   internal language.
6. How should profiles and dumb repo scripts fit? Current answer: they are
   guidance/stable command surfaces for `hk validate -- <native command>`, not a
   task-runner layer.
7. Revisit whether HK 2.0 should collapse profile functionality into
   `.harness/harness.toml` targets/checks/ready policy. Current working model is
   good enough for lifecycle implementation, but the simpler long-term model may
   be: `.harness` is the durable config system, while profiles are only reusable
   presets/checksets or migration compatibility.
