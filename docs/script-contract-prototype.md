---
id: script-contract-prototype
title: Canonical Scripts Contract Prototype
description: >
  Prototype direction for replacing or complementing the generated mise task
  contract with thin native-tool script adapters.
index:
  - id: contract
    keywords: [scripts, check, verify, ci, task-contract]
  - id: examples
    keywords: [python, rust, web, native-tools]
---

# Canonical Scripts Contract Prototype

## Status

Prototype design for a later Harness Kit scaffold rollout phase.

This document does not replace the current generated mise task contract yet. It
captures the proposed adapter shape and the validation bar for deciding whether
it is better than keeping mise as the canonical scaffold surface.

## Thesis

Canonical scripts should be boring adapter entrypoints, not a task runner.

They should give humans, agents, CI, mise, just, make, and package-manager
scripts one stable set of commands without making `hk` execute validation.

## Contract

A scaffolded repo may expose:

```text
scripts/setup
scripts/fmt
scripts/lint
scripts/typecheck
scripts/test
scripts/build
scripts/check
scripts/verify
scripts/sync
```

Rules:

- every script is executable;
- every script is non-interactive;
- every script exits nonzero on failure;
- scripts delegate to native tools;
- scripts avoid flags/subcommands except where stack-native tools require them;
- CI may call scripts directly;
- mise/just/npm/make may delegate to scripts;
- `hk` does not become a task runner for these commands.

## Python example

```bash
# scripts/check
#!/usr/bin/env bash
set -euo pipefail

scripts/lint
scripts/typecheck
scripts/test
```

```bash
# scripts/lint
#!/usr/bin/env bash
set -euo pipefail

uv run ruff format --check .
uv run ruff check .
```

```bash
# scripts/typecheck
#!/usr/bin/env bash
set -euo pipefail

uv run ty check
```

```bash
# scripts/test
#!/usr/bin/env bash
set -euo pipefail

uv run pytest -m "not slow"
```

## Rust example

```bash
# scripts/check
#!/usr/bin/env bash
set -euo pipefail

scripts/fmt
scripts/lint
scripts/typecheck
scripts/test
```

```bash
# scripts/fmt
#!/usr/bin/env bash
set -euo pipefail

cargo fmt --check
```

```bash
# scripts/lint
#!/usr/bin/env bash
set -euo pipefail

cargo clippy --all-targets --all-features -- -D warnings
```

```bash
# scripts/typecheck
#!/usr/bin/env bash
set -euo pipefail

cargo check --all-targets --all-features
```

```bash
# scripts/test
#!/usr/bin/env bash
set -euo pipefail

cargo test --all-features
```

## Web/TypeScript example

```bash
# scripts/check
#!/usr/bin/env bash
set -euo pipefail

pnpm run fmt:check
pnpm run lint
pnpm run typecheck
pnpm run test
pnpm run build
```

```json
{
  "scripts": {
    "fmt": "prettier --write .",
    "fmt:check": "prettier --check .",
    "lint": "eslint .",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "build": "tsc --noEmit && vite build",
    "check": "scripts/check",
    "verify": "scripts/verify"
  }
}
```

## Validation questions

Before replacing the current mise-first scaffold contract, validate:

1. Is the scripts contract easier for agents to discover and run?
2. Does it reduce dependencies without recreating a worse task runner?
3. Can CI call the same commands as local usage?
4. Can mise aliases delegate cleanly for users who like mise?
5. Are Python, Go, Rust, and Web examples equally understandable?
6. Does the generated repo still pass a golden-path check out of the box?

## Recommendation

Prototype scripts in generated fixture repos first. If the examples stay thin and
pleasant, make scripts canonical and keep mise aliases optional. If the scripts
start growing flags, dispatch logic, or hidden state, keep mise as the scaffold
contract and treat scripts as optional aliases only.
