"""Cyclopts CLI for Harness Kit portable workflow state."""

from __future__ import annotations

import json as json_lib
import shlex
import sys
from pathlib import Path
from typing import Literal

from cyclopts import App

from harness_toolkit.kit.app.lifecycle import (
    ArtifactAttachRequest,
    CaptureRequest,
    DangerousSkipRequest,
    HandoffRequest,
    LifecycleApp,
    NoteRequest,
    ReviewRequest,
    StartRequest,
    SyncRequest,
    TargetRequest,
)
from harness_toolkit.kit.local import (
    LocalWorkflowError,
    active_work_dir,
    brief_markdown,
    json_dump_dataclass,
    json_dump_object,
    print_capture_and_exit,
    read_evidence,
    resolve_local_state,
)
from harness_toolkit.kit.local import (
    brief as local_brief,
)
from harness_toolkit.kit.profiles import (
    PROFILE_SELECTION_GUIDANCE,
    ProfileCatalog,
    ProfileError,
    ProfileName,
    checks_to_json,
    resolution_to_json,
)
from harness_toolkit.kit.state.repo import RepoStateError, git_root
from harness_toolkit.names import KIT_COMMAND, SCAFFOLD_COMMAND

# Keep this module as the Cyclopts adapter. If command behavior grows beyond
# argument parsing, output formatting, and error translation, move application
# operations behind a deeper kit module.
app = App(
    name=Path(sys.argv[0]).name,
    help="Use the Harness Kit lifecycle in any repo without committing scaffold files.",
)
profile_app = App(name="profile", help="List, show, and create workflow profiles.")
work_app = App(name="work", help="Advanced: manage ledger-backed local work units.")
evidence_app = App(name="evidence", help="Inspect captured evidence; use `list`.")
spec_app = App(name="spec", help="Manage optional local/external specs.")
review_app = App(name="review", help="Record external-enough review evidence.")
artifact_app = App(
    name="artifact", help="Attach external files to active Harness Kit work."
)
app.command(profile_app, name="profile")
app.command(work_app, name="work")
app.command(evidence_app, name="evidence")
app.command(spec_app, name="spec")
app.command(review_app, name="review")
app.command(artifact_app, name="artifact")

lifecycle_app = LifecycleApp()


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

Standard agent loop:

```bash
{KIT_COMMAND} brief --target . --json
{KIT_COMMAND} start <slug> --plan 'Adopted implementation intent' --target . --json
# work normally in the repo
{KIT_COMMAND} validate --why 'What this command proves' --target . -- <native command>
{KIT_COMMAND} status --target . --json
{KIT_COMMAND} ready --target . --json
{KIT_COMMAND} handoff --target .
```

Follow `hk status` next actions when it asks for them:

```bash
# optional context when it prevents rediscovery
{KIT_COMMAND} context 'Relevant constraints, files, or repo facts' --target . --json
{KIT_COMMAND} decide 'Decision/spec reflection' --spec-impact none --target . --json
{KIT_COMMAND} checks --target . --profile {profile.name}{profiles_dir_arg} --json
# review is required by default: preferred independent AI/tool reviewer; minimum fresh-context subagent
{KIT_COMMAND} review prompt --target .
# dispatch via your harness if available (Pi subagent tool, Claude Code Agent/Task tool, Codex Shell tool: codex review --uncommitted)
{KIT_COMMAND} review add --backend subagent --reviewer reviewer-fresh-context --rubric core-quality --summary 'Review summary' --target . --json
# review tools may create local agent state; check status again before syncing
{KIT_COMMAND} status --target . --json
{KIT_COMMAND} sync --target . --json
```

Important: `{KIT_COMMAND}` is shell-first. It may capture exact native command evidence via `validate`, but it must not hide validation behind `hk run`-style task-runner commands. Use profile/check guidance to choose native commands, then capture the selected command with `validate --why`.

{profile.instructions}
"""


def print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


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
    json
        Print machine-readable JSON.
    """
    try:
        catalog = resolve_catalog(profiles_dir)
        resolved_target: Path | None = None
        resolved_root: Path | None = None
        if target is not None:
            resolved_target = target.resolve()
            resolved_root = git_root(resolved_target)
    except (RepoStateError, ProfileError) as e:
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
    name="resolve",
    help_epilogue=(
        "Examples:\n"
        "  hk profile resolve --target . --json\n"
        "  HARNESS_KIT_CONFIG=/tmp/harness.toml hk profile resolve --target /work/foreman --json"
    ),
)
def profile_resolve(
    *,
    target: Path = Path("."),
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Resolve the configured profile for a target path.

    Resolution is explicit, not heuristic: user config target bindings are matched
    by longest path prefix, then default_profile/generic fallback applies.
    """
    try:
        catalog = resolve_catalog(profiles_dir)
        resolution = catalog.resolve(target)
    except (KeyError, ProfileError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(resolution_to_json(resolution))
        return
    print(f"Profile: {resolution.profile} [{resolution.source}]")
    print(f"Reason: {resolution.reason}")
    print(f"Target: {resolution.target}")
    if resolution.matched_target:
        print(f"Matched target: {resolution.matched_target}")
    if resolution.config_path:
        print(f"Config: {resolution.config_path}")


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
    if selected.profile.reviews:
        print()
        print("Reviews:")
        for review in selected.profile.reviews:
            print(
                f"- {review.name} [{review.backend}/{review.rubric}]: {review.purpose}"
            )
            if review.dispatch_hint:
                print(f"  dispatch: {review.dispatch_hint}")


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
        "  hk checks --target /work/my-python-package --json\n"
        "  hk checks --profile python --target /work/my-python-package --json\n"
        "  hk checks --profile my-project-api --profiles-dir ~/.config/harness-toolkit/profiles --target /work/repo/my_project/api"
    )
)
def checks(
    *,
    profile: ProfileName | None = None,
    target: Path = Path("."),
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Show named verification checks for a profile without executing them.

    Parameters
    ----------
    profile
        Workflow profile. If omitted, explicit user config target bindings are
        resolved first, then default_profile/generic fallback applies.
    target
        Target repository or scoped path. Used to resolve repo-root guidance.
    profiles_dir
        Optional directory of custom profile TOML files.
    json
        Print machine-readable JSON.
    """
    try:
        catalog = resolve_catalog(profiles_dir)
        resolved_target = target.resolve()
        selected_profile = profile or catalog.resolve(resolved_target).profile
        view = catalog.checks_view(
            selected_profile,
            target=resolved_target,
            repo_root=git_root(resolved_target),
        )
    except (KeyError, ProfileError, RepoStateError) as e:
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
    if view.reviews:
        print()
        print("Reviews:")
        for review in view.reviews:
            print(f"{review.name}: {review.purpose}")
            print(f"  backend: {review.backend}")
            print(f"  rubric: {review.rubric}")
            if review.dispatch_hint:
                print(f"  dispatch: {review.dispatch_hint}")
            if review.prompt:
                print(f"  prompt: {review.prompt}")
            if review.prompt_file:
                print(f"  prompt_file: {review.prompt_file}")


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
    except LocalWorkflowError as e:
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
    """Initialize local or external Harness Kit state for a target."""
    try:
        result = lifecycle_app.init(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"state_dir={result.state_dir}")
    print(f"mode={result.mode}")


@app.command(
    name="start",
    help_epilogue=(
        "Examples:\n"
        "  hk start my-slice --plan 'Adopted implementation intent'\n"
        "  hk start my-slice --context 'Relevant constraint or repo fact' --plan 'Adopted implementation intent'\n"
        "\n"
        "Slug guidance: use a short human-readable task name. HK adds the timestamp/work ID for chronological ordering."
    ),
)
def start(
    slug: str,
    *,
    plan: str = "",
    context: str = "",
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Start a lifecycle work item backed by the local ledger."""
    try:
        result = lifecycle_app.start(
            StartRequest(
                target=target,
                no_local_files=no_local_files,
                slug=slug,
                plan=plan.strip(),
                context=context.strip(),
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"work_id={result.work_id}")
    print(f"work_dir={result.work_dir}")
    if context.strip():
        print(f"context: {context.strip()}")
    if plan.strip():
        print(f"plan: {plan.strip()}")
    print("minimal loop:")
    if not context.strip():
        print(
            "  hk context 'Constraints, relevant files, or repo facts'  # optional, when useful"
        )
    if not plan.strip():
        print("  hk plan 'Adopted implementation intent'")
    print("  hk validate --why 'What this proves' -- <native command>")
    print("  hk status  # follow next actions for decision/review/sync when needed")
    print("  hk ready && hk handoff")


@app.command(
    name="context",
    help_epilogue=(
        "Examples:\n"
        "  hk context 'Relevant constraints, files, or repo facts' --target . --json\n"
        "  hk context --from-file /tmp/context.md --target . --json\n"
        "  printf '%s\\n' 'Rich context with `backticks`' | hk context --from-file - --target . --json"
    ),
)
def context_command(
    text: str = "",
    *,
    from_file: Path | None = None,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record durable context that prevents rediscovery."""
    try:
        if from_file is not None:
            if text:
                raise LocalWorkflowError(
                    "Use either context TEXT or --from-file, not both."
                )
            if str(from_file) == "-":
                text = sys.stdin.read().strip()
            else:
                try:
                    text = from_file.read_text().strip()
                except OSError as e:
                    raise LocalWorkflowError(
                        f"Could not read context file: {from_file}"
                    ) from e
        if not text.strip():
            raise LocalWorkflowError("context requires TEXT or --from-file PATH")
        result = lifecycle_app.note(
            NoteRequest(
                target=target,
                no_local_files=no_local_files,
                kind="context",
                text=text,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"context: {result.text}")


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
        result = lifecycle_app.start(
            StartRequest(target=target, no_local_files=no_local_files, slug=slug)
        )
    except LocalWorkflowError as e:
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
    except LocalWorkflowError as e:
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
        result = lifecycle_app.materialize(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
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
    kind: Literal[
        "context", "plan", "background", "learning", "decision", "gap", "spec-impact"
    ],
    from_file: Path | None = None,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Append an advanced typed lifecycle note/event."""
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
        result = lifecycle_app.note(
            NoteRequest(
                target=target, no_local_files=no_local_files, kind=kind, text=text
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"{result.kind}: {result.text}")


@app.command(
    name="decide",
    help_epilogue=(
        "Examples:\n"
        "  hk decide 'Kept API behavior unchanged' --spec-impact none\n"
        "  hk decide 'Updated lifecycle command shape' --spec-impact updated --spec-ref SPEC.md --spec-ref docs/harness-kit-lifecycle-design.md\n"
        "  hk decide 'Internal refactor only' --spec-impact not-needed"
    ),
)
def decide(
    text: str,
    *,
    spec_impact: Literal["none", "updated", "not-needed"] | None = None,
    spec_ref: tuple[Path, ...] = (),
    no_spec_impact: bool = False,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record a lifecycle decision and its spec reflection."""
    try:
        if not text.strip():
            raise LocalWorkflowError("decide requires TEXT")
        if spec_impact is not None and no_spec_impact:
            raise LocalWorkflowError(
                "Use either --spec-impact or --no-spec-impact, not both."
            )
        if spec_impact is None and not no_spec_impact:
            raise LocalWorkflowError(
                "decide requires --spec-impact none|updated|not-needed or --no-spec-impact"
            )
        result = lifecycle_app.note(
            NoteRequest(
                target=target,
                no_local_files=no_local_files,
                kind="decision",
                text=text,
            )
        )
        refs = [str(path) for path in spec_ref]
        if no_spec_impact:
            impact_mode = "none"
            impact_detail = "No spec impact declared."
        else:
            assert spec_impact is not None
            impact_mode = spec_impact
            impact_detail = {
                "none": "No spec impact declared.",
                "updated": "Spec/docs updated or verified.",
                "not-needed": "Spec/docs update not needed.",
            }[spec_impact]
        ref_text = f"; refs: {', '.join(refs)}" if refs else ""
        impact_text = f"{impact_mode}: {impact_detail}{ref_text}"
        lifecycle_app.note(
            NoteRequest(
                target=target,
                no_local_files=no_local_files,
                kind="spec-impact",
                text=impact_text,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"decision: {result.text}")
    print(f"spec-impact: {impact_text}")


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk sync --target .\n"
        "  hk sync --check --target . --json\n"
        "  hk sync --exclude .pi --reason 'Only local agent session state changed' --target . --json\n"
        "\n"
        "Repeat --exclude for multiple explicit paths. Exclusions are one-shot checkpoint evidence, not persisted ignore config."
    )
)
def sync(
    *,
    target: Path = Path("."),
    check: bool = False,
    exclude: tuple[Path, ...] = (),
    reason: str = "",
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record or check a sync checkpoint for the active work snapshot."""
    try:
        result = lifecycle_app.sync(
            SyncRequest(
                target=target,
                no_local_files=no_local_files,
                check=check,
                exclude_paths=exclude,
                reason=reason,
            )
        )
    except LocalWorkflowError as e:
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
        "  hk validate --why 'Focused regression coverage' -- uv run pytest tests/test_example.py -q\n"
        "  hk validate --why 'Lint and typecheck gate' --shell 'pnpm run lint && pnpm run typecheck'\n"
    )
)
def validate(
    command: tuple[str, ...] = (),
    *,
    why: str,
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
    """Run a native command and record validation evidence with rationale."""
    try:
        if not why.strip():
            raise LocalWorkflowError("validate requires --why TEXT")
        result = lifecycle_app.capture(
            CaptureRequest(
                target=target,
                no_local_files=no_local_files,
                command=command,
                shell_command=shell,
                kind=kind,
                why=why.strip(),
                no_log=no_log,
                raw_log=raw_log,
                stream_to_stderr=json,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print_capture_and_exit(result)
        return
    print(f"evidence_id={result.evidence_id}")
    print(f"status={result.status}")
    print(f"why={result.why}")
    print(f"transcript_path={result.transcript_path}")
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)


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
    """Advanced: run a native command and record exact evidence."""
    try:
        result = lifecycle_app.capture(
            CaptureRequest(
                target=target,
                no_local_files=no_local_files,
                command=command,
                shell_command=shell,
                kind=kind,
                no_log=no_log,
                raw_log=raw_log,
                stream_to_stderr=json,
            )
        )
    except LocalWorkflowError as e:
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


@artifact_app.command(
    name="attach",
    help_epilogue=(
        "Examples:\n"
        "  hk artifact attach --path /tmp/session.jsonl --kind agent-session --target . --json\n"
        "  hk artifact attach --path /tmp/codex-review.md --kind codex-review --label 'Codex review transcript'\n"
        "  hk artifact attach --path /tmp/large.har --kind browser-har --no-copy --redaction external\n"
    ),
)
def artifact_attach(
    *,
    path: Path,
    kind: str,
    label: str = "",
    redaction: Literal["none", "unknown", "external"] = "unknown",
    copy: bool = True,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Attach a harness/tool-produced file to the active Harness Kit work ledger."""
    try:
        result = lifecycle_app.attach_artifact(
            ArtifactAttachRequest(
                target=target,
                no_local_files=no_local_files,
                path=path,
                kind=kind,
                label=label,
                redaction=redaction,
                copy=copy,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"artifact={result.kind}")
    print(f"path={result.artifact_path or result.source_path}")
    print(f"sha256={result.sha256}")


@review_app.command(
    name="add",
    help_epilogue=(
        "Examples:\n"
        "  hk review add --backend subagent --reviewer reviewer-fresh-context --rubric core-quality --summary 'No blocking findings' --target . --json\n"
        "  hk review add --backend codex --reviewer codex-bug-hunter --rubric bug-hunt --summary 'No blocking findings' --target . --json\n\n"
        "Review is required by default. Preferred: independent AI/tool reviewer, ideally different model/runtime/context. Minimum fallback: fresh-context subagent.\n"
        "Implementation-agent self-review does not satisfy readiness. Generate a reviewer prompt with: hk review prompt --target .\n"
        "If available, dispatch that prompt via your harness: Pi subagent tool, Claude Code Agent/Task tool, or Codex Shell tool running `codex review --uncommitted`. Then record with hk review add and re-run hk status because review tools may create agent-local state.\n"
        "If no independent AI/tool or fresh-context review is possible, record the risk explicitly:\n"
        "  hk dangerously-skip review --reason 'no independent/fresh-context reviewer available before handoff' --target . --json"
    ),
)
def review_add(
    *,
    backend: str,
    reviewer: str,
    rubric: tuple[str, ...],
    summary: str,
    disposition: str = "accepted",
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record external-enough review evidence for readiness.

    Do not record your own implementation self-review. Review is required by
    default. Preferred review is an independent AI/tool reviewer, ideally a
    different model/runtime/context; a fresh-context subagent is the minimum
    acceptable fallback. Otherwise use `hk dangerously-skip review --reason ...`.
    """
    try:
        result = lifecycle_app.add_review(
            ReviewRequest(
                target=target,
                no_local_files=no_local_files,
                backend=backend,
                reviewer=reviewer,
                rubrics=rubric,
                summary=summary,
                disposition=disposition,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"review={result.backend}/{result.reviewer}")
    print(f"rubrics={', '.join(result.rubrics)}")
    print(f"summary={result.summary}")


@review_app.command(name="prompt")
def review_prompt_command(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Print a fresh-context reviewer prompt for the active work."""
    try:
        result = lifecycle_app.review_prompt(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.prompt, end="")


@evidence_app.default
def evidence_default(
    *,
    target: Path = Path("."),
    json: bool = False,
) -> None:
    """Show the evidence-list subcommand hint for bare `hk evidence`."""
    message = "hk evidence requires a subcommand. Try: hk evidence list --target <repo> --json"
    if json:
        print(
            json_dump_object(
                {"error": message, "try": "hk evidence list --target <repo> --json"}
            )
        )
    else:
        print_error(message)
    _ = target
    raise SystemExit(1)


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
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    rows = [record.__dict__ for record in records]
    if json:
        print(json_dump_object({"evidence": rows}))
        return
    for record in records:
        why = f" — {record.why}" if record.why else ""
        print(f"{record.id}: {record.status} {record.command_display}{why}")


@app.command(name="ready")
def ready_command(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Check lifecycle handoff readiness."""
    try:
        result = lifecycle_app.ready(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
    else:
        print(result.status)
        for check in result.checks:
            print(f"- {check.id}: {check.status} — {check.message}")
    if not result.ready:
        raise SystemExit(1)


@app.command(
    name="dangerously-skip",
    help_epilogue=(
        "Examples:\n"
        "  hk dangerously-skip review --reason 'docs-only change; no independent reviewer available' --target . --json\n"
        "  hk dangerously-skip sync --reason 'Only .pi agent-local state changed after the last checkpoint' --target . --json\n"
        "\n"
        "Sync skips are tied to the current diff snapshot; run them as one of the final freshness actions."
    ),
)
def ready_dangerously_skip(
    check: Literal["review", "validation", "sync"],
    *,
    reason: str,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record an explicit dangerous skip for a readiness check."""
    try:
        result = lifecycle_app.dangerously_skip(
            DangerousSkipRequest(
                target=target,
                no_local_files=no_local_files,
                check=check,
                reason=reason,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"dangerously-skipped={check}")
    print(f"reason={reason}")


@app.command(name="export")
def export_command(
    *,
    target: Path = Path("."),
    format: Literal["handoff"] = "handoff",
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Export generated lifecycle views from the active ledger."""
    _ = format
    try:
        result = lifecycle_app.materialize(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.path)


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
    format: Literal["markdown", "pr"] = "markdown",
    write: Path | None = None,
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Render a conservative handoff from the active work ledger."""
    try:
        result = lifecycle_app.handoff(
            HandoffRequest(
                target=target,
                no_local_files=no_local_files,
                output_path=write,
                format=format,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
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
        result = lifecycle_app.spec_init(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
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
        result = lifecycle_app.spec_status(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
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
        result = lifecycle_app.spec_outline(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
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
    json: bool = False,
) -> None:
    """Preview promoting a local draft SPEC into the target repo."""
    if not dry_run:
        print_error("spec promote currently requires --dry-run")
        raise SystemExit(1)
    try:
        preview = lifecycle_app.spec_promote_dry_run(
            TargetRequest(target, no_local_files)
        )
        if json:
            print(json_dump_object({"preview": preview}))
            return
        print(preview, end="")
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e


@app.command(
    help_epilogue=(
        "Examples:\n"
        "  hk plan 'Implement lifecycle-first ready checks'\n"
        "  hk plan --from-file /tmp/adopted-plan.md --json\n"
        "  hk start my-slice --plan 'Initial implementation intent'\n"
        "\n"
        "Use `hk plan` to record/refine the lifecycle plan for active Harness Kit work. Use `hk start --plan` to seed the first plan while starting work."
    )
)
def plan(
    text: str = "",
    *,
    from_file: Path | None = None,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record or refine the agreed lifecycle implementation plan."""
    try:
        if from_file is not None:
            if text:
                raise LocalWorkflowError(
                    "Use either plan TEXT or --from-file, not both."
                )
            try:
                text = from_file.read_text().strip()
            except OSError as e:
                raise LocalWorkflowError(
                    f"Could not read plan file: {from_file}"
                ) from e
        if not text:
            raise LocalWorkflowError("plan requires TEXT or --from-file PATH")
        result = lifecycle_app.note(
            NoteRequest(
                target=target, no_local_files=no_local_files, kind="plan", text=text
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"plan: {result.text}")


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
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Show lifecycle work status and next-action guidance for a target repo."""
    try:
        result = lifecycle_app.status(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"active_work={result.active_work or 'none'}")
    print(f"sync_status={result.sync_status}")
    print(f"ready_status={result.ready_status}")
    print(f"phase={result.phase}")
    print(f"state_dir={result.state_dir}")
    print("checks:")
    if result.checks:
        for check in result.checks:
            print(f"- {check.id}: {check.status} — {check.message}")
    else:
        print("- none")
    print("next actions:")
    for action in result.next_actions:
        print(f"- {action}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
