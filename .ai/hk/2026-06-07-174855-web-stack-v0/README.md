# HK export: `2026-06-07-174855-web-stack-v0`

This directory is a generated review/handoff package from the Harness Kit ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, `hk validate`, `hk review add`, and `hk sync`, then regenerate.

## Freshness
Validate this export against local HK state with:

```bash
hk export --format handoff-dir --output .ai/hk/2026-06-07-174855-web-stack-v0 --target . --check
```

Historical hand-authored slice plans live under `.ai/plans/`; new Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.

## Handoff

## Summary
- Work: `2026-06-07-174855-web-stack-v0`
- Branch: `feat/web-stack-v0`

## Context
- Implement web as the first real adapter: Vite React TypeScript on Cloudflare Workers/Static Assets with D1/auth-ready generated schema. Keep Vercel/Postgres/R2 as docs/ADR extension points, not generated fake code. Follow docs taxonomy under docs/reference, docs/how-to, docs/explanation; stack must satisfy docs/reference/stacks/acceptance-rubric.md before fully supported.

## Plan
- Add a supported web stack for Vite React Cloudflare Worker apps with D1/auth-ready scaffold and NBA simulator dogfood path. Keep Cloudflare+D1 as the first real adapter; document Vercel/Postgres/R2 as planned extension points until validated by a second app.

## Decisions and spec reflection
- Web stack V0 will ship Cloudflare+D1 as the concrete supported path; Vercel/Postgres/R2 remain planned extension points until a second validated adapter exists.
  - Spec: updated: Spec/docs updated or verified.; refs: docs/reference/decisions/0013-web-stack.md

## Learning
- None recorded.

## Gaps
- None recorded.

## Validation evidence
- `uv run pytest -m contract`: pass (exit 0) — validates: Docs, task files, CI matrix, and stack reference contract after adding web stack — `<local HK state not exported>`
- `bash -lc 'tmp=$(mktemp -d) && cp -R . "$tmp/harness-toolkit" && cd "$tmp/harness-toolkit" && mise run init -- --non-interactive --name smokeweb --shape single --stack web --no-hooks && mise trust .mise.toml && mise run setup && mise run check'`: fail (exit 1) — attempted to validate: Generated web stack initializes, installs dependencies, and passes its check task in a throwaway copy — `<local HK state not exported>`
- `bash -lc 'tmp=$(mktemp -d) && cp -R . "$tmp/harness-toolkit" && cd "$tmp/harness-toolkit" && mise trust .mise.toml && mise run init -- --non-interactive --name smokeweb --shape single --stack web --no-hooks && mise trust .mise.toml && mise run setup && mise run check'`: pass (exit 0) — validates: Generated web stack initializes, installs dependencies, and passes its check task in a throwaway copy — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repository fast gate after web stack implementation, docs, and tests — `<local HK state not exported>`
- `mise run sync-check`: pass (exit 0) — validates: Repository handoff/sync contract after CI workflow and scaffold changes — `<local HK state not exported>`
- `mise run verify`: pass (exit 0) — validates: Heavy validation after adding a supported stack and verify-task behavior — `<local HK state not exported>`
- `uv run pytest tests/unit/stacks/test_web.py -q`: pass (exit 0) — validates: WebStack no-examples regression fix keeps generated App.tsx valid after removing ExamplePanel — `<local HK state not exported>`
- `bash -lc 'tmp=$(mktemp -d) && cp -R . "$tmp/harness-toolkit" && cd "$tmp/harness-toolkit" && mise trust .mise.toml && mise run init -- --non-interactive --name smokeweb --shape single --stack web --no-hooks --no-examples && mise trust .mise.toml && mise run setup && mise run check'`: pass (exit 0) — validates: Generated web stack passes check after no-examples removes ExamplePanel and rewrites App.tsx — `<local HK state not exported>`
- `mise run check`: fail (exit 1) — attempted to validate: Full repository fast gate after no-examples web polish fix — `<local HK state not exported>`
- `mise run check`: pass (exit 0) — validates: Full repository fast gate after no-examples web polish fix and typed unit test — `<local HK state not exported>`
- `uv run pytest tests/unit/stacks/test_web.py tests/e2e/test_web.py -q`: pass (exit 0) — validates: Codex review fixes: web stack scaffold cleanup and saved-run auth guard — `<local HK state not exported>`
- `uv run pytest tests/contract/test_docs_contract.py -q`: pass (exit 0) — validates: Docs summary for web scaffold template passes docs contract tests — `<local HK state not exported>`

## Readiness
- context: info — context recorded
- plan: pass — plan recorded
- decision: pass — decision and spec reflection recorded
- validation: pass — validation evidence with rationale recorded
- review: fail — missing accepted external-enough review record; dispatch a separate reviewer/subagent with fresh context via your harness, then record it with hk review add
- profile-check:focused-contract-tests: fail — required profile check `focused-contract-tests` does not cover current changed paths (matched docs/reference/stacks/index.md, docs/reference/stacks/web-template-summary.md); rerun the matching native command from `hk checks --changed`, record it with `hk validate --check focused-contract-tests --why '...' -- <command>`, or `hk dangerously-skip validation --label focused-contract-tests --reason ... --mitigation ...`
- profile-check:fast-gate: fail — required profile check `fast-gate` does not cover current changed paths (matched docs/reference/stacks/index.md, src/harness_toolkit/scaffold/stacks/web.py, stacks/web/project/tests/worker.test.ts, +3 more); rerun the matching native command from `hk checks --changed`, record it with `hk validate --check fast-gate --why '...' -- <command>`, or `hk dangerously-skip validation --label fast-gate --reason ... --mitigation ...`
- profile-check:handoff-sync-check: pass — required profile check recorded: handoff-sync-check (matched .github/workflows/ci.yml)
- profile-check:heavy-gate: pass — required profile check recorded: heavy-gate (matched .github/workflows/ci.yml, .mise/tasks/verify)
- profile-check:generated-stack-smoke: fail — required profile check `generated-stack-smoke` does not cover current changed paths (matched src/harness_toolkit/scaffold/stacks/web.py, stacks/web/project/tests/worker.test.ts, stacks/web/project/worker/routes/runs.ts); rerun the matching native command from `hk checks --changed`, record it with `hk validate --check generated-stack-smoke --why '...' -- <command>`, or `hk dangerously-skip validation --label generated-stack-smoke --reason ... --mitigation ...`
- profile-review:codex-review: fail — missing required profile review `codex-review` (matched .github/workflows/ci.yml, .mise/tasks/build, .mise/tasks/dev, +52 more); run `hk review prompt codex-review` and record with `hk review add --review codex-review --backend subagent --reviewer reviewer-fresh-context --summary '...'`, or `hk dangerously-skip review --label codex-review --reason ... --mitigation ...`

## Review
- None recorded.

## Dangerous skips
- review: codex-review — reason: codex review --uncommitted failed: default gpt-5.5 requires newer CLI; explicit gpt-5 and gpt-5-mini are unsupported for this ChatGPT account; subagent fallback is not permitted without explicit user delegation request in this session; mitigation: Recorded focused contract tests, generated web stack smoke, full fast gate, sync-check, and heavy gate through HK; performed local architecture-polish/self-review before handoff
- review: codex-review — reason: codex review --uncommitted failed: default gpt-5.5 requires newer CLI; explicit gpt-5 and gpt-5-mini are unsupported for this ChatGPT account; subagent fallback is not permitted without explicit user delegation request in this session; mitigation: Fresh HK validation covers contract tests, generated web smoke including --no-examples, full fast gate, sync-check, and heavy gate; local architecture-polish pass fixed the no-examples regression
