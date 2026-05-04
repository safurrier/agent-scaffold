"""Cyclopts CLI for Harness Kit portable workflow state."""

from __future__ import annotations

import json as json_lib
import shlex
import sys
from pathlib import Path
from typing import Literal

from cyclopts import App

from harness_toolkit.kit.local import (
    LocalWorkflowError,
    active_work_dir,
    add_note,
    brief_markdown,
    capture_command,
    create_work,
    init_spec,
    init_state,
    json_dump_dataclass,
    json_dump_object,
    materialize_work,
    print_capture_and_exit,
    read_evidence,
    resolve_local_state,
    spec_promote_dry_run,
    sync_checkpoint,
)
from harness_toolkit.kit.local import (
    brief as local_brief,
)
from harness_toolkit.kit.local import (
    handoff as local_handoff,
)
from harness_toolkit.kit.local import (
    spec_outline as local_spec_outline,
)
from harness_toolkit.kit.local import (
    spec_status as local_spec_status,
)
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
work_app = App(name="work", help="Manage ledger-backed local work units.")
evidence_app = App(name="evidence", help="List captured evidence.")
spec_app = App(name="spec", help="Manage optional local/external specs.")
app.command(profile_app, name="profile")
app.command(work_app, name="work")
app.command(evidence_app, name="evidence")
app.command(spec_app, name="spec")


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
    help_epilogue=("Examples:\n  hk brief --target .\n  hk brief --target . --json\n")
)
def brief(
    *,
    target: Path = Path("."),
    json: bool = False,
    markdown: bool = False,
    no_local_files: bool = False,
) -> None:
    """Print a read-only repo brief without selecting validation commands."""
    _ = markdown
    try:
        result = local_brief(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(brief_markdown(result), end="")


@app.command(
    name="init",
    help_epilogue=(
        "Examples:\n"
        "  hk init --target . --json\n"
        "  hk init --target . --no-local-files --json\n"
    ),
)
def init_command(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Initialize local or external Harness Kit 2 state for a target."""
    try:
        result = init_state(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"state_dir={result.state_dir}")
    print(f"mode={result.mode}")


@work_app.command(name="start")
def work_start(
    slug: str,
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Start a ledger-backed local work unit."""
    try:
        result = create_work(target, slug, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"work_id={result.work_id}")
    print(f"work_dir={result.work_dir}")


@work_app.command(name="status")
def work_status(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Show active local work status."""
    try:
        state = resolve_local_state(target, no_local_files=no_local_files)
        result = local_brief(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    _ = state
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"active_work={result.active_work or 'none'}")
    print(f"sync_status={result.sync_status}")


@work_app.command(name="materialize")
def work_materialize(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Materialize generated Markdown views for the active work ledger."""
    try:
        result = materialize_work(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.path)


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk note --kind plan 'Implement the agreed sync/readiness docs update'\n"
        "  hk note --kind learning 'Auth timeout is owned by session refresh'\n"
        "  hk note --kind gap 'Full suite not run' --json\n"
        "  hk note --kind plan --from-file /tmp/plan-summary.md\n"
    )
)
def note(
    text: str = "",
    *,
    kind: Literal["plan", "learning", "decision", "gap", "context", "spec-impact"],
    from_file: Path | None = None,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Append a typed plan, learning, decision, gap, context, or spec-impact note."""
    try:
        if from_file is not None:
            if text:
                raise LocalWorkflowError(
                    "Use either note TEXT or --from-file, not both."
                )
            try:
                text = from_file.read_text().strip()
            except OSError as e:
                raise LocalWorkflowError(
                    f"Could not read note file: {from_file}"
                ) from e
        if not text:
            raise LocalWorkflowError("note requires TEXT or --from-file PATH")
        result = add_note(target, kind=kind, text=text, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"{result.kind}: {result.text}")


@app.command(
    help_epilogue=(
        "Examples:\n  hk sync --target .\n  hk sync --check --target . --json\n"
    )
)
def sync(
    *,
    target: Path = Path("."),
    check: bool = False,
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record or check a sync checkpoint for the active work snapshot."""
    try:
        result = sync_checkpoint(target, check=check, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
    else:
        print(result.message)
        if not result.synced:
            print("Guidance:")
            for item in result.guidance:
                print(f"- {item}")
    if check and not result.synced:
        raise SystemExit(1)


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk capture --kind test -- uv run pytest tests/test_example.py -q\n"
        "  hk capture --shell 'pnpm run lint && pnpm run typecheck'\n"
    )
)
def capture(
    command: tuple[str, ...] = (),
    *,
    target: Path = Path("."),
    kind: Literal[
        "test", "lint", "typecheck", "build", "check", "e2e", "other"
    ] = "other",
    shell: str = "",
    no_log: bool = False,
    raw_log: bool = False,
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Run a native command and record exact evidence."""
    try:
        result = capture_command(
            target,
            command,
            shell_command=shell,
            kind=kind,
            no_log=no_log,
            raw_log=raw_log,
            no_local_files=no_local_files,
            stream_to_stderr=json,
        )
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print_capture_and_exit(result)
        return
    print(f"evidence_id={result.evidence_id}")
    print(f"status={result.status}")
    print(f"transcript_path={result.transcript_path}")
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)


@evidence_app.command(name="list")
def evidence_list(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """List captured evidence for the active work unit."""
    try:
        state = resolve_local_state(target, no_local_files=no_local_files)
        work_dir = active_work_dir(state)
        records = read_evidence(work_dir) if work_dir is not None else []
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    rows = [record.__dict__ for record in records]
    if json:
        print(json_dump_object({"evidence": rows}))
        return
    for record in records:
        print(f"{record.id}: {record.status} {record.command_display}")


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk handoff --format markdown\n"
        "  hk handoff --format pr --write /tmp/handoff.md\n"
    )
)
def handoff(
    *,
    target: Path = Path("."),
    format: Literal["markdown", "pr", "json"] = "markdown",
    write: Path | None = None,
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Render a conservative handoff from the active work ledger."""
    _ = format
    try:
        result = local_handoff(target, output_path=write, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json or format == "json":
        print(json_dump_dataclass(result))
        return
    print(result.content, end="")


@spec_app.command(name="init")
def spec_init(
    *,
    local: bool = False,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Create a local draft SPEC without committing repo files."""
    _ = local
    try:
        result = init_spec(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.spec_path)


@spec_app.command(name="status")
def spec_status(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Show the active committed or local SPEC source."""
    try:
        result = local_spec_status(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"{result.source}: {result.spec_path}")


@spec_app.command(name="outline")
def spec_outline(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Print headings from the active committed or local SPEC."""
    try:
        result = local_spec_outline(target, no_local_files=no_local_files)
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    for heading in result.headings:
        print(heading)


@spec_app.command(name="promote")
def spec_promote(
    *,
    dry_run: bool = False,
    target: Path = Path("."),
    no_local_files: bool = False,
) -> None:
    """Preview promoting a local draft SPEC into the target repo."""
    if not dry_run:
        print_error("spec promote currently requires --dry-run")
        raise SystemExit(1)
    try:
        print(spec_promote_dry_run(target, no_local_files=no_local_files), end="")
    except (WorkflowError, LocalWorkflowError) as e:
        print_error(str(e))
        raise SystemExit(1) from e


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
