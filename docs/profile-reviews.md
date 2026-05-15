---
id: profile-reviews
title: Profile Reviews
description: >
  How Harness Kit profiles define named review policies, including suggested
  and required reviews plus skill-backed review instructions.
index:
  - id: overview
    keywords: [hk, reviews, profiles, instructions, skills]
  - id: suggested-required
    keywords: [applies_when, required_when, status, readiness]
  - id: skill-backed
    keywords: [skill, prompt, instructions, fresh-context]
---

# Profile Reviews

Profile reviews are named review policies in an HK profile. HK renders a review
prompt and records external-enough review evidence; it does not run the reviewer
or load skills/plugins itself.

Use profile reviews when a repo has repeatable review guidance such as:

- a final architecture/reviewability pass before PR;
- a required safety review for lifecycle, sync, profile, or export changes;
- a Codex or fresh-context review prompt for agent-facing CLI changes;
- a back-pocket review skill the agent can invoke by name.

## Schema

```toml
[[reviews]]
name = "architecture-polish-review"
purpose = "Suggested final A/A+ architecture and reviewability pass for PR-sized work."
backend = "subagent"
dispatch_hint = "Run after validation before considering implementation complete. Use a fresh-context subagent. Do not self-review."
applies_when = ["src/**", "templates/**", "SPEC.md"]
required_when = []

[reviews.instructions]
type = "file"
path = "../review-prompts/architecture-polish-review.md"
```

Fields:

| Field | Meaning |
|---|---|
| `name` | Stable HK handle used by `hk review prompt NAME` and `hk review add --review NAME`. |
| `purpose` | Short explanation of why the review exists. |
| `backend` | Expected dispatch mechanism, such as `subagent`, `codex-cli`, or `fresh-context-subagent`. |
| `dispatch_hint` | Short operational guidance for the implementation agent: when/how to run it. |
| `[reviews.instructions]` | Optional inline or file-backed reviewer instructions rendered into `hk review prompt`. |
| `applies_when` | Changed-path patterns that make the review show as a non-blocking suggestion. |
| `required_when` | Changed-path patterns that make the review readiness-blocking. |

Instruction forms:

```toml
[reviews.instructions]
type = "inline"
text = "Review the CLI UX against the agent-friendly CLI checklist."
```

```toml
[reviews.instructions]
type = "file"
path = "../review-prompts/agent-friendly-cli-review.md"
```

File paths are resolved relative to the profile TOML file, with `~` and
environment variables expanded. HK reads the file and embeds the contents in the
rendered review prompt so the fresh reviewer receives a self-contained packet.

## Suggested vs required

A review can be available, suggested, or required.

### Back-pocket review

Define the review without `applies_when` or `required_when`:

```toml
[[reviews]]
name = "architecture-polish-review"
purpose = "Manual architecture polish review."
backend = "subagent"
dispatch_hint = "Use when the user asks for final architecture polish."

[reviews.instructions]
type = "file"
path = "../review-prompts/architecture-polish-review.md"
```

The agent can still run:

```bash
hk review prompt architecture-polish-review --target .
```

### Suggested review

Use `applies_when` when the review should appear in `hk checks --changed` and
`hk status` but should not block readiness:

```toml
applies_when = ["src/harness_toolkit/kit/**", "docs/**"]
required_when = []
```

`hk status` renders matching suggestions under `optional profile suggestions` with
commands to run. These suggestions are not readiness blockers.

### Required review

Use `required_when` when readiness must block until the review is recorded or
explicitly skipped:

```toml
required_when = [
  "src/harness_toolkit/kit/readiness/**",
  "src/harness_toolkit/kit/sync/**",
  "src/harness_toolkit/kit/handoff/**",
]
```

Then `hk status` / `hk ready` report the missing profile review until the agent
records:

```bash
hk review add --review readiness-safety-review \
  --backend subagent \
  --reviewer reviewer-fresh-context \
  --summary "No blockers."
```

If the review is genuinely impossible, use a scary explicit skip with a matching
label:

```bash
hk dangerously-skip review \
  --label readiness-safety-review \
  --reason "review tool unavailable" \
  --mitigation "rerun before merge"
```

## Skill-backed reviews

HK does not load skills or plugin directories. Use an instruction file as a
wrapper that tells the reviewer what to load and how to apply it.

Example wrapper:

```md
# Architecture polish review

Load and follow the architecture-polish-review skill.

Skill directory:
`~/git_repositories/dots/config/ai-config/plugins/alex-ai/skills/architecture-polish-review`

Run this after:
- implementation is functionally working;
- focused validation evidence exists;
- the implementation agent believes the work is near handoff.

Do not answer as the implementation agent. Dispatch this to a fresh-context reviewer.

Return:
- current grade;
- P0/P1 blockers;
- P2/P3 improvements;
- recommended fix order;
- verification plan;
- re-grade criteria.
```

The profile stays simple:

```toml
[[reviews]]
name = "architecture-polish-review"
purpose = "Suggested final architecture/reviewability pass before PR."
backend = "subagent"
dispatch_hint = "Run after validation before considering implementation complete. Use a fresh-context subagent. Do not self-review."
applies_when = ["src/**", "templates/**", "SPEC.md"]
required_when = []

[reviews.instructions]
type = "file"
path = "../review-prompts/architecture-polish-review.md"
```

The agent flow is:

```bash
hk status --target .
hk review prompt architecture-polish-review --target .
# dispatch the prompt to the fresh reviewer
# fix high-signal findings
hk review add --review architecture-polish-review \
  --backend subagent \
  --reviewer reviewer-fresh-context \
  --summary "Accepted after architecture polish."
hk status --target .
```

## Targeted follow-up

HK records path/content coverage for profile reviews. After small follow-up edits,
record targeted review coverage instead of rerunning a broad review:

```bash
hk review add --review architecture-polish-review \
  --path src/harness_toolkit/kit/cli.py \
  --backend subagent \
  --reviewer reviewer-fresh-context \
  --summary "Targeted follow-up accepted."
```
