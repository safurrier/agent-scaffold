

agent-scaffold — Specification







Description





agent-scaffold is an opinionated starter repository for agent-driven engineering. It provides a stable task contract (fmt, lint, typecheck, test, check, verify, etc.) implemented via mise, plus repeatable conventions around structure, tooling, and CI so AI-native codebases are deterministic, reproducible, and easy to validate.



Reference templates (existing):



- Python: https://github.com/safurrier/python-collab-template
- Go: https://github.com/safurrier/go-template-project





These repos define the baseline “batteries included” expectations (interactive init, quality gates, pre-commit, CI, docs/docker patterns).









1. Goals







1.1 Primary Goals





- Provide a stable, minimal command surface for humans and agents.
- Preserve capabilities present in the reference repos (not necessarily 1:1 command names).
- Support two repo shapes out-of-the-box:


- Single-project (one language, conventional layout like src/, tests/)
- Apps workspace (“v2”) suitable for multi-app repos (apps/…) without forcing polyglot

-

- Keep orchestration thin: delegate to language-native tools.
- Make CI call the same entrypoints as local usage.







1.2 Non-Goals (v1)





- No Bazel/Buck2.
- No implicit auto-discovery of “apps” based solely on folder existence; configuration must be explicit once initialized.
- No mandatory spec folder layout.











2. Core Principles







2.1 Unified Task Contract





Every agent-scaffold repo MUST expose the following tasks at repository root (via mise):



- init
- setup
- fmt
- lint
- typecheck
- test
- build
- check
- dev
- ci
- verify







2.2 Thin Orchestration





The contract stays stable; implementations call native tools.



Examples:

|   |   |   |   |   |
|---|---|---|---|---|
|Stack|fmt|lint|typecheck|test|
|Python|ruff format|ruff check|ty|pytest|
|Go|gofumpt/gofmt|golangci-lint|(alias/test-based)|go test|
|Rust|cargo fmt|cargo clippy|cargo check|cargo test|
|Web (TS)|prettier|eslint|tsc –noEmit|vitest/jest|



2.3 Fast 

check

, Explicit 

verify





- check MUST be deterministic, non-interactive, and fast.
- verify is allowed to be heavier (integration/e2e/docker/security/docs).







2.4 Deterministic CI





GitHub Actions MUST call exactly one entrypoint:

mise run ci

Initially, ci aliases check (may expand later, but remains a single entrypoint).









3. Repo Shapes: Single-Project vs Apps Workspace (“v2”)





agent-scaffold supports two repo shapes. The shape is selected at init time.





3.1 Single-Project Shape





For a single language / single deliverable.



Recommended structure:

src/            (or language-idiomatic equivalent)

tests/

scripts/

docs/           (optional)

docker/         (optional)

.github/

.mise.toml

Notes:



- Python prefers src/ + tests/.
- Go and Rust may be root-based (cmd/, internal/, pkg/ or src/), but the template should still provide a predictable convention.







3.2 Apps Workspace Shape (“v2”)





For repos that may contain multiple apps (one language or many), plus shared packages.



Recommended structure:

apps/

  <app-1>/

  <app-2>/

packages/        (optional shared libs)

infra/           (optional: compose/terraform/etc.)

scripts/

docs/            (optional)

.github/

workspace.toml   (or workspace.yml)   <-- explicit module registry

.mise.toml

Key requirement: explicit module registry (e.g., workspace.toml) listing which modules exist and their type. This avoids “magic” execution based on mere folder presence.



Example minimum manifest fields per module:



- path (e.g., apps/api-go)
- kind (python|go|rust|web)
- role (app|package)
- optional dev command selector (for dev task)
- optional verify selector (for integration tests)











4. init







4.1 Purpose





Initialize a fresh clone of agent-scaffold into a project-specific repo.





4.2 Required Modes





init MUST support:



- Interactive mode (default)
- Non-interactive mode (flags)





Examples:

mise run init

mise run init -- --non-interactive --name myproj --shape apps --stacks go,web



4.3 Responsibilities





- Select repo shape: single or apps
- Select stack(s): python, go, rust, web (subset depending on desired project)
- Write configuration:


- for apps shape: generate workspace.toml module registry
- for single shape: configure conventional layout and tooling

-

- Apply project metadata:


- name, description, license, authorship (where applicable)
- package/module identifiers (Python package name, Go module path, Cargo crate name, npm package name)

-

- Remove or keep example code
- Initialize git (if needed)
- Install pre-commit hooks (if enabled)
- Ensure mise run check passes on a fresh init (golden path)





Non-interactive mode MUST:



- require explicit values for required fields
- fail fast with clear error messages if inputs are missing
- produce deterministic outputs











5. setup







5.1 Purpose





Install dependencies and prepare the environment.





5.2 Behavior by Repo Shape







Single-project





Runs the stack-appropriate install (e.g., uv sync, go mod download, cargo fetch, pnpm install).





Apps workspace





Iterates modules listed in workspace.toml and runs per-module setup in that module’s working directory.



Constraints:



- setup must be non-interactive
- Must be safe to re-run











6. Task Definitions







6.1 fmt





Applies formatting across the configured scope:



- single: project root
- apps: per manifest module







6.2 lint





Runs non-modifying lint checks.





6.3 typecheck





Runs static type analysis.

Rules:



- Go may implement as alias to compile/test-based check (documented).
- JS-only repos may implement as no-op or lint-only; TS uses tsc --noEmit.







6.4 test





Runs unit tests only (fast path).





6.5 build





Produces artifacts appropriate for the stack and shape:



- single: one artifact
- apps: per-app artifacts (not necessarily building packages unless required)





Must not deploy.





6.6 check





Runs:



- formatting in check mode
- lint
- typecheck
- unit tests





Must be deterministic and fast. No integration dependencies by default.





6.7 dev





Starts local development.



- single: start the app (or no-op if library)
- apps: start one or more modules marked “dev=true” (or require a --module flag)





May start infra dependencies (compose) if explicitly configured.





6.8 ci





Default CI entrypoint.



- Initially: ci = check
- Later: may add reporting/coverage export but must remain a single mise run ci entrypoint.







6.9 verify





Heavier validation gate.

May include:



- integration tests
- docker build + smoke test
- e2e tests
- security scans
- docs build
- migration checks





verify should use workspace.toml to decide what to run in apps shape.









7. Mise Conventions







7.1 Task Surface





All contract tasks must be present as mise tasks.





7.2 Task Scope





- Single-project tasks operate at repo root.
- Apps workspace tasks iterate the module manifest.
- Tasks must provide clear, prefixed output per module (to help agents attribute failures).







7.3 One Source of Truth





GitHub Actions should call mise run ci and not duplicate the underlying commands.









8. Reference Implementations and Parity Targets





agent-scaffold v1 is informed by and should preserve the “batteries included” capabilities of:



- python-collab-template (uv + ruff + ty + pytest, pre-commit, docs, docker, GitHub Actions, local CI via act, interactive init)
    https://github.com/safurrier/python-collab-template
- go-template-project (interactive init, quality gates, pre-commit mirroring CI, docker-compose, distroless Docker images, CI/Security/Release workflows, docs pipeline)
    https://github.com/safurrier/go-template-project





agent-scaffold is allowed to normalize naming and task surfaces, but should retain the spirit:



- one-command quality gate
- CI parity with local checks
- project initialization automation
- practical docs/docker patterns











9. Rust Template (Planned Stack Module)







9.1 Tooling





- fmt: cargo fmt
- lint: cargo clippy --all-targets --all-features -- -D warnings
- typecheck: cargo check --all-targets --all-features
- test: cargo test --all-features
- build: cargo build --release







9.2 Layout





Single-project:



- either root crate (default) or workspace-ready crates/<name>/ (optional)
    Apps shape:
- apps/<service>/ as a crate, plus optional packages/<lib>/ crates







9.3 verify additions (optional)





- cargo audit / cargo deny (security workflow)
- Docker build + smoke test for service templates











10. Acceptance Criteria (v1)





11. mise run init supports interactive + non-interactive modes.
12. init can produce either:


- a single-project repo, or
- an apps workspace repo with a module manifest.

4.

5. All contract tasks exist and run in both shapes.
6. check is deterministic and fast, and does not require external services by default.
7. GitHub Actions uses a single entrypoint: mise run ci.
8. The repo includes clear docs for humans/agents describing:


- the task contract
- repo shape selection
- how to run fast checks vs heavy verification

10.

11. Parity target: core functionality of the referenced Python and Go templates is preserved (init automation, quality gates, pre-commit, CI patterns).











12. Future Extensions (post-v1)





- “Changed modules only” execution for apps shape
- Parallel task execution across modules
- Optional gen task for code generation when needed
- Optional Bazel/Buck2 profile for scale mode
- More structured release automation per language
