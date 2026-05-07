# Harness Kit Naming Brief

## Final direction

Use **Harness Engineering Toolkit** as the umbrella, **harness-kit** as the
portable toolkit name, **hk** as the daily CLI, and **harness-scaffold** as the
starter-template name.

## Product boundary

```text
Harness Engineering Toolkit
├── harness-kit / hk        # portable CLI/tooling layer for existing repos
└── harness-scaffold        # starter template for new projects
```

## Why this direction

- The project is about harness engineering: making agent work loops repeatable,
  inspectable, and handoff-safe across coding harnesses.
- `agent-harness` / `harness` is too ambiguous because Claude Code, Codex, Pi,
  Cursor, and similar tools are already harnesses.
- `harness-eng-toolkit` communicates the category but is too long as the command
  users type repeatedly.
- `hk` is short and memorable; `harness-kit` gives docs and packaging a readable
  long form.
- `harness-scaffold` fits the family and keeps the template/scaffold action
  explicit.

## Docs copy

> **Harness Engineering Toolkit** is a toolkit for making AI-agent engineering
> loops repeatable, inspectable, and handoff-safe across coding harnesses like
> Claude Code, Codex, Pi, and Cursor.
>
> Use **`hk`** when adding the workflow to an existing repo. Use
> **harness-scaffold** when starting a new repo with the workflow, task contract,
> docs, and CI already wired in.

## Command examples

```bash
hk instructions
hk profile list --target . --json
hk plan cache-bug --target . --profile python --json
hk status --target . --json
hk checks --target . --profile python --json
hk sync-check --target . --profile python --json
```

```bash
git clone https://github.com/safurrier/harness-toolkit.git my-project
cd my-project
mise run init -- --non-interactive --name my-project --shape single --stack python
```

## Implementation policy

The implementation uses a clean rename and does not register legacy
`agent-scaffold` or `agent-workflow` console scripts.
