# Agent-Friendly CLI Audit

Applied `alex-ai-agent-friendly-cli` checklist to the Harness Kit CLI after the agent-adoption dogfood failure where Codex copied `--profile` onto `hk start`.

## Summary

Harness Kit is already mostly agent-friendly:

- non-interactive command surface;
- shell-first `hk validate -- <native command>` capture;
- broad `--json` support;
- progressive discovery through subcommand help;
- actionable readiness/status next actions;
- explicit dangerous skips instead of hidden prompts;
- profile/check commands show guidance without executing commands.

## Fixes made in this slice

- Added generated `hk instructions` guidance that profile flags are only for discovery commands (`hk profile`, `hk checks`, repo-scope `hk instructions`) and must not be copied to lifecycle commands.
- Added the same guidance to the repo-scope instructions snippet and public docs.
- Added a preflight error for accidental profile flags on lifecycle commands before Cyclopts emits a generic unknown-option error.
- Added examples to promoted/helpful subcommands that lacked them: `hk ready --help` and `hk review prompt --help`.

Example new error:

```text
Error: hk start does not use --profile. Profile flags are only for discovery commands such as `hk profile`, `hk checks`, and repo-scope `hk instructions`.
Try:
  hk profile resolve --target . --json
  hk checks --target . --json
  hk start --help
```

## Checklist

| Principle | Status | Notes |
|---|---:|---|
| Non-interactive by default | Good | No mandatory prompts found in promoted lifecycle. |
| Progressive discovery | Good | Root help lists commands; subcommand help is available. |
| Useful help with examples | Improved | Promoted commands mostly have examples; added missing examples for `ready` and `review prompt`. Some advanced commands could still get richer examples later. |
| Flags/stdin for inputs | Good | Text can be passed as args or `--from-file`; `context` supports stdin via `--from-file -`. |
| Actionable errors | Improved | Profile-flag misuse now gives direct repair steps. Existing local workflow errors avoid tracebacks. |
| Idempotency | Mixed/intentional | Most record/update commands append ledger events. `hk start` intentionally creates a new work item; agents should not retry it blindly. Could add future duplicate-work recovery guidance if retries become noisy. |
| Dry-run for destructive actions | Mostly OK | HK mostly records local evidence. `spec promote` requires `--dry-run`; dangerous skips are explicit/auditable rather than destructive. |
| `--yes`/`--force` bypass | N/A | No mandatory confirmations found. |
| Predictable structure | Good enough | Promoted lifecycle is verb-oriented (`start`, `validate`, `status`, `ready`, `handoff`); advanced noun groups (`profile`, `review`, `artifact`, `spec`) are consistent. |
| Data on success | Good | Commands return IDs, paths, statuses; most support `--json`. |
| Machine-readable output | Good | Most agent-facing commands support `--json`. |
| Non-zero failures | Good | Validation propagates native exit codes; readiness/check failures exit non-zero. |

## Remaining non-blocking gaps

1. **Root help is broad.** Advanced command groups are visible alongside promoted lifecycle commands. This is acceptable for now because `hk status` and docs promote the happy path, but a future `hk help lifecycle` or root-help grouping could reduce token load.
2. **`hk start` is not retry-idempotent.** This is product-intentional today, but if agents retry after timeouts it can create extra work items. A future `hk start --resume-if-active` or clearer active-work error could help.
3. **Advanced subcommand examples are uneven.** Promoted commands are covered; lower-level `spec`, `work`, and `evidence` commands could get more examples later if agents start using them directly.
4. **Cyclopts help epilogues render examples densely in captured text.** This is cosmetic but can be harder for agents to skim. If it becomes an issue, consider shorter examples or custom help formatting.
