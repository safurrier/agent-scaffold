from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_workflow(*args: str, command: str = "hk") -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", command, *args],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    return env


def _git_init(path: Path) -> None:
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, env=_git_env()
    )
    subprocess.run(
        ["git", "checkout", "-b", "feat/demo"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    (path / "README.md").write_text("# demo\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "chore: initial"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env()
        | {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


def _active_plan(state_dir: Path) -> Path:
    plans = sorted(
        path
        for path in (state_dir / ".ai" / "plans").iterdir()
        if path.is_dir() and path.name.startswith("20")
    )
    assert len(plans) == 1
    return plans[0]


def _git_status(path: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        check=True,
        text=True,
        env=_git_env(),
    ).stdout


def test_workflow_help_includes_agent_copyable_examples() -> None:
    result = _run_workflow("plan", "--help")

    assert result.returncode == 0, result.stderr
    assert "Examples:" in result.stdout
    assert "hk plan investigate-cache-bug" in result.stdout


def test_harness_kit_long_command_is_available() -> None:
    result = _run_workflow("--help", command="harness-kit")

    assert result.returncode == 0, result.stderr
    assert "Usage: harness-kit COMMAND" in result.stdout


def test_legacy_agent_workflow_command_is_not_registered() -> None:
    result = _run_workflow("--help", command="agent-workflow")

    assert result.returncode != 0


def test_workflow_instructions_prints_minimal_agents_snippet() -> None:
    result = _run_workflow("instructions", "--profile", "python", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "python"
    assert "hk profile list --target . --json" in payload["agents_md"]
    assert "hk status --target . --profile python --json" in payload["agents_md"]
    assert "hk checks --target . --profile python --json" in payload["agents_md"]
    assert "hk sync-check --target . --profile python --json" in payload["agents_md"]
    assert "Do not create or commit `.ai/`" in payload["agents_md"]
    assert "does not run validation commands" in payload["agents_md"]


def test_workflow_profiles_and_checks_are_discoverable_without_execution(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)

    state_root = tmp_path / "state"
    profiles = _run_workflow(
        "profile",
        "list",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--json",
    )
    checks = _run_workflow(
        "checks",
        "--profile",
        "python",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--json",
    )

    assert profiles.returncode == 0, profiles.stderr
    profiles_payload = json.loads(profiles.stdout)
    profile_names = {row["name"] for row in profiles_payload["profiles"]}
    assert {"generic", "python", "go", "rust", "rust-mise"} <= profile_names
    assert profiles_payload["target"] == str(target.resolve())
    assert "selection_guidance" in profiles_payload
    assert (
        "Choose the closest available profile yourself"
        in profiles_payload["selection_guidance"]
    )
    assert (
        "Match the profile to the target scope"
        in profiles_payload["selection_guidance"]
    )
    assert "recommended_profile" not in profiles_payload
    assert "recommendations" not in profiles_payload
    assert checks.returncode == 0, checks.stderr
    payload = json.loads(checks.stdout)
    assert payload["profile"] == "python"
    assert payload["target"] == str(target.resolve())
    assert payload["repo_root"] == str(target.resolve())
    focused = payload["checks"][0]
    assert focused["name"] == "tests"
    assert focused["command_template"] == "uv run pytest <test_path_or_selector>"
    assert focused["agent_should_run_directly"] is True
    assert not (target / "uv").exists()
    assert _git_status(target) == ""


def test_workflow_profiles_provide_model_guidance_for_foreman_style_repo(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    (target / "Cargo.toml").write_text('[package]\nname = "demo"\n')
    (target / ".mise.toml").write_text('[tasks.check]\nrun = "cargo check"\n')

    result = _run_workflow("profile", "list", "--target", str(target), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "recommended_profile" not in payload
    assert "recommendations" not in payload
    assert "selection_guidance" in payload
    assert "Rust repo with mise task contract" in payload["selection_guidance"]
    assert (
        "--target crates/tui and no module profile exists, but Cargo.toml exists -> rust"
        in payload["selection_guidance"]
    )
    assert "-> rust-mise" in payload["selection_guidance"]
    assert _git_status(target) == "?? .mise.toml\n?? Cargo.toml\n"

    checks = _run_workflow(
        "checks",
        "--profile",
        "rust-mise",
        "--target",
        str(target),
        "--json",
    )
    assert checks.returncode == 0, checks.stderr
    check_payload = json.loads(checks.stdout)
    assert check_payload["checks"][0]["command_template"] == "mise run check"
    assert check_payload["checks"][0]["run_from"] == "repo-root"


def test_workflow_custom_profile_create_show_and_checks(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    profiles_dir = tmp_path / "profiles"
    output = profiles_dir / "my-project-api.toml"

    create = _run_workflow(
        "profile",
        "create",
        "my-project-api",
        "--target",
        "my_project/api",
        "--preset",
        "python",
        "--output",
        str(output),
        "--json",
    )

    assert create.returncode == 0, create.stderr
    assert output.exists()
    assert json.loads(create.stdout)["profile"] == "my-project-api"

    duplicate = _run_workflow(
        "profile",
        "create",
        "my-project-api",
        "--target",
        "my_project/api",
        "--preset",
        "python",
        "--output",
        str(output),
    )
    assert duplicate.returncode == 1
    assert "already exists" in duplicate.stderr

    listing = _run_workflow(
        "profile", "list", "--profiles-dir", str(profiles_dir), "--json"
    )
    assert listing.returncode == 0, listing.stderr
    listed = json.loads(listing.stdout)
    custom = next(row for row in listed["profiles"] if row["name"] == "my-project-api")
    assert custom["source"] == "file"
    assert custom["path"] == str(output)

    shown = _run_workflow(
        "profile",
        "show",
        "my-project-api",
        "--profiles-dir",
        str(profiles_dir),
        "--json",
    )
    assert shown.returncode == 0, shown.stderr
    shown_payload = json.loads(shown.stdout)
    assert shown_payload["name"] == "my-project-api"
    assert shown_payload["source"] == "file"

    checks = _run_workflow(
        "checks",
        "--profile",
        "my-project-api",
        "--profiles-dir",
        str(profiles_dir),
        "--target",
        str(target),
        "--json",
    )
    assert checks.returncode == 0, checks.stderr
    check_payload = json.loads(checks.stdout)
    assert check_payload["profile"] == "my-project-api"
    assert (
        check_payload["checks"][0]["command_template"]
        == "uv run pytest <test_path_or_selector>"
    )


def test_workflow_profile_create_stdout_and_rust_mise_preset(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)

    result = _run_workflow(
        "profile",
        "create",
        "foreman-root",
        "--target",
        str(target),
        "--preset",
        "rust-mise",
        "--stdout",
    )

    assert result.returncode == 0, result.stderr
    assert 'name = "foreman-root"' in result.stdout
    assert 'command_template = "mise run check"' in result.stdout
    assert (
        'command_template = "hk sync-check --target <target> --profile foreman-root --json"'
        in result.stdout
    )
    assert result.stdout.count('name = "handoff"') == 1
    assert _git_status(target) == ""


def test_workflow_plan_validates_custom_profile_without_profile_scoped_state(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    profiles_dir = tmp_path / "profiles"
    state_root = tmp_path / "state"
    create_profile = _run_workflow(
        "profile",
        "create",
        "my-project-api",
        "--target",
        "my_project/api",
        "--preset",
        "python",
        "--profiles-dir",
        str(profiles_dir),
    )
    assert create_profile.returncode == 0, create_profile.stderr

    result = _run_workflow(
        "plan",
        "custom-profile-plan",
        "--target",
        str(target),
        "--profile",
        "my-project-api",
        "--profiles-dir",
        str(profiles_dir),
        "--state-root",
        str(state_root),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    state_dir = Path(payload["state_dir"])
    assert state_dir.name == "root"
    assert "my-project-api" not in str(state_dir.relative_to(state_root))
    assert _active_plan(state_dir).name.endswith("-custom-profile-plan")
    assert _git_status(target) == ""


def test_workflow_external_plan_keeps_target_repo_clean(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    state_root = tmp_path / "state"

    result = _run_workflow(
        "plan",
        "portable-demo",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--profile",
        "python",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    state_dir = Path(payload["state_dir"])
    assert state_dir.is_relative_to(state_root)
    assert (state_dir / ".ai" / "plans" / "_templates").is_dir()
    assert _active_plan(state_dir).name.endswith("-portable-demo")
    assert _git_status(target) == ""


def test_workflow_target_subdirectory_defines_scope(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    scoped = target / "packages" / "api"
    scoped.mkdir(parents=True)
    state_root = tmp_path / "state"

    result = _run_workflow(
        "attach",
        "--target",
        str(scoped),
        "--state-root",
        str(state_root),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["target_root"] == str(target.resolve())
    assert payload["target_scope"] == str(scoped.resolve())
    assert payload["scope"] == "packages-api"
    state_dir = Path(payload["state_dir"])
    assert state_dir.name == "packages-api"
    assert state_dir.parent.parent == state_root
    assert _git_status(target) == ""


def test_workflow_overlay_attach_updates_local_exclude_only(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)

    result = _run_workflow(
        "attach",
        "--target",
        str(target),
        "--mode",
        "overlay",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ignored_by_local_git"] is True
    state_dir = Path(payload["state_dir"])
    assert state_dir == target / ".ai-local" / "harness-kit" / "root"
    assert (
        "/.ai-local/harness-kit/" in (target / ".git" / "info" / "exclude").read_text()
    )
    assert _git_status(target) == ""


def test_workflow_overlay_attach_works_with_linked_worktree(tmp_path: Path) -> None:
    main_repo = tmp_path / "main"
    main_repo.mkdir()
    _git_init(main_repo)
    worktree = tmp_path / "linked-worktree"
    subprocess.run(
        ["git", "worktree", "add", "-b", "feat/worktree", str(worktree)],
        cwd=main_repo,
        check=True,
        capture_output=True,
        env=_git_env(),
    )

    result = _run_workflow(
        "attach",
        "--target",
        str(worktree),
        "--mode",
        "overlay",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ignored_by_local_git"] is True
    exclude_path = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"],
        cwd=worktree,
        check=True,
        capture_output=True,
        text=True,
        env=_git_env(),
    ).stdout.strip()
    assert "/.ai-local/harness-kit/" in Path(exclude_path).read_text()
    assert _git_status(worktree) == ""


def test_workflow_sync_check_validates_local_plan_without_tracked_artifacts(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    state_root = tmp_path / "state"

    create = _run_workflow(
        "plan",
        "local-check",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--json",
    )
    assert create.returncode == 0, create.stderr
    state_dir = Path(json.loads(create.stdout)["state_dir"])
    plan = _active_plan(state_dir)
    (plan / "TODO.md").write_text("# TODO\n\n- [x] Prove portable workflow\n")
    (plan / "DECISIONS.md").write_text(
        "# Decisions\n\n## What Changed\n\n- Added portable workflow state.\n\n## Why\n\n- Shared repos should stay clean.\n"
    )
    (plan / "VALIDATION.md").write_text(
        "# Validation\n\n```bash\ngit status --porcelain\n```\n"
    )
    (plan / "REVIEW.md").write_text(
        "# Review\n\n- External reviewer found no blockers.\n"
    )

    result = _run_workflow(
        "sync-check",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["plan_dir"] == str(plan)
    assert payload["checks"] == ["plan", "decisions", "validation", "review"]


def test_workflow_sync_check_rejects_placeholder_plan_even_with_validation_command(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    state_root = tmp_path / "state"
    create = _run_workflow(
        "plan",
        "placeholder-check",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--json",
    )
    assert create.returncode == 0, create.stderr
    plan = _active_plan(Path(json.loads(create.stdout)["state_dir"]))
    (plan / "VALIDATION.md").write_text(
        "# Validation\n\n```bash\ngit status --porcelain\n```\n"
    )

    result = _run_workflow(
        "sync-check",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
    )

    assert result.returncode == 1
    assert "TODO.md must contain meaningful checklist items" in result.stderr


def test_workflow_attach_dry_run_does_not_write_state(tmp_path: Path) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)
    state_root = tmp_path / "state"

    result = _run_workflow(
        "attach",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--dry-run",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["state_dir"]).is_relative_to(state_root)
    assert not Path(payload["state_dir"]).exists()
    assert _git_status(target) == ""
