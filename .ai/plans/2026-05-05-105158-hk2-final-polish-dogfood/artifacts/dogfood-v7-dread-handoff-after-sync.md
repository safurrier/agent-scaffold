# Handoff

## Summary
- Work: `2026-05-05-135903-dread-format-config`
- Branch: `hk2-dogfood-v7-dread`
- Git SHA: `6952b7a`
- Dirty: `true`
- Sync status: `synced`

## Context
- Relevant files: src/dread/formatting.py defines message_preview used by tab-separated CLI output in message list, mention list, and inbox recap. Existing tests do not cover formatting helper directly; add focused unit coverage.

## Plan
- Make a narrow message formatting or config behavior change with focused tests, then run HK validation and review lifecycle.

## Decisions and spec reflection
- Normalize Discord message previews for terminal tabular output by collapsing all whitespace runs to one space before truncation. This avoids embedded tabs/carriage returns/newlines breaking TSV-style CLI rows while preserving concise previews.
  - Spec: none: No spec impact declared.

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest tests/test_formatting.py -v`: pass (exit 0) — validates: Focused formatting helper tests cover whitespace normalization and truncation behavior. — `/private/tmp/hk2-pr-sized-trials-v7/dread/.harness-local/harness-kit/root/work/2026-05-05-135903-dread-format-config/artifacts/ev_20260505_135944_162995.transcript.log`
- `uv run ruff check src/dread/formatting.py tests/test_formatting.py`: pass (exit 0) — validates: Ruff lint ensures the formatting helper and new tests satisfy project style. — `/private/tmp/hk2-pr-sized-trials-v7/dread/.harness-local/harness-kit/root/work/2026-05-05-135903-dread-format-config/artifacts/ev_20260505_135957_044983.transcript.log`

## Readiness
- Status: `ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- sync: pass — sync checkpoint fresh

## Review
- codex / codex-review (core-quality): Codex review found formatting change and tests sound; it flagged untracked .pi/session.json as unrelated local artifact, which was removed before handoff. [accepted]

## Sync exclusions
- .pi: Codex/Pi review monitor state is agent-local and not part of the dread formatting change.
