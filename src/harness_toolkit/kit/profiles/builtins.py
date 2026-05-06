"""Built-in Harness Kit profile definitions."""

from __future__ import annotations

from harness_toolkit.kit.profiles.models import (
    CheckDefinition,
    LoadedProfile,
    ProfileName,
    WorkflowProfile,
)
from harness_toolkit.names import KIT_COMMAND

GENERIC_INSTRUCTIONS = f"""Use this profile when a repo has no more specific built-in or custom profile.

Before choosing generic, run `{KIT_COMMAND} profile list --target <target> --json`
and check whether a module, repo, language, or task-runner profile matches the
checkout. Inspect the repo's own AGENTS.md, README, and docs for validation
commands. If the repo has adopted harness-scaffold or a similar task contract,
prefer its documented fast and heavy gates. Otherwise run the repo-native fast
gate directly and record the exact command/result with `hk validate --why`.
"""

PYTHON_INSTRUCTIONS = """Use this profile for Python projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `uv run pytest`, `uv run ruff check .`, and `uv run ty check` or the repo's
configured type checker. Run commands directly and record exact command/result
evidence with `hk validate --why`.
"""

GO_INSTRUCTIONS = """Use this profile for Go projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `go test ./...`, `go vet ./...`, and the repo's formatter/linter. Run commands
directly and record exact command/result evidence with `hk validate --why`.
"""

RUST_INSTRUCTIONS = """Use this profile for Rust projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `cargo test`, `cargo check`, `cargo clippy`, and `cargo fmt --check`. Run
commands directly and record exact command/result evidence with `hk validate --why`.
"""

RUST_MISE_INSTRUCTIONS = f"""Use this profile for Rust projects that expose a mise task contract.

Prefer `mise run check` as the fast local gate and `mise run verify` when the
change needs heavier confidence. Run commands directly and record exact
command/result evidence with `hk validate --why`. Do not assume a repo-native `mise run
sync-check` exists; for Harness Kit lifecycle handoff state, use `{KIT_COMMAND} sync`,
`{KIT_COMMAND} ready`, and `{KIT_COMMAND} handoff`.
"""


BUILTIN_PROFILES: dict[ProfileName, WorkflowProfile] = {
    "generic": WorkflowProfile(
        name="generic",
        title="Generic repository",
        summary="Fallback profile for repos without a more specific built-in or custom contract.",
        target_hint="Pass the repo or module path that owns the work.",
        instructions=GENERIC_INSTRUCTIONS,
        checks=(
            CheckDefinition(
                name="repo-native-fast-gate",
                purpose="Run the repository's documented fast validation gate.",
                command_template="<repo documented fast gate, e.g. mise run check>",
                run_from="target",
                required_inputs=("documented_command",),
                notes=(
                    "Inspect local AGENTS.md/README/docs first.",
                    f"Run the command directly; do not route it through {KIT_COMMAND}.",
                ),
            ),
            CheckDefinition(
                name="handoff-readiness",
                purpose="Checkpoint lifecycle freshness and check handoff readiness.",
                command_template=f"{KIT_COMMAND} sync --target <target> --json && {KIT_COMMAND} ready --target <target> --json",
                run_from="current-directory",
                notes=("This checks recorded evidence; it does not rerun validation.",),
            ),
        ),
    ),
    "python": WorkflowProfile(
        name="python",
        title="Python project",
        summary="Python validation loops for tests, lint, and type checks.",
        target_hint="Use --target <python project or package path>.",
        instructions=PYTHON_INSTRUCTIONS,
        checks=(
            CheckDefinition(
                name="tests",
                purpose="Run the Python test suite or focused test path.",
                command_template="uv run pytest <test_path_or_selector>",
                run_from="target",
                required_inputs=("test_path_or_selector",),
                notes=(
                    "Use the repo's documented pytest wrapper if it has one.",
                    "For focused work, prefer the smallest test path that covers the change.",
                ),
            ),
            CheckDefinition(
                name="lint",
                purpose="Run Python lint checks.",
                command_template="uv run ruff check .",
                run_from="target",
                notes=("Use the repo's configured lint command when different.",),
            ),
            CheckDefinition(
                name="typecheck",
                purpose="Run Python static type checks.",
                command_template="uv run ty check",
                run_from="target",
                notes=(
                    "Use mypy, pyright, or the repo's configured checker when different.",
                ),
            ),
        ),
    ),
    "go": WorkflowProfile(
        name="go",
        title="Go project",
        summary="Go validation loops for tests, vet, and formatting.",
        target_hint="Use --target <Go module path>.",
        instructions=GO_INSTRUCTIONS,
        checks=(
            CheckDefinition(
                name="tests",
                purpose="Run Go tests for all packages or a focused package.",
                command_template="go test ./...",
                run_from="target",
                notes=(
                    "Narrow to ./path/... when the repo is large and the change is focused.",
                ),
            ),
            CheckDefinition(
                name="vet",
                purpose="Run Go static analysis.",
                command_template="go vet ./...",
                run_from="target",
            ),
            CheckDefinition(
                name="format-check",
                purpose="Check Go formatting using the repo's formatter.",
                command_template='test -z "$(gofmt -l <changed_files>)"',
                run_from="target",
                required_inputs=("changed_files",),
                notes=("Use gofumpt or repo-specific formatter when documented.",),
            ),
        ),
    ),
    "rust": WorkflowProfile(
        name="rust",
        title="Rust project",
        summary="Rust validation loops for tests, check, clippy, and formatting.",
        target_hint="Use --target <Cargo project or workspace path>.",
        instructions=RUST_INSTRUCTIONS,
        checks=(
            CheckDefinition(
                name="tests",
                purpose="Run Rust tests.",
                command_template="cargo test",
                run_from="target",
            ),
            CheckDefinition(
                name="check",
                purpose="Run Rust type/compile checks without building final artifacts.",
                command_template="cargo check --all-targets --all-features",
                run_from="target",
            ),
            CheckDefinition(
                name="clippy",
                purpose="Run Rust lints.",
                command_template="cargo clippy --all-targets --all-features -- -D warnings",
                run_from="target",
            ),
            CheckDefinition(
                name="format-check",
                purpose="Check Rust formatting.",
                command_template="cargo fmt --check",
                run_from="target",
            ),
        ),
    ),
    "rust-mise": WorkflowProfile(
        name="rust-mise",
        title="Rust project with mise task contract",
        summary="Rust validation through repo-native mise gates such as `mise run check` and `mise run verify`.",
        target_hint="Use --target <Rust workspace or crate path> that owns the mise contract.",
        instructions=RUST_MISE_INSTRUCTIONS,
        checks=(
            CheckDefinition(
                name="fast-gate",
                purpose="Run the repo's fast local validation gate before handoff.",
                command_template="mise run check",
                run_from="repo-root",
                notes=(
                    "If mise reports the checkout is untrusted, run `mise trust .mise.toml` and retry.",
                    "Prefer this over individual cargo commands when AGENTS.md or README names it as the fast gate.",
                ),
            ),
            CheckDefinition(
                name="heavy-gate",
                purpose="Run heavier validation for runtime-sensitive or merge-ready changes.",
                command_template="mise run verify",
                run_from="repo-root",
                notes=(
                    "Use when the repo guidance or risk level calls for broader confidence.",
                ),
            ),
            CheckDefinition(
                name="handoff-readiness",
                purpose="Checkpoint lifecycle freshness and check handoff readiness.",
                command_template=f"{KIT_COMMAND} sync --target <target> --json && {KIT_COMMAND} ready --target <target> --json",
                run_from="current-directory",
                notes=(
                    "This checks recorded portable evidence; it does not rerun validation.",
                    "Do not assume the target repo has its own `mise run sync-check` task.",
                ),
            ),
        ),
    ),
}


def loaded_builtins() -> dict[str, LoadedProfile]:
    return {
        name: LoadedProfile(profile=profile, source="built-in")
        for name, profile in BUILTIN_PROFILES.items()
    }
