# Review harness mechanism notes

Date: 2026-05-05

## Purpose

Quick confirmation of common harness-specific fresh-context review mechanisms so HK can stay harness-agnostic while giving agents enough examples to map `hk review prompt` to their environment.

## Findings

### Claude Code

Official Claude Code docs describe subagents as separate fresh-context agents. They are suitable for code review because the subagent has its own context window and returns a final response to the parent. Claude Code currently exposes the tool as `Agent`; older `Task(...)` references remain compatibility aliases after the rename in Claude Code v2.1.63.

Useful wording for HK docs:

```text
Claude Code: dispatch `hk review prompt` to an Agent/Task subagent, e.g. a code-reviewer subagent.
```

Sources:

- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/agent-sdk/subagents

### Codex CLI

Correction: Codex `/review` and `/agent` are CLI slash commands, not tools. Harness-facing instructions should not rely on them because an agent can call tools, not interactive TUI slash commands.

Tool-callable / command-callable options:

- Codex CLI has a non-interactive shell command: `codex review --uncommitted`. A dogfood run showed this installed Codex CLI rejects `codex review --uncommitted -` even though help mentions stdin prompts, so the default HK hint should use the working no-stdin form.
- Codex docs also describe subagent workflows and custom agents, but they do not expose a Claude-style one-off `Agent` tool name in the user-facing docs I found. Experimental batch subagent jobs use `spawn_agents_on_csv`, where each worker reports via `report_agent_job_result`; that is too specialized for the default HK review hint.

Useful wording for HK docs:

```text
Codex: use the Shell tool to run `codex review --uncommitted`, then record the accepted review with `hk review add`.
```

Sources:

- `codex review --help` and dogfood v7 against the local CLI.
- https://developers.openai.com/codex/cli/features
- https://developers.openai.com/codex/subagents

## Product decision

HK should not hard-code any harness. The CLI should define the review contract and provide examples:

```text
Review required by default.
Preferred: independent AI/tool reviewer.
Minimum fallback: fresh-context subagent.
Dispatch `hk review prompt` using your harness mechanism if available:
- Pi: reviewer subagent.
- Claude Code: Agent/Task subagent.
- Codex: Shell tool running `codex review --uncommitted`.
If unavailable, record `hk dangerously-skip review --reason ...`.
```

Actual persistent review backend configuration remains deferred.
