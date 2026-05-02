"""Built-in and custom profile/check DSL for portable agent workflows.

Profiles describe named verification loops. They intentionally do not execute
those loops; agents should run the suggested commands directly so raw output stays
visible in the normal agent shell loop.
"""

from __future__ import annotations

import json
import re
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, cast

from harness_toolkit.names import KIT_COMMAND

ProfileName = str
ProfileSource = Literal["built-in", "file"]
RunFrom = Literal["target", "repo-root", "current-directory", "external-ui"]
VALID_RUN_FROM: tuple[RunFrom, ...] = (
    "target",
    "repo-root",
    "current-directory",
    "external-ui",
)
BUILTIN_PRESETS = ("generic", "python", "go", "rust", "rust-mise")


@dataclass(frozen=True)
class CheckDefinition:
    name: str
    purpose: str
    command_template: str
    run_from: RunFrom
    required_inputs: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    agent_should_run_directly: bool = True


@dataclass(frozen=True)
class WorkflowProfile:
    name: ProfileName
    title: str
    summary: str
    target_hint: str
    instructions: str
    checks: tuple[CheckDefinition, ...]


@dataclass(frozen=True)
class LoadedProfile:
    profile: WorkflowProfile
    source: ProfileSource
    path: str | None = None


@dataclass(frozen=True)
class ProfileCheckView:
    profile: ProfileName
    target: str
    repo_root: str
    checks: tuple[CheckDefinition, ...]
    reminder: str


class ProfileError(ValueError):
    """Raised when profile loading or validation fails."""


@dataclass(frozen=True)
class ProfileCatalog:
    """Loaded profile catalog with lookup, views, and template generation."""

    profiles: dict[str, LoadedProfile]

    @classmethod
    def load(cls, profiles_dir: Path | None = None) -> ProfileCatalog:
        return cls(load_profile_catalog(profiles_dir))

    def names(self) -> tuple[ProfileName, ...]:
        return tuple(self.profiles)

    def loaded(self, name: str) -> LoadedProfile:
        return get_loaded_profile(name, self.profiles)

    def get(self, name: str) -> WorkflowProfile:
        return self.loaded(name).profile

    def list_json(
        self, *, target: Path | None = None, repo_root: Path | None = None
    ) -> str:
        return profiles_to_json(self.profiles, target=target, repo_root=repo_root)

    def profile_json(self, name: str) -> str:
        loaded = self.loaded(name)
        return profile_to_json(loaded.profile, source=loaded.source, path=loaded.path)

    def checks_view(
        self, name: str, *, target: Path, repo_root: Path
    ) -> ProfileCheckView:
        return checks_view(name, target, repo_root, catalog=self.profiles)

    def template(self, name: str, *, target: Path, preset: str = "generic") -> str:
        return profile_template(name, target=target, preset=preset)


GENERIC_INSTRUCTIONS = f"""Use this profile when a repo has no more specific built-in or custom profile.

Before choosing generic, run `{KIT_COMMAND} profile list --target <target> --json`
and check whether a module, repo, language, or task-runner profile matches the
checkout. Inspect the repo's own AGENTS.md, README, and docs for validation
commands. If the repo has adopted harness-scaffold or a similar task contract,
prefer its documented fast and heavy gates. Otherwise run the repo-native fast
gate directly and record the exact command/result in the portable plan's
`VALIDATION.md`.
"""

PYTHON_INSTRUCTIONS = """Use this profile for Python projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `uv run pytest`, `uv run ruff check .`, and `uv run ty check` or the repo's
configured type checker. Run commands directly and record exact command/result
evidence in the plan.
"""

GO_INSTRUCTIONS = """Use this profile for Go projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `go test ./...`, `go vet ./...`, and the repo's formatter/linter. Run commands
directly and record exact command/result evidence in the plan.
"""

RUST_INSTRUCTIONS = """Use this profile for Rust projects.

Prefer the repository's documented task runner when one exists. Common fast loops
are `cargo test`, `cargo check`, `cargo clippy`, and `cargo fmt --check`. Run
commands directly and record exact command/result evidence in the plan.
"""

RUST_MISE_INSTRUCTIONS = f"""Use this profile for Rust projects that expose a mise task contract.

Prefer `mise run check` as the fast local gate and `mise run verify` when the
change needs heavier confidence. Run commands directly and record exact
command/result evidence in the plan. Do not assume a repo-native `mise run
sync-check` exists; for portable workflow handoff state, use `{KIT_COMMAND}
sync-check`.
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
                name="handoff",
                purpose="Validate portable plan evidence and review state.",
                command_template=f"{KIT_COMMAND} sync-check --target <target> --profile generic --json",
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
                command_template="gofmt -w <changed_files>",
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
                name="handoff",
                purpose="Validate portable plan evidence and review state.",
                command_template=f"{KIT_COMMAND} sync-check --target <target> --profile rust-mise --json",
                run_from="current-directory",
                notes=(
                    "This checks recorded portable evidence; it does not rerun validation.",
                    "Do not assume the target repo has its own `mise run sync-check` task.",
                ),
            ),
        ),
    ),
}

PROFILE_SELECTION_GUIDANCE = """Choose the closest available profile yourself; the CLI does not auto-select one.

Match the profile to the target scope, not just the repository root. In monorepos,
pass `--target` as the module/package/crate directory that owns the work, then
inspect that module's files first and repo-level AGENTS.md/README guidance second.
Prefer profiles in this order:
1. exact target/module profile
2. repo-specific profile
3. stack/task-runner profile
4. generic fallback

Tell the user once which profile you chose and why, then use that profile
consistently for plan, checks, and sync-check.

Examples:
- --target my_project/api and profile my-project-api exists -> my-project-api
- --target my_project/api and no module profile exists, but pyproject.toml exists -> python
- --target crates/tui and profile foreman-tui exists -> foreman-tui
- --target crates/tui and no module profile exists, but Cargo.toml exists -> rust
- Rust repo with mise task contract but no exact module profile -> rust-mise
- no close target/module match -> generic
"""


def profile_names(
    catalog: dict[str, LoadedProfile] | None = None,
) -> tuple[ProfileName, ...]:
    return tuple((catalog or load_profile_catalog()).keys())


def _loaded_builtins() -> dict[str, LoadedProfile]:
    return {
        name: LoadedProfile(profile=profile, source="built-in")
        for name, profile in BUILTIN_PROFILES.items()
    }


def load_profile_catalog(profiles_dir: Path | None = None) -> dict[str, LoadedProfile]:
    catalog = _loaded_builtins()
    if profiles_dir is None:
        return catalog

    if not profiles_dir.exists():
        raise ProfileError(f"profiles directory does not exist: {profiles_dir}")
    if not profiles_dir.is_dir():
        raise ProfileError(f"profiles path is not a directory: {profiles_dir}")

    for path in sorted(profiles_dir.glob("*.toml")):
        loaded = load_profile_file(path)
        catalog[loaded.profile.name] = loaded
    return catalog


def load_profile_file(path: Path) -> LoadedProfile:
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ProfileError(f"invalid profile TOML {path}: {e}") from e
    profile = parse_profile_data(data, source=str(path))
    return LoadedProfile(profile=profile, source="file", path=str(path))


def _required_str(data: dict[str, object], key: str, *, source: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(f"profile {source} must define non-empty string '{key}'")
    return value


def _optional_str_tuple(
    data: dict[str, object], key: str, *, source: str
) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProfileError(f"profile {source} field '{key}' must be a string array")
    return tuple(cast("list[str]", value))


def parse_profile_data(data: object, *, source: str) -> WorkflowProfile:
    if not isinstance(data, dict):
        raise ProfileError(f"profile {source} must be a TOML table")
    data = cast("dict[str, object]", data)

    name = _required_str(data, "name", source=source)
    validate_profile_name(name)
    checks_data = data.get("checks")
    if not isinstance(checks_data, list) or not checks_data:
        raise ProfileError(
            f"profile {source} must define at least one [[checks]] entry"
        )

    checks: list[CheckDefinition] = []
    for index, raw_check in enumerate(checks_data, start=1):
        if not isinstance(raw_check, dict):
            raise ProfileError(f"profile {source} check #{index} must be a TOML table")
        run_from = _required_str(raw_check, "run_from", source=source)
        if run_from not in VALID_RUN_FROM:
            valid = ", ".join(VALID_RUN_FROM)
            raise ProfileError(
                f"profile {source} check #{index} has invalid run_from '{run_from}'. Valid: {valid}"
            )
        agent_should_run_directly = raw_check.get("agent_should_run_directly", True)
        if not isinstance(agent_should_run_directly, bool):
            raise ProfileError(
                f"profile {source} check #{index} field 'agent_should_run_directly' must be boolean"
            )
        checks.append(
            CheckDefinition(
                name=_required_str(raw_check, "name", source=source),
                purpose=_required_str(raw_check, "purpose", source=source),
                command_template=_required_str(
                    raw_check, "command_template", source=source
                ),
                run_from=run_from,  # type: ignore[arg-type]
                required_inputs=_optional_str_tuple(
                    raw_check, "required_inputs", source=source
                ),
                notes=_optional_str_tuple(raw_check, "notes", source=source),
                agent_should_run_directly=agent_should_run_directly,
            )
        )

    return WorkflowProfile(
        name=name,
        title=_required_str(data, "title", source=source),
        summary=_required_str(data, "summary", source=source),
        target_hint=_required_str(data, "target_hint", source=source),
        instructions=_required_str(data, "instructions", source=source),
        checks=tuple(checks),
    )


def validate_profile_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ProfileError(
            "profile name must be lowercase and contain only letters, numbers, '.', '_', or '-'"
        )


def get_loaded_profile(
    name: str, catalog: dict[str, LoadedProfile] | None = None
) -> LoadedProfile:
    resolved_catalog = catalog or load_profile_catalog()
    if name not in resolved_catalog:
        valid = ", ".join(resolved_catalog)
        raise KeyError(f"Unknown profile '{name}'. Valid profiles: {valid}")
    return resolved_catalog[name]


def get_profile(
    name: str, catalog: dict[str, LoadedProfile] | None = None
) -> WorkflowProfile:
    return get_loaded_profile(name, catalog).profile


def profile_to_json(
    profile: WorkflowProfile, *, source: str = "built-in", path: str | None = None
) -> str:
    payload = asdict(profile)
    payload["source"] = source
    if path is not None:
        payload["path"] = path
    return json.dumps(payload, indent=2, sort_keys=True)


def profiles_to_json(
    catalog: dict[str, LoadedProfile] | None = None,
    target: Path | None = None,
    repo_root: Path | None = None,
) -> str:
    resolved_catalog = catalog or load_profile_catalog()
    rows = [
        {
            "name": loaded.profile.name,
            "title": loaded.profile.title,
            "summary": loaded.profile.summary,
            "target_hint": loaded.profile.target_hint,
            "source": loaded.source,
            **({"path": loaded.path} if loaded.path else {}),
        }
        for loaded in resolved_catalog.values()
    ]
    payload: dict[str, object] = {
        "profiles": rows,
        "selection_guidance": PROFILE_SELECTION_GUIDANCE,
    }
    if target is not None and repo_root is not None:
        payload.update({"target": str(target), "repo_root": str(repo_root)})
    return json.dumps(payload, indent=2, sort_keys=True)


def checks_view(
    profile_name: str,
    target: Path,
    repo_root: Path,
    catalog: dict[str, LoadedProfile] | None = None,
) -> ProfileCheckView:
    profile = get_profile(profile_name, catalog)
    return ProfileCheckView(
        profile=profile.name,
        target=str(target),
        repo_root=str(repo_root),
        checks=profile.checks,
        reminder=(
            "Run validation commands directly in the agent shell loop, then record "
            "the exact command/result in the portable plan's VALIDATION.md."
        ),
    )


def checks_to_json(view: ProfileCheckView) -> str:
    return json.dumps(asdict(view), indent=2, sort_keys=True)


def _toml_string(value: str) -> str:
    return json.dumps(value)


def _toml_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(_toml_string(value) for value in values) + "]"


def _title_from_name(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def profile_template(name: str, *, target: Path, preset: str = "generic") -> str:
    validate_profile_name(name)
    if preset not in BUILTIN_PRESETS:
        valid = ", ".join(BUILTIN_PRESETS)
        raise ProfileError(f"Unknown preset '{preset}'. Valid presets: {valid}")

    preset_profile = BUILTIN_PROFILES[preset]
    target_text = str(target)
    instructions = (
        f"Use this profile for work under {target_text}.\n\n"
        "TODO:\n"
        "- Confirm the fast validation gate for this target/module.\n"
        "- Confirm focused test command patterns.\n"
        "- Confirm when heavier validation is required.\n\n"
        "Run validation commands directly and record exact command/result evidence "
        "in VALIDATION.md before handoff."
    )

    checks = [check for check in preset_profile.checks if check.name != "handoff"]
    if preset == "generic":
        checks = [
            CheckDefinition(
                name="fast-gate",
                purpose="TODO: Run the fastest validation gate appropriate before handoff.",
                command_template="TODO: e.g. mise run check",
                run_from="repo-root",
                notes=("Replace this TODO before relying on the profile.",),
            ),
            CheckDefinition(
                name="focused-tests",
                purpose="TODO: Run focused tests for the changed area.",
                command_template="TODO: e.g. uv run pytest <test_path_or_selector>",
                run_from="target",
                required_inputs=("test_path_or_selector",),
                notes=("Use the smallest test path that covers the change.",),
            ),
        ]
    checks.append(
        CheckDefinition(
            name="handoff",
            purpose="Validate portable workflow evidence and review state.",
            command_template=f"{KIT_COMMAND} sync-check --target <target> --profile {name} --json",
            run_from="current-directory",
            notes=("This checks recorded evidence; it does not rerun validation.",),
        )
    )

    lines = [
        f"name = {_toml_string(name)}",
        f"title = {_toml_string(_title_from_name(name))}",
        f"summary = {_toml_string(f'TODO: Describe the validation contract for {target_text}.')}",
        f"target_hint = {_toml_string(f'Use --target {target_text}.')}",
        "",
        f"instructions = {_toml_string(instructions)}",
        "",
    ]
    for check in checks:
        lines.extend(
            [
                "[[checks]]",
                f"name = {_toml_string(check.name)}",
                f"purpose = {_toml_string(check.purpose)}",
                f"command_template = {_toml_string(check.command_template)}",
                f"run_from = {_toml_string(check.run_from)}",
            ]
        )
        if check.required_inputs:
            lines.append(f"required_inputs = {_toml_array(check.required_inputs)}")
        if check.notes:
            lines.append(f"notes = {_toml_array(check.notes)}")
        if not check.agent_should_run_directly:
            lines.append("agent_should_run_directly = false")
        lines.append("")
    return "\n".join(lines)
