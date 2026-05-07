from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

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
    assert "hk plan" in result.stdout
    assert "hk start my-slice --plan" in result.stdout
    assert "hk legacy" not in result.stdout


def test_root_help_groups_primary_lifecycle_before_advanced_commands() -> None:
    result = _run_workflow("--help")

    assert result.returncode == 0, result.stderr
    assert "1. Primary lifecycle" in result.stdout
    assert "4. Advanced/local state" in result.stdout
    assert result.stdout.index("1. Primary lifecycle") < result.stdout.index(
        "4. Advanced/local state"
    )


def test_help_examples_preserve_short_copyable_command_lines() -> None:
    result = _run_workflow("validate", "--help")

    assert result.returncode == 0, result.stderr
    assert "hk validate --why 'Focused test' -- uv run pytest -q" in result.stdout
    assert "tests/test_example.py" not in result.stdout


def test_harness_kit_long_command_is_available() -> None:
    result = _run_workflow("--help", command="harness-kit")

    assert result.returncode == 0, result.stderr
    assert "Usage: harness-kit COMMAND" in result.stdout


def test_legacy_agent_workflow_command_is_not_registered() -> None:
    result = _run_workflow("--help", command="agent-workflow")

    assert result.returncode != 0


def test_workflow_instructions_default_to_user_level_snippet() -> None:
    result = _run_workflow("instructions", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["scope"] == "user"
    assert "## Harness Kit" in payload["agents_md"]
    assert "hk profile resolve --target . --json" in payload["agents_md"]
    assert "hk start <slug> --plan" in payload["agents_md"]
    assert (
        "do not pass `--profile` or `--profiles-dir` to lifecycle commands"
        in payload["agents_md"]
    )
    assert (
        "https://safurrier.github.io/harness-toolkit/agent-adoption/"
        in payload["agents_md"]
    )
    assert "--profile generic" not in payload["agents_md"]


def test_workflow_instructions_print_repo_profile_snippet() -> None:
    result = _run_workflow(
        "instructions", "--scope", "repo", "--profile", "python", "--json"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["scope"] == "repo"
    assert payload["profile"] == "python"
    assert "hk brief --target . --json" in payload["agents_md"]
    assert (
        "hk start <slug> --plan 'Adopted implementation intent' --target . --json"
        in payload["agents_md"]
    )
    assert "hk status --target . --json" in payload["agents_md"]
    assert "hk checks --target . --profile python --json" in payload["agents_md"]
    assert "hk validate --why" in payload["agents_md"]
    assert "hk ready --target . --json" in payload["agents_md"]
    assert "agent-generated local state as uncommitted" in payload["agents_md"]
    assert "shell-first" in payload["agents_md"]
    assert "Only discovery commands" in payload["agents_md"]
    assert (
        "do not pass `--profile` or `--profiles-dir` to lifecycle commands"
        in payload["agents_md"]
    )


def test_profile_flags_on_lifecycle_commands_get_actionable_error() -> None:
    result = _run_workflow(
        "start",
        "demo",
        "--plan",
        "Adopted implementation intent",
        "--profile",
        "python",
    )

    assert result.returncode == 1
    assert "hk start does not use --profile" in result.stderr
    assert "hk profile resolve --target . --json" in result.stderr
    assert "hk checks --target . --json" in result.stderr
    assert "hk start --help" in result.stderr
    assert "Traceback" not in result.stderr


def test_profile_flag_preflight_does_not_mask_unknown_commands() -> None:
    from harness_toolkit.kit.cli import _profile_option_mistake

    assert _profile_option_mistake(["does-not-exist", "--profile", "python"]) is None


def test_profile_flags_after_validate_separator_are_native_command_args() -> None:
    from harness_toolkit.kit.cli import _profile_option_mistake

    assert (
        _profile_option_mistake(
            [
                "validate",
                "--why",
                "Native command accepts profile",
                "--",
                "tool",
                "--profile",
                "ci",
            ]
        )
        is None
    )


def test_start_retries_resume_active_work_with_same_slug(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)

    first = _run_workflow(
        "start",
        "demo-work",
        "--plan",
        "Adopted implementation intent",
        "--context",
        "Important context",
        "--target",
        str(repo),
        "--json",
    )
    second = _run_workflow(
        "start",
        "demo-work",
        "--plan",
        "Adopted implementation intent",
        "--context",
        "Important context",
        "--target",
        str(repo),
        "--json",
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr
    first_payload = json.loads(first.stdout)
    second_payload = json.loads(second.stdout)
    assert first_payload["work_id"] == second_payload["work_id"]
    assert first_payload["resumed"] is False
    assert second_payload["resumed"] is True
    state_dir = Path(second_payload["state_dir"])
    work_dirs = list((state_dir / "work").iterdir())
    assert len(work_dirs) == 1
    events_path = state_dir / "work" / second_payload["work_id"] / "events.jsonl"
    notes = [
        json.loads(line)
        for line in events_path.read_text().splitlines()
        if line.strip()
    ]
    plan_notes = [
        event
        for event in notes
        if event["type"] == "note_added"
        and event["data"]["kind"] == "plan"
        and event["data"]["text"] == "Adopted implementation intent"
    ]
    context_notes = [
        event
        for event in notes
        if event["type"] == "note_added"
        and event["data"]["kind"] == "context"
        and event["data"]["text"] == "Important context"
    ]
    assert len(plan_notes) == 1
    assert len(context_notes) == 1


def test_workflow_instructions_profile_implies_repo_scope_for_compatibility() -> None:
    result = _run_workflow("instructions", "--profile", "python", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["scope"] == "repo"
    assert payload["profile"] == "python"
    assert "hk checks --target . --profile python --json" in payload["agents_md"]


def test_workflow_instructions_reject_user_scope_with_profile() -> None:
    result = _run_workflow("instructions", "--scope", "user", "--profile", "python")

    assert result.returncode == 1
    assert "--profile/--profiles-dir only apply with --scope repo" in result.stderr


def test_user_harness_config_resolves_inline_profile_and_checks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "foreman"
    repo.mkdir()
    _git_init(repo)
    prompt_file = tmp_path / "foreman-review.md"
    prompt_file.write_text("Review CLI config behavior and focused tests.\n")
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "generic"

[[targets]]
name = "foreman"
path = "{repo}"
profile = "foreman"

[profiles.foreman]
title = "Foreman"
summary = "Rust CLI/TUI project."
target_hint = "Use --target {repo}."
instructions = "Use focused cargo tests and record exact HK evidence."

[[profiles.foreman.checks]]
name = "cli-config-tests"
purpose = "Run CLI config tests."
command_template = "cargo test --test cli_config"
run_from = "repo-root"
notes = ["Use for config behavior changes."]

[[profiles.foreman.reviews]]
name = "core-quality"
purpose = "Fresh-context review before handoff."
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt_file = "{prompt_file.name}"
'''
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    resolved = _run_workflow("profile", "resolve", "--target", str(repo), "--json")
    checks = _run_workflow("checks", "--target", str(repo), "--json")

    assert resolved.returncode == 0, resolved.stderr
    resolution = json.loads(resolved.stdout)
    assert resolution["profile"] == "foreman"
    assert resolution["source"] == "user-config"
    assert resolution["matched_name"] == "foreman"
    assert checks.returncode == 0, checks.stderr
    payload = json.loads(checks.stdout)
    assert payload["profile"] == "foreman"
    assert payload["checks"][0]["command_template"] == "cargo test --test cli_config"
    assert payload["reviews"][0]["backend"] == "codex"
    assert payload["reviews"][0]["dispatch_hint"] == "codex review --uncommitted"
    assert "Review CLI config behavior" in payload["reviews"][0]["prompt_file_text"]


def test_user_harness_config_uses_longest_target_prefix(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    module = repo / "module"
    module.mkdir(parents=True)
    _git_init(repo)
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1

[[targets]]
name = "repo"
path = "{repo}"
profile = "repo-profile"

[[targets]]
name = "module"
path = "{module}"
profile = "module-profile"

[profiles.repo-profile]
title = "Repo"
summary = "Repo profile."
target_hint = "repo"
instructions = "repo instructions"

[[profiles.repo-profile.checks]]
name = "repo-check"
purpose = "Repo check."
command_template = "repo-check"
run_from = "repo-root"

[profiles.module-profile]
title = "Module"
summary = "Module profile."
target_hint = "module"
instructions = "module instructions"

[[profiles.module-profile.checks]]
name = "module-check"
purpose = "Module check."
command_template = "module-check"
run_from = "target"
'''
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_workflow("profile", "resolve", "--target", str(module), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "module-profile"
    assert payload["matched_name"] == "module"


def test_workflow_profiles_and_checks_are_discoverable_without_execution(
    tmp_path: Path,
) -> None:
    target = tmp_path / "target"
    target.mkdir()
    _git_init(target)

    profiles = _run_workflow(
        "profile",
        "list",
        "--target",
        str(target),
        "--json",
    )
    checks = _run_workflow(
        "checks",
        "--profile",
        "python",
        "--target",
        str(target),
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
        'command_template = "hk sync --target <target> --json && hk ready --target <target> --json"'
        in result.stdout
    )
    assert result.stdout.count('name = "handoff-readiness"') == 1
    assert _git_status(target) == ""


def test_workflow_status_reports_missing_target_without_traceback(
    tmp_path: Path,
) -> None:
    result = _run_workflow("status", "--target", str(tmp_path / "missing"))

    assert result.returncode == 1
    assert "target does not exist" in result.stderr
    assert "Traceback" not in result.stderr


def test_workflow_status_reports_file_target_without_traceback(tmp_path: Path) -> None:
    target = tmp_path / "not-a-directory"
    target.write_text("not a checkout")

    result = _run_workflow("status", "--target", str(target))

    assert result.returncode == 1
    assert "target is not a directory" in result.stderr
    assert "Traceback" not in result.stderr
