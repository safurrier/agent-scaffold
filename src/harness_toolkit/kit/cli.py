"""Cyclopts CLI for Harness Kit portable workflow state."""

from __future__ import annotations

import json as json_lib
import shlex
import sys
from pathlib import Path
from typing import Literal

from cyclopts import App, Group

from harness_toolkit.kit.app.lifecycle import (
    ArtifactAttachRequest,
    CaptureRequest,
    DangerousSkipRequest,
    ExportRequest,
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
    brief_markdown,
    json_dump_dataclass,
    json_dump_object,
    print_capture_and_exit,
)
from harness_toolkit.kit.profiles import (
    PROFILE_SELECTION_GUIDANCE,
    ProfileCatalog,
    ProfileError,
    ProfileName,
    checks_to_json,
    profile_template,
    resolution_to_json,
)
from harness_toolkit.kit.state.repo import RepoStateError, git_root
from harness_toolkit.names import KIT_COMMAND


def examples(*commands: str, note: str = "") -> str:
    """Render help examples as a code block so Cyclopts preserves line breaks."""
    body = "\n".join(commands)
    rendered = f"Examples:\n\n```bash\n{body}\n```"
    if note:
        rendered += f"\n\n{note}"
    return rendered


LIFECYCLE_GROUP = Group("1. Primary lifecycle", help="Start here for normal work.")
GUIDANCE_GROUP = Group(
    "2. Guidance and discovery",
    help="Read-only repo, profile, and instruction helpers.",
)
EVIDENCE_GROUP = Group(
    "3. Evidence, review, and handoff", help="Capture proof and finish handoff."
)
ADVANCED_GROUP = Group(
    "4. Advanced/local state", help="Lower-level inspection and local state helpers."
)

# Keep this module as the Cyclopts adapter. If command behavior grows beyond
# argument parsing, output formatting, and error translation, move application
# operations behind a deeper kit module.
app = App(
    name=Path(sys.argv[0]).name,
    help="Use the Harness Kit lifecycle in any repo without committing scaffold files.",
    group_commands=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk start demo-work --plan 'Adopted implementation intent'",
        "hk checks --target . --changed --json",
        "hk status --target .",
        "hk ready --target . && hk summary --target .",
        note="Run `hk instructions` for AGENTS.md guidance and `hk checks --target . --changed --json` for validation hints. Use `hk status` for agent next actions and `hk summary` for a human-readable readiness digest.",
    ),
)
profile_app = App(
    name="profile",
    help="List, show, and create workflow profiles.",
    group=GUIDANCE_GROUP,
)
work_app = App(
    name="work",
    help="Advanced: manage ledger-backed local work units.",
    group=ADVANCED_GROUP,
)
evidence_app = App(
    name="evidence", help="Inspect captured evidence; use `list`.", group=EVIDENCE_GROUP
)
spec_app = App(
    name="spec", help="Manage optional local/external specs.", group=ADVANCED_GROUP
)
review_app = App(
    name="review", help="Record external-enough review evidence.", group=EVIDENCE_GROUP
)
artifact_app = App(
    name="artifact",
    help="Attach external files to active Harness Kit work.",
    group=EVIDENCE_GROUP,
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


def changed_paths_for_target(target: Path) -> tuple[str, ...]:
    return lifecycle_app.changed_paths_for_target(TargetRequest(target))


AGENT_ADOPTION_URL = "https://safurrier.github.io/harness-toolkit/agent-adoption/"
InstructionScope = Literal["user", "repo"]


def user_agents_snippet() -> str:
    return f"""## Harness Kit

For meaningful code changes, use Harness Kit (`{KIT_COMMAND}`) for planning, validation evidence, review, sync, and handoff unless stronger repo-specific instructions supersede it.

Start by resolving the repo/module workflow:

```bash
{KIT_COMMAND} profile resolve --target . --json
```

Use the repo or module that owns the work as `--target`. Profile flags are only for discovery commands such as `{KIT_COMMAND} profile`, `{KIT_COMMAND} checks`, and repo-scope `{KIT_COMMAND} instructions`; do not pass `--profile` or `--profiles-dir` to lifecycle commands unless that command's help shows those options. Then start work with `{KIT_COMMAND} start demo-work --plan "..."`, record validation with `{KIT_COMMAND} validate --why`, and follow `{KIT_COMMAND} status --target .`. Use `{KIT_COMMAND} summary --target .` when a human-readable readiness digest is useful.

If `{KIT_COMMAND}` is unavailable or you are unfamiliar with the workflow, read the Harness Kit agent adoption guide before proceeding:
{AGENT_ADOPTION_URL}
"""


def repo_agents_snippet(
    profile_name: ProfileName, *, profiles_dir: Path | None = None
) -> str:
    catalog = resolve_catalog(profiles_dir)
    profile = catalog.get(profile_name)
    profiles_dir_arg = (
        f" --profiles-dir {shlex.quote(str(profiles_dir))}" if profiles_dir else ""
    )
    return f"""## Portable agent workflow

Use `{KIT_COMMAND}` for meaningful work in this repo or scoped path unless stronger repo-specific instructions supersede it. Treat Harness Kit and agent-generated local state as uncommitted unless the repo instructions or user explicitly say it should be committed.

Profile: `{profile.name}` — {profile.summary}

Standard agent loop:

```bash
{KIT_COMMAND} brief --target . --json
{KIT_COMMAND} start demo-work --plan 'Adopted implementation intent' --target . --json
# work normally in the repo
{KIT_COMMAND} checks --target . --changed --json
{KIT_COMMAND} validate --why 'Fast gate passes' --target . -- mise run check
{KIT_COMMAND} status --target . --json
{KIT_COMMAND} ready --target . --json
{KIT_COMMAND} summary --target .
{KIT_COMMAND} handoff --target .
```

Follow `hk status` next actions when it asks for them:

```bash
# optional context when it prevents rediscovery
{KIT_COMMAND} context 'Relevant constraints, files, or repo facts' --target . --json
{KIT_COMMAND} decide 'Decision/spec reflection' --spec-impact none --target . --json
{KIT_COMMAND} checks --target . --profile {profile.name}{profiles_dir_arg} --changed --json
# review is required by default: preferred independent AI/tool reviewer; minimum fresh-context subagent
{KIT_COMMAND} review prompt core-review --target .
# dispatch via your harness if available (Pi subagent tool, Claude Code Agent/Task tool, Codex Shell tool: codex review --uncommitted)
{KIT_COMMAND} review add --backend subagent --reviewer reviewer-fresh-context --summary 'Review summary' --target . --json
# review tools may create local agent state; check status again before syncing
{KIT_COMMAND} status --target . --json
{KIT_COMMAND} sync --target . --json
```

Important: `{KIT_COMMAND}` is shell-first. It may capture exact native command evidence via `validate`, but it must not hide validation behind `hk run`-style task-runner commands. Use profile/check guidance to choose native commands, then capture the selected command with `validate --why` or `validate --check NAME --why` when satisfying a named profile check. Use `{KIT_COMMAND} status` for next actions and `{KIT_COMMAND} summary` for a human-readable readiness digest. Only discovery commands such as `{KIT_COMMAND} checks`, `{KIT_COMMAND} profile`, and repo-scope `{KIT_COMMAND} instructions` use profile flags; do not pass `--profile` or `--profiles-dir` to lifecycle commands unless that command's help shows those options.

{profile.instructions}
"""


def print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


_PROFILE_ONLY_OPTIONS = {"--profile", "--profiles-dir"}
_PROFILE_OPTION_COMMANDS = {"checks", "instructions", "profile"}
_PROFILE_FORBIDDEN_COMMANDS = {
    "artifact",
    "brief",
    "capture",
    "context",
    "dangerously-skip",
    "decide",
    "evidence",
    "export",
    "handoff",
    "init",
    "note",
    "plan",
    "ready",
    "review",
    "spec",
    "start",
    "status",
    "summary",
    "sync",
    "validate",
    "work",
}


def _argv_before_native_separator(argv: list[str]) -> list[str]:
    """Return HK argv before a native-command `--` separator."""
    if "--" not in argv:
        return argv
    return argv[: argv.index("--")]


def _profile_option_mistake(argv: list[str]) -> tuple[str, str] | None:
    """Detect profile flags on lifecycle commands before Cyclopts' generic error.

    Agents often resolve a profile, then incorrectly copy `--profile` or
    `--profiles-dir` onto lifecycle commands such as `hk start`. Give them a
    one-hop repair hint instead of an unknown-option error. Ignore arguments
    after `--` so native validation commands may use their own profile flags.
    """
    if not argv:
        return None
    command = argv[0]
    if (
        command.startswith("-")
        or command in _PROFILE_OPTION_COMMANDS
        or command not in _PROFILE_FORBIDDEN_COMMANDS
    ):
        return None
    hk_args = _argv_before_native_separator(argv[1:])
    for arg in hk_args:
        option = arg.split("=", 1)[0]
        if option in _PROFILE_ONLY_OPTIONS:
            return command, option
    return None


def _removed_rubric_option_mistake(argv: list[str]) -> bool:
    return len(argv) >= 2 and argv[:2] == ["review", "add"] and "--rubric" in argv[2:]


def _preflight_agent_friendly_errors(argv: list[str]) -> None:
    if _removed_rubric_option_mistake(argv):
        print_error("--rubric was removed from `hk review add`.")
        print(
            "Review criteria now live in profile review instructions, e.g.:",
            file=sys.stderr,
        )
        print("  [reviews.instructions]", file=sys.stderr)
        print('  type = "inline"', file=sys.stderr)
        print(
            '  text = "Review correctness, validation, and handoff clarity."',
            file=sys.stderr,
        )
        print("Try:", file=sys.stderr)
        print(
            f"  {KIT_COMMAND} review add --backend subagent --reviewer reviewer-fresh-context --summary 'Review summary' --target .",
            file=sys.stderr,
        )
        raise SystemExit(1)
    mistake = _profile_option_mistake(argv)
    if mistake is None:
        return
    command, option = mistake
    print_error(
        f"{KIT_COMMAND} {command} does not use {option}. Profile flags are only for "
        f"discovery commands such as `{KIT_COMMAND} profile`, `{KIT_COMMAND} checks`, "
        f"and repo-scope `{KIT_COMMAND} instructions`."
    )
    print("Try:", file=sys.stderr)
    print(f"  {KIT_COMMAND} profile resolve --target . --json", file=sys.stderr)
    print(f"  {KIT_COMMAND} checks --target . --json", file=sys.stderr)
    print(f"  {KIT_COMMAND} {command} --help", file=sys.stderr)
    raise SystemExit(1)


@app.command(
    group=GUIDANCE_GROUP,
    help_epilogue=examples(
        "hk instructions",
        "hk instructions --scope user --json",
        "hk instructions --scope repo --profile python",
        "hk instructions --scope repo --profile api --profiles-dir /tmp/ad-hoc-profiles --json",
        note="Configured profile directories from harness.toml load automatically; use --profiles-dir only for ad hoc repo snippets.",
    ),
)
def instructions(
    *,
    scope: InstructionScope | None = None,
    profile: ProfileName | None = None,
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Print an AGENTS.md snippet for Harness Kit adoption.

    Parameters
    ----------
    scope
        `user` prints the compact durable user-level directive. `repo` prints a
        fuller repo-local snippet with profile-specific guidance. When omitted,
        `--profile` or `--profiles-dir` implies `repo`; otherwise `user`.
    profile
        Workflow profile to include in the repo snippet. Defaults to `generic`
        for repo snippets.
    profiles_dir
        Optional ad hoc directory of custom profile TOML files for repo snippets.
        Directories declared in harness.toml load automatically.
    json
        Print machine-readable JSON with the snippet in `agents_md`.
    """
    if scope == "user" and (profile is not None or profiles_dir is not None):
        print_error("--profile/--profiles-dir only apply with --scope repo")
        raise SystemExit(1)
    effective_scope: InstructionScope = scope or (
        "repo" if profile is not None or profiles_dir is not None else "user"
    )
    effective_profile: ProfileName = profile or "generic"
    try:
        snippet = (
            user_agents_snippet()
            if effective_scope == "user"
            else repo_agents_snippet(effective_profile, profiles_dir=profiles_dir)
        )
    except (KeyError, ProfileError) as e:
        print_error(str(e))
        raise SystemExit(1) from e
    payload = {"agents_md": snippet, "scope": effective_scope}
    if effective_scope == "repo":
        payload["profile"] = effective_profile
    if json:
        print(json_lib.dumps(payload, sort_keys=True))
        return
    print(snippet)


@profile_app.command(
    name="list",
    help_epilogue=examples(
        "hk profile list",
        "hk profile list --target /work/repo --json",
        "hk profile list --profiles-dir /tmp/ad-hoc-profiles --json",
        note="Configured profile directories from harness.toml load automatically; use --profiles-dir only for ad hoc catalogs.",
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
        Optional ad hoc directory of custom profile TOML files. Directories
        declared in harness.toml load automatically.
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
        print_error(f"{e}\nTry: hk profile list --target . --json")
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
    help_epilogue=examples(
        "hk profile resolve --target . --json",
        "HARNESS_KIT_CONFIG=/tmp/h.toml hk profile resolve --target .",
        "hk profile resolve --target . --profiles-dir /tmp/ad-hoc-profiles --json",
        note="Configured profile directories from harness.toml load automatically; use --profiles-dir only for ad hoc catalogs.",
    ),
)
def profile_resolve(
    *,
    target: Path = Path("."),
    profiles_dir: Path | None = None,
    json: bool = False,
) -> None:
    """Resolve the configured profile for a target path.

    Resolution first matches user config target bindings by longest path prefix.
    If no literal path matches, HK maps configured targets across Git linked
    worktrees from the same worktree family and retries the same longest-prefix
    selection. Separate clones are not auto-matched by remote URL.
    Configured profile directories from harness.toml load automatically;
    --profiles-dir is only for ad hoc catalogs.
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
    print(f"Match kind: {resolution.match_kind}")
    print(f"Reason: {resolution.reason}")
    print(f"Target: {resolution.target}")
    if resolution.matched_target:
        print(f"Matched target: {resolution.matched_target}")
    if resolution.worktree_projected_target:
        print(f"Worktree projected target: {resolution.worktree_projected_target}")
    if resolution.worktree_git_common_dir:
        print(f"Worktree common git dir: {resolution.worktree_git_common_dir}")
    if resolution.config_path:
        print(f"Config: {resolution.config_path}")


@profile_app.command(
    name="show",
    help_epilogue=examples(
        "hk profile show python",
        "hk profile show api --json",
        "hk profile show api --profiles-dir /tmp/ad-hoc-profiles --json",
        note="Configured profile directories from harness.toml load automatically; use --profiles-dir only for ad hoc catalogs.",
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
        Optional ad hoc directory of custom profile TOML files. Directories
        declared in harness.toml load automatically.
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
        if check.applies_when:
            print(f"  applies_when: {', '.join(check.applies_when)}")
        if check.required_when:
            print(f"  required_when: {', '.join(check.required_when)}")
    if selected.profile.reviews:
        print()
        print("Reviews:")
        for review in selected.profile.reviews:
            print(f"- {review.name} [{review.backend}]: {review.purpose}")
            if review.dispatch_hint:
                print(f"  dispatch: {review.dispatch_hint}")
            if review.instructions is not None:
                if review.instructions.type == "file":
                    print(f"  instructions: file {review.instructions.path}")
                else:
                    print("  instructions: inline")
            if review.applies_when:
                print(f"  applies_when: {', '.join(review.applies_when)}")
            if review.required_when:
                print(f"  required_when: {', '.join(review.required_when)}")


@profile_app.command(
    name="create",
    help_epilogue=examples(
        "hk profile create api --target api --preset python --output /tmp/api.toml",
        "hk profile create foreman --target . --preset rust-mise --stdout",
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
        content = profile_template(name, target=target, preset=preset)
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
    print("  2. If this directory is declared in harness.toml, run:")
    print(f"     hk profile show {name} --json")
    print(f"     hk checks --target {target} --profile {name} --json")
    print("  3. Otherwise inspect it as an ad hoc catalog:")
    print(f"     hk profile show {name} --profiles-dir {destination.parent} --json")
    print(
        f"     hk checks --target {target} --profile {name} --profiles-dir {destination.parent} --json"
    )


@app.command(
    group=GUIDANCE_GROUP,
    help_epilogue=examples(
        "hk checks --target /work/my-python-package --json",
        "hk checks --target . --changed --json",
        "hk checks --profile api --target api --json",
        "hk checks --profile api --profiles-dir /tmp/ad-hoc-profiles --target api --json",
        note="Path rules match repo-root paths and, for subdirectory targets, target-relative paths; output stays repo-root-relative. Configured profile directories from harness.toml load automatically.",
    ),
)
def checks(
    *,
    profile: ProfileName | None = None,
    target: Path = Path("."),
    profiles_dir: Path | None = None,
    changed: bool = False,
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
        Optional ad hoc directory of custom profile TOML files. Directories
        declared in harness.toml load automatically.
    changed
        Include diff-based suggestions using profile applies_when/required_when
        rules. Rules match repo-root paths and, for subdirectory targets,
        target-relative paths; matched output stays repo-root-relative.
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
            changed_paths=changed_paths_for_target(resolved_target) if changed else (),
            enforce_required=profile is None and profiles_dir is None,
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
    if changed:
        print()
        print("Changed paths:")
        for path in view.changed_paths or ("none",):
            print(f"- {path}")
        print()
        print("Suggested checks:")
        if view.suggested_checks:
            for item in view.suggested_checks:
                required = "required" if item.required else "suggested"
                if item.required and not item.enforced:
                    required = "required by inspected profile"
                print(f"- {item.name} ({required}): {item.purpose}")
                print(
                    f"  reason: {item.matched_by} matched {', '.join(item.matched_paths)}"
                )
                if item.matched_patterns:
                    print(f"  patterns: {', '.join(item.matched_patterns)}")
                if item.record_command:
                    print(f"  record: {item.record_command}")
        else:
            print("- none")
        print()
        print("Suggested reviews:")
        if view.suggested_reviews:
            for item in view.suggested_reviews:
                required = "required" if item.required else "suggested"
                if item.required and not item.enforced:
                    required = "required by inspected profile"
                print(f"- {item.name} ({required}): {item.purpose}")
                print(
                    f"  reason: {item.matched_by} matched {', '.join(item.matched_paths)}"
                )
                if item.matched_patterns:
                    print(f"  patterns: {', '.join(item.matched_patterns)}")
                if item.dispatch_hint:
                    print(f"  hint: {item.dispatch_hint}")
                if item.prompt_command:
                    print(f"  prompt: {item.prompt_command}")
                if item.record_command:
                    print(f"  record: {item.record_command}")
        else:
            print("- none")
    print()
    for check in view.checks:
        print(f"{check.name}: {check.purpose}")
        print(f"  command: {check.command_template}")
        print(f"  run from: {check.run_from}")
        if check.required_inputs:
            print(f"  inputs: {', '.join(check.required_inputs)}")
        if check.applies_when:
            print(f"  applies_when: {', '.join(check.applies_when)}")
        if check.required_when:
            print(f"  required_when: {', '.join(check.required_when)}")
    if view.reviews:
        print()
        print("Reviews:")
        for review in view.reviews:
            print(f"{review.name}: {review.purpose}")
            print(f"  backend: {review.backend}")
            if review.dispatch_hint:
                print(f"  dispatch: {review.dispatch_hint}")
            if review.instructions is not None:
                if review.instructions.type == "file":
                    print(f"  instructions: file {review.instructions.path}")
                else:
                    print("  instructions: inline")
            if review.applies_when:
                print(f"  applies_when: {', '.join(review.applies_when)}")
            if review.required_when:
                print(f"  required_when: {', '.join(review.required_when)}")


@app.command(
    group=GUIDANCE_GROUP,
    help_epilogue=examples("hk brief --target .", "hk brief --target . --json"),
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
        result = lifecycle_app.brief(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(brief_markdown(result), end="")


@app.command(
    name="init",
    group=ADVANCED_GROUP,
    help_epilogue=examples(
        "hk init --target . --json",
        "hk init --target . --no-local-files --json",
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk start my-slice --plan 'Adopted implementation intent'",
        "hk start my-slice --context 'Constraint' --plan 'Intent'",
        note="Slug guidance: use a short human-readable task name. If the active work already has the same slug, `hk start` resumes it instead of creating duplicate retry state.",
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
    if result.resumed:
        print("resumed=true")
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
    print("  hk validate --why 'Fast gate passes' -- mise run check")
    print("  hk status  # follow next actions for decision/review/sync when needed")
    print("  hk ready && hk handoff")


@app.command(
    name="context",
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk context 'Relevant constraints, files, or repo facts' --target . --json",
        "hk context --from-file /tmp/context.md --target . --json",
        "printf 'Context\\n' | hk context --from-file - --target . --json",
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


@work_app.command(
    name="start",
    help_epilogue=examples(
        "hk work start experiment --target . --json",
        note="Advanced compatibility surface. Prefer `hk start demo-work --plan ...` for normal lifecycle work.",
    ),
)
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
    if result.resumed:
        print("resumed=true")


@work_app.command(
    name="status",
    help_epilogue=examples(
        "hk work status --target .", "hk work status --target . --json"
    ),
)
def work_status(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Show active local work status."""
    try:
        result = lifecycle_app.brief(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"active_work={result.active_work or 'none'}")
    print(f"sync_status={result.sync_status}")


@work_app.command(
    name="materialize",
    help_epilogue=examples("hk work materialize --target . --json"),
)
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
    group=ADVANCED_GROUP,
    help_epilogue=examples(
        "hk note --kind plan 'Implement the agreed sync/readiness docs update'",
        "hk note --kind learning 'Auth timeout is owned by session refresh'",
        "hk note --kind gap 'Full suite not run' --json",
        "hk note --kind plan --from-file /tmp/plan-summary.md",
    ),
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk decide 'Kept API behavior unchanged' --spec-impact none",
        "hk decide 'Updated CLI' --spec-impact updated --spec-ref SPEC.md",
        "hk decide 'Internal refactor only' --spec-impact not-needed",
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk sync --target .",
        "hk sync --check --target . --json",
        "hk sync --exclude .pi --reason agent-local --json",
        note="Repeat --exclude for multiple explicit paths. Exclusions are one-shot checkpoint evidence, not persisted ignore config.",
    ),
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk validate --why 'Focused test' -- uv run pytest -q",
        "hk validate --why 'Env-specific test' -- env PYTHONPATH=src pytest -q",
        "hk validate --check repo-native-fast-gate --why 'Fast gate' -- mise run check",
    ),
)
def validate(
    command: tuple[str, ...] = (),
    *,
    why: str,
    target: Path = Path("."),
    kind: Literal[
        "test", "lint", "typecheck", "build", "check", "e2e", "other"
    ] = "other",
    check: str = "",
    shell: str = "",
    no_log: bool = False,
    raw_log: bool = False,
    timeout_seconds: int = 0,
    max_log_bytes: int = 0,
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
                check_name=check,
                no_log=no_log,
                raw_log=raw_log,
                stream_to_stderr=json,
                timeout_seconds=timeout_seconds,
                max_log_bytes=max_log_bytes,
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
    if result.check_name:
        print(f"check={result.check_name}")
    print(f"transcript_path={result.transcript_path}")
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)


@app.command(
    group=ADVANCED_GROUP,
    help_epilogue=examples(
        "hk capture --kind test -- uv run pytest -q",
        "hk capture --shell 'pnpm lint && pnpm typecheck'",
    ),
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
    timeout_seconds: int = 0,
    max_log_bytes: int = 0,
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
                timeout_seconds=timeout_seconds,
                max_log_bytes=max_log_bytes,
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
    name="list",
    help_epilogue=examples(
        "hk artifact list --target .",
        "hk artifact list --target . --json",
    ),
)
def artifact_list(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """List attached harness/tool-produced files for the active work."""
    try:
        result = lifecycle_app.artifact_records(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    if not result.work_id:
        print(
            "No active HK work. Try: hk start demo-work --plan '...'", file=sys.stderr
        )
        return
    if not result.artifacts:
        print("No artifacts attached.")
        return
    for artifact in result.artifacts:
        label = f" — {artifact.label}" if artifact.label else ""
        copied = "copied" if artifact.copied else "referenced"
        path = artifact.artifact_path or artifact.source_path
        print(
            f"{artifact.seq}: {artifact.kind} ({copied}, {artifact.redaction}, "
            f"{artifact.size_bytes} bytes, {artifact.sha256}) `{path}`{label}"
        )


@artifact_app.command(
    name="attach",
    help_epilogue=examples(
        "hk artifact attach --path /tmp/session.jsonl --kind agent-session --json",
        "hk artifact attach --path /tmp/review.md --kind codex-review --label review --redaction external",
        "hk artifact attach --path /tmp/large.har --kind browser-har --no-copy",
        "hk artifact list --target . --json",
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
    help_epilogue=examples(
        "hk review add --review cli-review --backend subagent --reviewer fresh --summary OK",
        "hk review add --backend codex --reviewer bug-hunter --summary OK",
        "hk review add --review cli-review --path src/cli.py --backend subagent --reviewer fresh --summary OK",
        "hk dangerously-skip review --label no-review --reason unavailable --mitigation follow-up --json",
        note=(
            "Review is required by default. Preferred: independent AI/tool reviewer.\n"
            "Minimum fallback: fresh-context subagent, e.g. reviewer-fresh-context.\n"
            "Implementation-agent self-review does not satisfy readiness.\n"
            "Generate a prompt with `hk review prompt --target .`, dispatch it, then record with `hk review add` and re-run `hk status`."
        ),
    ),
)
def review_add(
    *,
    backend: str,
    reviewer: str,
    summary: str,
    disposition: str = "accepted",
    review: str = "",
    path: tuple[str, ...] = (),
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Record external-enough review evidence for readiness.

    Do not record your own implementation self-review. Review is required by
    default. Preferred review is an independent AI/tool reviewer, ideally a
    different model/runtime/context; a fresh-context subagent is the minimum
    acceptable fallback. Otherwise use `hk dangerously-skip review --label ... --reason ... --mitigation ...`.
    """
    try:
        result = lifecycle_app.add_review(
            ReviewRequest(
                target=target,
                no_local_files=no_local_files,
                backend=backend,
                reviewer=reviewer,
                summary=summary,
                disposition=disposition,
                review_name=review,
                reviewed_paths=path,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"review={result.backend}/{result.reviewer}")
    if result.review_name:
        print(f"profile_review={result.review_name}")
    if result.reviewed_paths:
        print(f"reviewed_paths={', '.join(result.reviewed_paths)}")
    print(f"summary={result.summary}")


@review_app.command(
    name="prompt",
    help_epilogue=examples(
        "hk review prompt --target .",
        "hk review prompt cli-review --target .",
        "hk review prompt cli-review --target . --json",
    ),
)
def review_prompt_command(
    name: str = "",
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Print a fresh-context reviewer prompt for the active work."""
    try:
        result = lifecycle_app.review_prompt(
            TargetRequest(target, no_local_files), review_name=name
        )
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
    message = (
        "hk evidence requires a subcommand. Try: hk evidence list --target . --json"
    )
    if json:
        print(
            json_dump_object(
                {"error": message, "try": "hk evidence list --target . --json"}
            )
        )
    else:
        print_error(message)
    _ = target
    raise SystemExit(1)


@evidence_app.command(
    name="list",
    help_epilogue=examples(
        "hk evidence list --target .",
        "hk evidence list --target . --json",
    ),
)
def evidence_list(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """List captured evidence for the active work unit."""
    try:
        records = lifecycle_app.evidence_records(TargetRequest(target, no_local_files))
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


@app.command(
    name="ready",
    group=LIFECYCLE_GROUP,
    help_epilogue=examples("hk ready --target .", "hk ready --target . --json"),
)
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk dangerously-skip validation --label docker-e2e --reason unavailable --mitigation CI-covers-it",
        "hk dangerously-skip sync --label agent-state --reason local-only --mitigation no-source-change",
        note="Sync skips are tied to the current diff snapshot; run them as one of the final freshness actions.",
    ),
)
def ready_dangerously_skip(
    check: Literal["review", "validation", "sync"],
    *,
    label: str,
    reason: str,
    mitigation: str,
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
                label=label,
                reason=reason,
                mitigation=mitigation,
            )
        )
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(f"dangerously-skipped={check}")
    print(f"label={label}")
    print(f"reason={reason}")
    print(f"mitigation={mitigation}")


@app.command(
    name="summary",
    group=EVIDENCE_GROUP,
    help_epilogue=examples(
        "hk summary --target .",
        "hk summary --target . --json",
        note="Use `hk status` for agent next actions; use `hk summary` for a human-readable readiness digest suitable for PRs or review handoff.",
    ),
)
def summary(
    *,
    target: Path = Path("."),
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Render a concise human-readable readiness digest."""
    try:
        result = lifecycle_app.summary(TargetRequest(target, no_local_files))
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.content, end="")


@app.command(
    name="export",
    group=EVIDENCE_GROUP,
    help_epilogue=examples(
        "hk export --target .",
        "hk export --format handoff-dir --output .ai/hk/2026-05-09-120000-demo --target .",
        "hk export --format handoff-dir --output .ai/hk/2026-05-09-120000-demo --check --target .",
    ),
)
def export_command(
    *,
    target: Path = Path("."),
    format: Literal["handoff", "handoff-dir"] = "handoff",
    output: Path | None = None,
    check: bool = False,
    no_local_files: bool = False,
    json: bool = False,
) -> None:
    """Export generated lifecycle views from the active ledger."""
    if format == "handoff" and (output is not None or check):
        print_error(
            "hk export --output/--check require --format handoff-dir\n"
            "Try: hk export --format handoff-dir --output .ai/hk/2026-05-09-120000-demo --target ."
        )
        raise SystemExit(1)
    request = ExportRequest(
        target=target,
        no_local_files=no_local_files,
        format=format,
        output_path=output,
        check=check,
    )
    if format == "handoff-dir" and check and json:
        try:
            status_result = lifecycle_app.export_status(request)
        except LocalWorkflowError as e:
            print_error(str(e))
            raise SystemExit(1) from e
        print(json_dump_dataclass(status_result))
        if not status_result.fresh:
            raise SystemExit(1)
        return
    try:
        result = lifecycle_app.export(request)
    except LocalWorkflowError as e:
        print_error(str(e))
        raise SystemExit(1) from e
    if json:
        print(json_dump_dataclass(result))
        return
    print(result.path)


@app.command(
    group=EVIDENCE_GROUP,
    help_epilogue=examples(
        "hk handoff --format markdown",
        "hk handoff --format pr --write /tmp/handoff.md",
    ),
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


@spec_app.command(
    name="init",
    help_epilogue=examples("hk spec init --target . --json"),
)
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


@spec_app.command(
    name="status",
    help_epilogue=examples(
        "hk spec status --target .", "hk spec status --target . --json"
    ),
)
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


@spec_app.command(
    name="outline",
    help_epilogue=examples(
        "hk spec outline --target .", "hk spec outline --target . --json"
    ),
)
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


@spec_app.command(
    name="promote",
    help_epilogue=examples(
        "hk spec promote --dry-run --target .",
        "hk spec promote --dry-run --target . --json",
    ),
)
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk plan 'Implement lifecycle-first ready checks'",
        "hk plan --from-file /tmp/adopted-plan.md --json",
        "hk start my-slice --plan 'Initial implementation intent'",
        note="Use `hk plan` to record/refine the lifecycle plan for active Harness Kit work. Use `hk start --plan` to seed the first plan while starting work.",
    ),
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
    group=LIFECYCLE_GROUP,
    help_epilogue=examples(
        "hk status --target /work/repo",
        "hk status --target /work/repo --json",
    ),
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
    if result.suggested_checks or result.suggested_reviews:
        print("optional profile suggestions:")
        if result.suggested_checks:
            for item in result.suggested_checks:
                print(f"- check: {item.name} — {item.purpose}")
                print(
                    f"  because: {item.matched_by} matched {', '.join(item.matched_paths)}"
                )
                if item.matched_patterns:
                    print(f"  patterns: {', '.join(item.matched_patterns)}")
                if item.record_command:
                    print(f"  record: {item.record_command}")
        if result.suggested_reviews:
            for item in result.suggested_reviews:
                print(f"- review: {item.name} — {item.purpose}")
                print(
                    f"  because: {item.matched_by} matched {', '.join(item.matched_paths)}"
                )
                if item.dispatch_hint:
                    print(f"  hint: {item.dispatch_hint}")
                if item.matched_patterns:
                    print(f"  patterns: {', '.join(item.matched_patterns)}")
                if item.prompt_command:
                    print(f"  prompt: {item.prompt_command}")
                if item.record_command:
                    print(f"  record: {item.record_command}")
        print(
            "  note: these suggestions are not readiness blockers; required items appear in checks/next actions."
        )
    print("next actions:")
    for action in result.next_actions:
        print(f"- {action}")


def main() -> None:
    _preflight_agent_friendly_errors(sys.argv[1:])
    app()


if __name__ == "__main__":
    main()
