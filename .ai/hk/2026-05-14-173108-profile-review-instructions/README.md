# HK export: `2026-05-14-173108-profile-review-instructions`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-05-14-173108-profile-review-instructions --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-05-14-173108-profile-review-instructions`
- Branch: `feat/profile-review-instructions`
- Git SHA: `5d2ab2e`
- Dirty: `true`
- Sync status: `synced`

## Context
- Profile reviews are named policies. Review instructions are inline or file-backed; applies_when suggests; required_when enforces; hk status surfaces optional suggestions. Skills/plugins remain wrapper instructions, not HK-loaded resources.

## Plan
- Simplify HK profile reviews around instruction-backed review policies: remove rubric from review UX/schema, replace prompt/prompt_file with typed review instructions, surface optional suggested checks/reviews in hk status, document skill-backed reviews, and update dots HK profile config after the HK PR is green.

## Decisions and spec reflection
- Break profile review compatibility by removing rubric and old prompt/prompt_file fields in favor of [reviews.instructions]. Keep old ledger rubrics readable but stop writing them.
  - Spec: updated: Spec/docs updated or verified.; refs: SPEC.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `bash -lc 'test -s /tmp/hk-dogfood-status.txt && test -s /tmp/hk-dogfood-prompt.txt && rg -q "optional profile suggestions" /tmp/hk-dogfood-status.txt && rg -q "Skill directory" /tmp/hk-dogfood-prompt.txt'`: pass (exit 0) — validates: Dogfood skill-backed suggested review flow: hk status surfaces optional review, review prompt embeds instructions, and review add works without rubric. — `<local HK state not exported>`
- `uv run pytest tests/unit/test_portable_workflow.py tests/unit/test_harness_kit_2.py tests/agent_sim/test_hk_agent_sim.py tests/e2e/test_hk2_cli_parity.py tests/unit/test_hk2_lifecycle_parity.py tests/unit/test_hk2_rendering_parity.py -q`: pass (exit 0) — validates: Focused HK regression suite passes for review instructions schema, status suggestions, review prompts, and review add without rubric. — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repo quality gate after profile review instructions changes. — `<local HK state not exported>`

## Readiness
- Status: `ready`
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: pass — external-enough review recorded
- sync: pass — sync checkpoint fresh

## Review
- pi-subagent / reviewer-fresh-context: Fresh-context lifecycle review found no blockers. Verified review instructions schema, removal of rubric from review UX, optional status suggestions, review prompt rendering, old ledger compatibility, docs, and tests. paths: .agent/skills/hk-pr-sized-dogfood/SKILL.md, README.md, SPEC.md, +30 more. [accepted]
- pi-subagent / agent-friendly-cli-fresh-context: Agent-friendly CLI review initially found removed --rubric lacked a repair hint and suggestion commands used ellipses. Fixed by adding a preflight migration error, copyable review add suggestions/readiness messages, and stable empty suggestion arrays; focused tests and full check passed. paths: .agent/skills/hk-pr-sized-dogfood/SKILL.md, README.md, SPEC.md, +30 more. [accepted]
