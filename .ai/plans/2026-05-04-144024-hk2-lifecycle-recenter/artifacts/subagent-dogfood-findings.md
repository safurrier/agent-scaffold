# HK 2.0 independent subagent dogfood findings

## Trial

A worker subagent was given a fresh synthetic repo at `/tmp/hk2-subagent-trial` and
a small product plan:

> implement `percent(part, whole)` in a tiny Python package, export it, add tests,
> and use HK 2.0 lifecycle commands.

The agent was instructed to use the local checkout executable:

```bash
uv --directory <REPO_ROOT> run hk
```

## Outcome

The agent completed the task and used the lifecycle:

```text
hk brief
hk start
hk context
hk plan
hk decide
hk validate --why ... -- uv run pytest -q
hk review add
hk sync
hk ready
hk handoff
hk export
```

Resulting code validation in the synthetic repo:

```bash
cd /tmp/hk2-subagent-trial
uv run pytest -q
```

Output:

```text
3 passed in 0.01s
```

HK readiness result reported by the agent:

```json
{"ready": true, "status": "ready"}
```

Generated handoff:

```text
/tmp/hk2-subagent-trial-handoff.md
```

## UX finding

The main issue was target resolution when using `uv --directory` to run HK from
the harness-toolkit checkout. Because `uv --directory ... run hk` changes the
process cwd to the harness-toolkit checkout, omitting `--target` makes HK act on
harness-toolkit instead of the shell's current synthetic repo.

The subagent noticed this and recorded it as context:

```text
UX finding: using uv --directory for the hk executable changes the process cwd,
so --target must be explicit or hk acts on harness-toolkit instead of the current
shell repo.
```

## Implication

This is mostly a dogfood invocation issue, not a core HK lifecycle failure. For
future dogfood and docs:

- use an installed `hk`/`hk2` binary when possible; or
- make every `uv --directory ... run hk` example include explicit `--target`.

## Product read

The lifecycle was understandable enough for a subagent to complete a small real
coding task without hand-holding. `hk ready` and generated handoff worked for the
simple repo. The most important improvement is documentation/help around target
selection when the executable is launched from a different directory.
