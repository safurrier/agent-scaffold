# AGENTS.md relevance review

Reviewed against the local `ai-context-engineering-files` principles: stateless onboarding, less-is-more, WHY/WHAT/HOW, actor test, progressive disclosure, and high-stakes DO/NOT/BECAUSE gotchas.

## Current state

Root `AGENTS.md` is still relevant after this PR, but it is doing two jobs:

1. onboarding agents to work in this repo;
2. preserving product-direction guardrails discovered during the Harness Kit lifecycle PR.

The file is about 165 lines, which is slightly above the preferred 150-line target from the context-engineering skill but far below the hard-stop range. It is still navigable.

## Clearly still relevant

- Repo identity: `hk`/`harness-kit` vs `harness-scaffold`.
- Workflow commands: `mise run plan`, `mise run check`, `mise run sync-check`.
- `scripts/hk-dev` guidance for dogfooding this checkout without changing cwd.
- Task-contract gotchas around `.mise/tasks/*`, stack registry/template alignment, and slice workflow wrappers.
- HK product invariants that directly steer future agent edits:
  - shell-first evidence;
  - review must be independent/fresh-context;
  - dangerous skips stay explicit/scary;
  - sync exclusions must be explicit literal local paths;
  - generic artifact attach over pseudo-transcript prose;
  - public docs stay generic, not personal-dotfiles-specific.

## Relevant but candidates for progressive disclosure

These are useful, but root AGENTS may not need all of them long-term:

- detailed product-direction bullets about `context`, singular lifecycle commands, export terminology, and not treating HK as generic memory;
- version-transition framing notes now that public docs are versionless;
- review mechanism examples that could live in `docs/agent-adoption.md` or `docs/harness-kit-lifecycle-design.md` with a shorter root pointer.

## Suggested follow-up after merge

Do a cleanup pass that keeps root `AGENTS.md` as a routing/onboarding file and moves lower-level product rationale into docs:

- keep 5-8 high-stakes gotchas in root;
- move expanded HK product-direction rationale into `docs/harness-kit-lifecycle-design.md` or a new concise `docs/harness-kit-agent-guidance.md`;
- keep `scripts/hk-dev` and repo command guidance in root;
- retain the new personal-dotfiles guardrail in root because it is a direct correction to future agents working in this repo.

No urgent change needed for this PR. The current file is still useful and below the hard-stop size, but it is close to becoming a product-design memory dump rather than a pure onboarding router.
