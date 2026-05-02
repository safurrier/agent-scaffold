"""Cyclopts CLI for Harness Kit portable workflow state."""

from __future__ import annotations

import json as json_lib
import shlex
import sys
from pathlib import Path
from typing import Literal

from cyclopts import App

from harness_toolkit.kit.profiles import (
    PROFILE_SELECTION_GUIDANCE,
    ProfileCatalog,
    ProfileError,
    ProfileName,
    checks_to_json,
)
from harness_toolkit.kit.workflow import (
    AttachResult,
    PlanResult,
    SyncResult,
    WorkflowError,
    WorkflowStatus,
    attach_workflow,
    create_plan,
    git_root,
    preview_attach,
    sync_check,
    to_jsonable,
    workflow_status,
)
from harness_toolkit.names import KIT_COMMAND, SCAFFOLD_COMMAND

WorkflowMode = Literal["external", "overlay"]

# Keep this module as the Cyclopts adapter. If command behavior grows beyond
# argument parsing, output formatting, and error translation, move application
# operations behind a deeper kit module.
app = App(
    name=Path(sys.argv[0]).name,
    help="Use Harness Kit planning in any repo without committing scaffold files.",
)
profile_app = App(name="profile", help="List, show, and create workflow profiles.")
app.command(profile_app, name="profile")


def resolve_catalog(profiles_dir: Path | None) -> ProfileCatalog:
    return ProfileCatalog.load(profiles_dir)


def agents_snippet(
    profile_name: ProfileName, *, profiles_dir: Path | None = None
) -> str:
    catalog = resolve_catalog(profiles_dir)
    profile = catalog.get(profile_name)
    profiles_dir_arg = (
        f" --profiles-dir {shlex.quote(str(profiles_dir))}" if profiles_dir else ""
    )
    return f"""## Portable agent workflow

Use `{KIT_COMMAND}` for meaningful work in this repo or scoped path. Do not create or commit `.ai/`, `.agent/`, `.mise/`, or `.gitignore` workflow files unless the user explicitly asks to adopt {SCAFFOLD_COMMAND} in this repository.

Profile: `{profile.name}` — {profile.summary}

Standard loop:

```bash
{KIT_COMMAND} profile list --target .{profiles_dir_arg} --json
# choose the closest profile yourself and tell the user once why you chose it
{KIT_COMMAND} status --target . --profile {profile.name}{profiles_dir_arg} --json
{KIT_COMMAND} plan <slug> --target . --profile {profile.name}{profiles_dir_arg} --json
{KIT_COMMAND} checks --target . --profile {profile.name}{profiles_dir_arg} --json
# run the suggested validation command directly, then update VALIDATION.md
{KIT_COMMAND} sync-check --target . --profile {profile.name}{profiles_dir_arg} --json
```

Important: `{KIT_COMMAND}` manages planning and handoff state only. It does not run validation commands. Agents should run profile-suggested commands directly so raw output stays visible in the normal shell loop.

{profile.instructions}
"""


def print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


def emit(
    value: AttachResult | PlanResult | WorkflowStatus | SyncResult, *, json: bool
) -> None:
    if json:
        print(to_jsonable(value))
        return

    if isinstance(value, AttachResult | WorkflowStatus):
        print(f"state_dir={value.state_dir}")
        print(f"target_root={value.target_root}")
        print(f"target_scope={value.target_scope}")
        print(f"scope={value.scope}")
        print(f"mode={value.mode}")
    elif isinstance(value, PlanResult | SyncResult):
        print(f"plan_dir={value.plan_dir}")


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk instructions\n"
        "  hk instructions --profile python\n"
        "  hk instructions --profile my-project-api --profiles-dir ~/.config/harness-toolkit/profiles --json"
    )
)
def instructions(
    *,
    profile: ProfileName = "generic",
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Print the minimal AGENTS.md snippet for harness-wide use.

    Parameters
    ----------
    profile
        Workflow profile to include in the snippet.
    profiles_dir
        Optional directory of custom profile TOML files.
    json
        Print machine-readable JSON with the snippet in `agents_md`.
    """
    try:
        snippet = agents_snippet(profile, profiles_dir=profiles_dir)
    except (KeyError, ProfileError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(
            json_lib.dumps({"agents_md": snippet, "profile": profile}, sort_keys=True)
        )
        return
    print(snippet)


@profile_app.command(
    name="list",
    help_epilogue=(
        "Examples:\n"
        "  hk profile list\n"
        "  hk profile list --target /work/repo --json\n"
        "  hk profile list --profiles-dir ~/.config/harness-toolkit/profiles --json"
    ),
)
def profile_list(
    *,
    target: Path | None = None,
    profiles_dir: Path | None = None,
    mode: WorkflowMode = "external",
    state_root: Path | None = None,
    json: bool = False,
) -> None:
    """List workflow profiles and model-directed selection guidance.

    Parameters
    ----------
    target
        Target repository or scoped path. Included in output for the agent's
        own profile-selection pass; profiles are not auto-ranked.
    profiles_dir
        Optional directory of custom profile TOML files.
    mode
        Accepted for command-shape consistency with stateful workflow commands.
        Profile selection guidance does not read or write workflow state.
    state_root
        Accepted for command-shape consistency with stateful workflow commands.
        Profile selection guidance does not read or write workflow state.
    json
        Print machine-readable JSON.
    """
    _ = (mode, state_root)
    try:
        catalog = resolve_catalog(profiles_dir)
        resolved_target: Path | None = None
        resolved_root: Path | None = None
        if target is not None:
            resolved_target = target.resolve()
            resolved_root = git_root(resolved_target)
    except (WorkflowError, ProfileError) as e:
        print_error(f"{e}\nTry: hk profile list --target <repo> --json")
        raise SystemExit(1) from e

    if json:
        print(catalog.list_json(target=resolved_target, repo_root=resolved_root))
        return
    if resolved_target is not None and resolved_root is not None:
        print(f"Target: {resolved_target}")
        print("Profile selection guidance:")
        print(PROFILE_SELECTION_GUIDANCE.strip())
        print()
    for name in catalog.names():
        loaded = catalog.loaded(name)
        source = f" [{loaded.source}]"
        print(f"{loaded.profile.name}{source}: {loaded.profile.summary}")


@profile_app.command(
    name="show",
    help_epilogue=(
        "Examples:\n"
        "  hk profile show python\n"
        "  hk profile show my-project-api --profiles-dir ~/.config/harness-toolkit/profiles --json"
    ),
)
def profile_show(
    name: ProfileName,
    *,
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Show one workflow profile.

    Parameters
    ----------
    name
        Profile name.
    profiles_dir
        Optional directory of custom profile TOML files.
    json
        Print machine-readable JSON.
    """
    try:
        catalog = resolve_catalog(profiles_dir)
        selected = catalog.loaded(name)
    except (KeyError, ProfileError) as e:
        print_error(str(e))
        raise SystemExit(1) from e

    if json:
        print(catalog.profile_json(name))
        return
    print(f"{selected.profile.name}: {selected.profile.summary}")
    print(
        f"Source: {selected.source}" + (f" ({selected.path})" if selected.path else "")
    )
    print()
    print(selected.profile.instructions.strip())
    print()
    print("Checks:")
    for check in selected.profile.checks:
        print(f"- {check.name}: {check.command_template}")


@profile_app.command(
    name="create",
    help_epilogue=(
        "Examples:\n"
        "  hk profile create my-project-api --target my_project/api --preset python --output ~/.config/harness-toolkit/profiles/my-project-api.toml\n"
        "  hk profile create foreman-root --target /work/foreman --preset rust-mise --stdout"
    ),
)
def profile_create(
    name: ProfileName,
    *,
    target: Path,
    preset: str = "generic",
    output: Path | None = None,
    profiles_dir: Path | None = None,
    stdout: bool = False,
    force: bool = False,
    json: bool = False,
) -> None:
    """Create an editable profile TOML template without modifying the target repo.

    Parameters
    ----------
    name
        New profile name, usually matching a target/module contract.
    target
        Target repository or scoped path the profile is meant to describe.
    preset
        Built-in preset used to seed checks. This is explicit and not inferred.
    output
        File to write. If omitted, `--profiles-dir <dir>` writes `<dir>/<name>.toml`.
    profiles_dir
        Optional output directory used when `--output` is omitted.
    stdout
        Print the template instead of writing a file.
    force
        Overwrite an existing output file.
    json
        Print machine-readable result metadata when writing a file.
    """
    try:
        content = ProfileCatalog.load().template(name, target=target, preset=preset)
    except ProfileError as e:
        print_error(str(e))
        raise SystemExit(1) from e

    if stdout:
        print(content, end="")
        return

    destination = output
    if destination is None and profiles_dir is not None:
        destination = profiles_dir / f"{name}.toml"
    if destination is None:
        print_error(
            "profile create requires --output, --profiles-dir, or --stdout\n"
            "Try: hk profile create <name> --target <path> --output <file>"
        )
        raise SystemExit(1)
    if destination.exists() and not force:
        print_error(
            f"profile file already exists: {destination}\n"
            "Try: pass --force to overwrite, or choose a different --output"
        )
        raise SystemExit(1)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(content)
    if json:
        print(
            json_lib.dumps(
                {
                    "profile": name,
                    "path": str(destination),
                    "preset": preset,
                    "target": str(target),
                },
                sort_keys=True,
            )
        )
        return
    print(f"Created profile: {destination}")
    print()
    print("Next:")
    print("  1. Edit TODOs and confirm commands.")
    print("  2. Run:")
    print(f"     hk profile show {name} --profiles-dir {destination.parent} --json")
    print(
        f"     hk checks --target {target} --profile {name} --profiles-dir {destination.parent} --json"
    )


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk checks --profile python --target /work/my-python-package --json\n"
        "  hk checks --profile my-project-api --profiles-dir ~/.config/harness-toolkit/profiles --target /work/repo/my_project/api"
    )
)
def checks(
    *,
    profile: ProfileName = "generic",
    target: Path = Path("."),
    profiles_dir: Path | None = None,
    mode: WorkflowMode = "external",
    state_root: Path | None = None,
    json: bool = False,
) -> None:
    """Show named verification checks for a profile without executing them.

    Parameters
    ----------
    profile
        Workflow profile.
    target
        Target repository or scoped path. Used to resolve repo-root guidance.
    profiles_dir
        Optional directory of custom profile TOML files.
    mode
        Accepted for command-shape consistency with stateful workflow commands.
        Check discovery does not read or write workflow state.
    state_root
        Accepted for command-shape consistency with stateful workflow commands.
        Check discovery does not read or write workflow state.
    json
        Print machine-readable JSON.
    """
    _ = (mode, state_root)
    try:
        catalog = resolve_catalog(profiles_dir)
        resolved_target = target.resolve()
        view = catalog.checks_view(
            profile,
            target=resolved_target,
            repo_root=git_root(resolved_target),
        )
    except (KeyError, ProfileError, WorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(checks_to_json(view))
        return
    print(f"Profile: {view.profile}")
    print(f"Target: {view.target}")
    print(view.reminder)
    print()
    for check in view.checks:
        print(f"{check.name}: {check.purpose}")
        print(f"  command: {check.command_template}")
        print(f"  run from: {check.run_from}")
        if check.required_inputs:
            print(f"  inputs: {', '.join(check.required_inputs)}")


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk attach --target /work/repo --mode external --json\n"
        "  hk attach --target /work/repo --mode overlay\n"
        "  hk attach --target /work/repo --dry-run --json"
    )
)
def attach(
    *,
    target: Path = Path("."),
    mode: WorkflowMode = "external",
    state_root: Path | None = None,
    json: bool = False,
    dry_run: bool = False,
) -> None:
    """Prepare portable workflow state for a target repo."""
    try:
        if dry_run:
            result = preview_attach(target, mode=mode, state_root=state_root)
        else:
            result = attach_workflow(target, mode=mode, state_root=state_root)
    except WorkflowError as e:
        print_error(f"{e}\nTry: hk attach --target <repo> --mode external --json")
        raise SystemExit(1) from e
    emit(result, json=json)


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk plan investigate-cache-bug --target /work/repo --json\n"
        "  hk plan api-timeout --target /work/my-python-package --profile python --json"
    )
)
def plan(
    slug: str,
    *,
    target: Path = Path("."),
    mode: WorkflowMode = "external",
    profile: ProfileName = "generic",
    profiles_dir: Path | None = None,
    state_root: Path | None = None,
    json: bool = False,
) -> None:
    """Create a local workflow plan for a target repo."""
    try:
        catalog = resolve_catalog(profiles_dir)
        catalog.get(profile)
        result = create_plan(target, slug, mode=mode, state_root=state_root)
    except (WorkflowError, KeyError, ProfileError) as e:
        print_error(f"{e}\nTry: hk plan my-slice --target <repo> --json")
        raise SystemExit(1) from e
    emit(result, json=json)


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk status --target /work/repo\n"
        "  hk status --target /work/repo --json"
    )
)
def status(
    *,
    target: Path = Path("."),
    mode: WorkflowMode = "external",
    profile: ProfileName = "generic",
    profiles_dir: Path | None = None,
    state_root: Path | None = None,
    json: bool = False,
) -> None:
    """Show portable workflow status for a target repo."""
    try:
        catalog = resolve_catalog(profiles_dir)
        catalog.get(profile)
        result = workflow_status(target, mode=mode, state_root=state_root)
    except (WorkflowError, KeyError, ProfileError) as e:
        print_error(f"{e}\nTry: hk status --target <repo> --json")
        raise SystemExit(1) from e
    emit(result, json=json)


@app.command(
    name="sync-check",
    help_epilogue=(
        "Examples:\n"
        "  hk sync-check --target /work/repo\n"
        "  hk sync-check --target /work/repo --json"
    ),
)
def sync_check_command(
    *,
    target: Path = Path("."),
    mode: WorkflowMode = "external",
    profile: ProfileName = "generic",
    profiles_dir: Path | None = None,
    state_root: Path | None = None,
    json: bool = False,
) -> None:
    """Run local handoff checks for portable workflow state."""
    try:
        catalog = resolve_catalog(profiles_dir)
        catalog.get(profile)
        result = sync_check(target, mode=mode, state_root=state_root)
    except (WorkflowError, KeyError, ProfileError) as e:
        print_error(
            f"{e}\nTry: hk status --target <repo> --json to find the active plan"
        )
        raise SystemExit(1) from e
    emit(result, json=json)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
