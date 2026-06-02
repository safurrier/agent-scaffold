from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.cli


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


def _write_profile_config(tmp_path: Path, repo: Path) -> Path:
    prompt = tmp_path / "agent-friendly-cli-review.md"
    prompt.write_text(
        "Review CLI changes for non-interactive defaults, JSON output, "
        "idempotency, actionable errors, and copyable help examples.\n"
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "hk-dogfood"

[[targets]]
name = "repo"
path = "{repo}"
profile = "hk-dogfood"

[profiles.hk-dogfood]
title = "HK dogfood"
summary = "Dogfood profile with command-specific guidance."
target_hint = "Use --target {repo}."
instructions = "Run native commands and record HK evidence."

[[profiles.hk-dogfood.checks]]
name = "unit-tests"
purpose = "Run focused unit tests for command behavior."
command_template = "uv run pytest tests/unit/test_portable_workflow.py -q"
run_from = "repo-root"
applies_when = ["src/**/cli.py"]
required_when = ["src/**/cli.py", "!src/**/generated/**"]

[[profiles.hk-dogfood.reviews]]
name = "agent-friendly-cli-review"
purpose = "Review CLI changes against agent-facing CLI design principles."
backend = "fresh-context-subagent"
dispatch_hint = "Use a fresh-context reviewer."
applies_when = ["src/**/cli.py", "docs/**"]
required_when = ["src/**/cli.py"]

[profiles.hk-dogfood.reviews.instructions]
type = "file"
path = "{prompt}"
'''.lstrip()
    )
    return config


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
    assert "hk start demo-work --plan" in payload["agents_md"]
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
        "hk start demo-work --plan 'Adopted implementation intent' --target . --json"
        in payload["agents_md"]
    )
    assert "hk status --target . --json" in payload["agents_md"]
    assert (
        "hk checks --target . --profile python --changed --json" in payload["agents_md"]
    )
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


def test_review_add_removed_rubric_flag_has_repair_hint() -> None:
    result = _run_workflow(
        "review",
        "add",
        "--backend",
        "subagent",
        "--reviewer",
        "fresh",
        "--rubric",
        "core",
        "--summary",
        "OK",
        "--target",
        ".",
    )

    assert result.returncode == 1
    assert "--rubric was removed" in result.stderr
    assert "[reviews.instructions]" in result.stderr
    assert "hk review add --backend subagent" in result.stderr


def test_profile_applicability_uses_gitignore_style_patterns() -> None:
    from harness_toolkit.kit.profiles import _matches_pattern

    assert _matches_pattern("README.md", "*.md") is True
    assert _matches_pattern("docs/explanation/portable-workflow.md", "*.md") is True
    assert _matches_pattern("README.md", "/*.md") is True
    assert _matches_pattern("docs/explanation/portable-workflow.md", "/*.md") is False
    assert _matches_pattern("docs/explanation/portable-workflow.md", "docs/**") is True
    assert _matches_pattern(".github/workflows/ci.yml", "github/**") is False
    assert _matches_pattern(".github/workflows/ci.yml", ".github/**") is True


def test_profile_applicability_supports_gitignore_negation() -> None:
    from harness_toolkit.kit.profiles import _matched_paths

    assert _matched_paths(
        ("src/**/cli.py", "!src/**/generated/**"),
        ("src/demo/cli.py", "src/demo/generated/cli.py"),
    ) == ("src/demo/cli.py",)


def test_profile_applicability_negation_can_mix_root_and_target_relative_paths() -> (
    None
):
    from harness_toolkit.kit.profiles import _matched_paths

    target = Path("/tmp/repo/discord_cap")
    repo_root = Path("/tmp/repo")

    assert _matched_paths(
        ("discord_cap/cap/**", "!cap/generated/**"),
        ("discord_cap/cap/generated/bot.py", "discord_cap/cap/bot.py"),
        target=target,
        repo_root=repo_root,
    ) == ("discord_cap/cap/bot.py",)
    assert _matched_paths(
        ("cap/**", "!discord_cap/cap/generated/**"),
        ("discord_cap/cap/generated/bot.py", "discord_cap/cap/bot.py"),
        target=target,
        repo_root=repo_root,
    ) == ("discord_cap/cap/bot.py",)


def test_checks_changed_suggests_applicable_profile_items(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src" / "harness_toolkit" / "kit").mkdir(parents=True)
    (repo / "src" / "harness_toolkit" / "kit" / "cli.py").write_text(
        "print('changed')\n"
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_profile_config(tmp_path, repo)))

    result = _run_workflow("checks", "--target", str(repo), "--changed", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_paths"] == ["src/harness_toolkit/kit/cli.py"]
    assert payload["suggested_checks"][0]["name"] == "unit-tests"
    assert payload["suggested_checks"][0]["required"] is True
    assert payload["suggested_checks"][0]["enforced"] is True
    assert payload["suggested_checks"][0]["matched_patterns"] == ["src/**/cli.py"]
    assert (
        "hk validate --check unit-tests"
        in payload["suggested_checks"][0]["record_command"]
    )
    assert payload["suggested_reviews"][0]["name"] == "agent-friendly-cli-review"
    assert payload["suggested_reviews"][0]["required"] is True
    assert payload["suggested_reviews"][0]["enforced"] is True
    assert payload["suggested_reviews"][0]["matched_patterns"] == ["src/**/cli.py"]
    assert (
        "hk review prompt agent-friendly-cli-review"
        in payload["suggested_reviews"][0]["prompt_command"]
    )
    assert "Review CLI changes for non-interactive defaults" not in json.dumps(payload)
    assert "Review CLI changes for non-interactive defaults" not in result.stdout

    inspected = _run_workflow(
        "checks",
        "--profile",
        "hk-dogfood",
        "--target",
        str(repo),
        "--changed",
        "--json",
    )
    inspected_payload = json.loads(inspected.stdout)
    assert inspected_payload["suggested_checks"][0]["required"] is True
    assert inspected_payload["suggested_checks"][0]["enforced"] is False


def test_status_surfaces_optional_profile_review_suggestions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_profile_config(tmp_path, repo)))
    assert (
        _run_workflow(
            "start",
            "docs-review-suggestion",
            "--plan",
            "Touch docs and surface optional review suggestions.",
            "--target",
            str(repo),
        ).returncode
        == 0
    )
    (repo / "docs").mkdir()
    (repo / "docs" / "guide.md").write_text("# guide\n")

    result = _run_workflow("status", "--target", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["suggested_reviews"][0]["name"] == "agent-friendly-cli-review"
    assert payload["suggested_reviews"][0]["required"] is False
    assert (
        payload["suggested_reviews"][0]["dispatch_hint"]
        == "Use a fresh-context reviewer."
    )
    assert payload["suggested_reviews"][0]["prompt_command"].startswith(
        "hk review prompt agent-friendly-cli-review"
    )
    assert payload["ready_status"] == "not-ready"

    text = _run_workflow("status", "--target", str(repo))
    assert "optional profile suggestions:" in text.stdout
    assert "review: agent-friendly-cli-review" in text.stdout
    assert "not readiness blockers" in text.stdout


def test_named_profile_review_prompt_uses_file_instructions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_profile_config(tmp_path, repo)))
    assert (
        _run_workflow(
            "start",
            "cli-review",
            "--plan",
            "Touch CLI command behavior.",
            "--target",
            str(repo),
        ).returncode
        == 0
    )
    (repo / "src" / "harness_toolkit" / "kit").mkdir(parents=True)
    (repo / "src" / "harness_toolkit" / "kit" / "cli.py").write_text(
        "print('changed')\n"
    )

    result = _run_workflow(
        "review",
        "prompt",
        "agent-friendly-cli-review",
        "--target",
        str(repo),
    )

    assert result.returncode == 0, result.stderr
    assert "Profile review: agent-friendly-cli-review" in result.stdout
    assert "Review CLI changes for non-interactive defaults" in result.stdout
    assert "hk review add --review agent-friendly-cli-review" in result.stdout
    assert "src/harness_toolkit/kit/cli.py" in result.stdout


def test_user_harness_config_loads_profiles_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "repo-profile.toml").write_text(
        f"""
name = "repo-profile"
title = "Repo Profile"
summary = "Profile loaded from a configured directory."
target_hint = "Use --target {repo}."
instructions = "Run native commands and record HK evidence."

[[checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "pytest -q"
run_from = "repo-root"
""".lstrip()
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
profiles_dir = "profiles"

[[targets]]
name = "repo"
path = "{repo}"
profile = "repo-profile"
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    resolved = _run_workflow("profile", "resolve", "--target", str(repo), "--json")
    checks = _run_workflow("checks", "--target", str(repo), "--json")

    assert resolved.returncode == 0, resolved.stderr
    assert json.loads(resolved.stdout)["profile"] == "repo-profile"
    assert checks.returncode == 0, checks.stderr
    payload = json.loads(checks.stdout)
    assert payload["profile"] == "repo-profile"
    assert payload["checks"][0]["command_template"] == "pytest -q"


def test_configured_profiles_dir_errors_are_actionable_but_create_still_works(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    missing = tmp_path / "missing-profiles"
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
profiles_dir = "{missing}"
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    listed = _run_workflow("profile", "list", "--json")
    created = _run_workflow(
        "profile",
        "create",
        "demo-profile",
        "--target",
        str(repo),
        "--stdout",
    )

    assert listed.returncode == 1
    assert "profiles directory does not exist" in listed.stderr
    assert f"configured in {config}" in listed.stderr
    assert "Try: mkdir -p" in listed.stderr
    assert created.returncode == 0, created.stderr
    assert 'name = "demo-profile"' in created.stdout


def test_configured_profiles_dirs_and_cli_profiles_dir_precedence(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    config_dir = tmp_path / "config-profiles"
    cli_dir = tmp_path / "cli-profiles"
    config_dir.mkdir()
    cli_dir.mkdir()
    profile_template_text = """
name = "repo-profile"
title = "Repo Profile"
summary = "Profile loaded from {source}."
target_hint = "Use --target {repo}."
instructions = "Run native commands and record HK evidence."

[[checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "{command}"
run_from = "repo-root"
"""
    (config_dir / "repo-profile.toml").write_text(
        profile_template_text.format(
            source="configured dir", repo=repo, command="pytest from-config-dir"
        ).lstrip()
    )
    (cli_dir / "repo-profile.toml").write_text(
        profile_template_text.format(
            source="cli dir", repo=repo, command="pytest from-cli-dir"
        ).lstrip()
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
profiles_dirs = ["{config_dir}"]

[[targets]]
name = "repo"
path = "{repo}"
profile = "repo-profile"

[profiles.repo-profile]
title = "Inline Repo Profile"
summary = "Inline profile."
target_hint = "Use --target {repo}."
instructions = "Run native commands and record HK evidence."

[[profiles.repo-profile.checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "pytest from-inline"
run_from = "repo-root"
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    configured = _run_workflow("checks", "--target", str(repo), "--json")
    ad_hoc = _run_workflow(
        "checks",
        "--target",
        str(repo),
        "--profiles-dir",
        str(cli_dir),
        "--json",
    )

    assert configured.returncode == 0, configured.stderr
    assert json.loads(configured.stdout)["checks"][0]["command_template"] == (
        "pytest from-config-dir"
    )
    assert ad_hoc.returncode == 0, ad_hoc.stderr
    assert json.loads(ad_hoc.stdout)["checks"][0]["command_template"] == (
        "pytest from-cli-dir"
    )


def test_changed_path_rules_accept_target_relative_patterns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "monorepo"
    repo.mkdir()
    _git_init(repo)
    target = repo / "discord_cap"
    (target / "cap").mkdir(parents=True)
    (target / "cap" / "bot.py").write_text("print('changed')\n")
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1

[[targets]]
name = "cap"
path = "{target}"
profile = "cap-profile"

[profiles.cap-profile]
title = "Cap"
summary = "Subdirectory target profile."
target_hint = "Use --target {target}."
instructions = "Run target checks."

[[profiles.cap-profile.checks]]
name = "target-relative"
purpose = "Check target-relative changed path matching."
command_template = "uv run pytest"
run_from = "target"
required_when = ["cap/**"]

[[profiles.cap-profile.reviews]]
name = "target-relative-review"
purpose = "Review target-relative changed path matching."
backend = "fresh-context-subagent"
applies_when = ["cap/**"]
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_workflow("checks", "--target", str(target), "--changed", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["changed_paths"] == ["discord_cap/cap/bot.py"]
    assert payload["suggested_checks"][0]["name"] == "target-relative"
    assert payload["suggested_checks"][0]["matched_paths"] == ["discord_cap/cap/bot.py"]
    assert payload["suggested_checks"][0]["matched_patterns"] == ["cap/**"]
    assert payload["suggested_reviews"][0]["name"] == "target-relative-review"


def test_ready_requires_matching_profile_check_and_review(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_profile_config(tmp_path, repo)))
    assert (
        _run_workflow(
            "start",
            "profile-required",
            "--plan",
            "Touch CLI command behavior.",
            "--target",
            str(repo),
        ).returncode
        == 0
    )
    (repo / "src" / "harness_toolkit" / "kit").mkdir(parents=True)
    (repo / "src" / "harness_toolkit" / "kit" / "cli.py").write_text(
        "print('changed')\n"
    )
    _run_workflow(
        "decide",
        "No spec impact for synthetic CLI dogfood.",
        "--spec-impact",
        "none",
        "--target",
        str(repo),
    )
    missing = _run_workflow("ready", "--target", str(repo), "--json")
    assert missing.returncode == 1
    missing_payload = json.loads(missing.stdout)
    missing_checks = {check["id"]: check for check in missing_payload["checks"]}
    assert missing_checks["profile-check:unit-tests"]["status"] == "fail"
    assert (
        missing_checks["profile-review:agent-friendly-cli-review"]["status"] == "fail"
    )

    _run_workflow(
        "validate",
        "--check",
        "unit-tests",
        "--why",
        "Focused synthetic check.",
        "--target",
        str(repo),
        "--",
        "python3",
        "-c",
        "print('ok')",
    )
    _run_workflow(
        "review",
        "add",
        "--review",
        "agent-friendly-cli-review",
        "--backend",
        "subagent",
        "--reviewer",
        "fresh-context",
        "--summary",
        "No blockers.",
        "--target",
        str(repo),
    )
    _run_workflow("sync", "--target", str(repo))

    result = _run_workflow("ready", "--target", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    checks = {check["id"]: check for check in payload["checks"]}
    assert checks["profile-check:unit-tests"]["status"] == "pass"
    assert checks["profile-review:agent-friendly-cli-review"]["status"] == "pass"


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
    assert (
        "hk checks --target . --profile python --changed --json" in payload["agents_md"]
    )


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
dispatch_hint = "codex review --uncommitted"

[profiles.foreman.reviews.instructions]
type = "file"
path = "{prompt_file.name}"
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
    assert payload["reviews"][0]["instructions"] == {
        "type": "file",
        "path": prompt_file.name,
    }


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
    assert payload["match_kind"] == "direct"
    assert payload["matched_name"] == "module"


def test_profile_resolution_projects_configured_targets_into_linked_worktree(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    module = repo / "module"
    module.mkdir(parents=True)
    _git_init(repo)
    (module / "README.md").write_text("# module\n")
    subprocess.run(
        ["git", "add", "module/README.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "test: add module"],
        cwd=repo,
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
    worktree = tmp_path / "repo linked worktree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
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

    repo_result = _run_workflow(
        "profile", "resolve", "--target", str(worktree), "--json"
    )
    module_result = _run_workflow(
        "profile", "resolve", "--target", str(worktree / "module"), "--json"
    )
    file_result = _run_workflow(
        "profile",
        "resolve",
        "--target",
        str(worktree / "module" / "README.md"),
        "--json",
    )

    assert repo_result.returncode == 0, repo_result.stderr
    repo_payload = json.loads(repo_result.stdout)
    assert repo_payload["profile"] == "repo-profile"
    assert repo_payload["match_kind"] == "worktree"
    assert repo_payload["matched_name"] == "repo"
    assert repo_payload["matched_target"] == str(repo)
    assert "worktree" in repo_payload["reason"]
    assert repo_payload["worktree_matched_target"] == str(repo)
    assert repo_payload["worktree_target"] == str(worktree.resolve())

    assert module_result.returncode == 0, module_result.stderr
    module_payload = json.loads(module_result.stdout)
    assert module_payload["profile"] == "module-profile"
    assert module_payload["matched_name"] == "module"
    assert module_payload["matched_target"] == str(module)
    assert "worktree" in module_payload["reason"]
    assert module_payload["worktree_projected_target"] == str(
        (worktree / "module").resolve()
    )

    assert file_result.returncode == 0, file_result.stderr
    file_payload = json.loads(file_result.stdout)
    assert file_payload["profile"] == "module-profile"
    assert file_payload["match_kind"] == "worktree"
    assert file_payload["matched_name"] == "module"
    assert file_payload["matched_target"] == str(module)
    assert file_payload["worktree_projected_target"] == str(
        (worktree / "module").resolve()
    )


def test_profile_resolution_uses_projected_specificity_for_worktree_matches(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "deep" / "canonical" / "repo"
    module = repo / "module"
    module.mkdir(parents=True)
    _git_init(repo)
    (module / "README.md").write_text("# module\n")
    subprocess.run(
        ["git", "add", "module/README.md"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "test: add module"],
        cwd=repo,
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
    module_binding_worktree = tmp_path / "wt1"
    target_worktree = tmp_path / "wt2"
    for worktree in (module_binding_worktree, target_worktree):
        subprocess.run(
            ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
            cwd=repo,
            check=True,
            capture_output=True,
            env=_git_env(),
        )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1

[[targets]]
name = "repo"
path = "{repo}"
profile = "repo-profile"

[[targets]]
name = "module-from-linked-worktree"
path = "{module_binding_worktree / "module"}"
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

    result = _run_workflow(
        "profile", "resolve", "--target", str(target_worktree / "module"), "--json"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "module-profile"
    assert payload["matched_name"] == "module-from-linked-worktree"
    assert payload["worktree_projected_target"] == str(
        (target_worktree / "module").resolve()
    )


def test_profile_resolution_does_not_autoselect_for_separate_clone_with_same_origin(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", str(repo), str(clone)],
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "generic"

[[targets]]
name = "repo"
path = "{repo}"
profile = "repo-profile"

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
'''
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_workflow("profile", "resolve", "--target", str(clone), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "generic"
    assert (
        payload["reason"]
        == "no configured target matched; using config default_profile"
    )
    assert payload["worktree_matched_target"] is None


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
    assert "Do not chase final readiness after every edit" in result.stdout
    assert "after small review fixes prefer targeted validation/review" in result.stdout
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


def test_decide_records_invariant_supersession_payload(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_profile_config(tmp_path, repo)))

    start = _run_workflow(
        "start",
        "supersede-invariant",
        "--plan",
        "Supersede an invariant.",
        "--target",
        str(repo),
    )
    assert start.returncode == 0, start.stderr

    result = _run_workflow(
        "decide",
        "Supersede safe mention default.",
        "--target",
        str(repo),
        "--spec-impact",
        "updated",
        "--kind",
        "invariant-supersession",
        "--invariant",
        "message-writes.mentions-safe-by-default",
        "--previous",
        "Messages suppress mentions by default.",
        "--replacement",
        "Messages use Discord default parsing unless explicit allow-list flags are passed.",
        "--reason",
        "Product request.",
        "--doc",
        ".harness/system.toml",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    supersession = payload["invariant_supersession"]
    assert supersession["invariant"] == "message-writes.mentions-safe-by-default"
    assert (
        supersession["commit_trailer"]
        == "Supersedes-Invariant: message-writes.mentions-safe-by-default"
    )

    status_result = _run_workflow("status", "--target", str(repo), "--json")
    status_payload = json.loads(status_result.stdout)
    assert status_payload["invariant_supersessions"][0]["reason"] == "Product request."


def test_target_config_system_map_path_resolves_relative_to_config(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    system_map = maps_dir / "repo.toml"
    system_map.write_text("version = 1\n[system]\nname = 'demo'\nsummary = 'Demo.'\n")
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "generic"

[[targets]]
name = "repo"
path = "{repo}"
profile = "generic"
system_map = "system-maps/repo.toml"
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    resolved = _run_workflow("profile", "resolve", "--target", str(repo), "--json")
    brief_result = _run_workflow("brief", "--target", str(repo), "--json")

    assert resolved.returncode == 0, resolved.stderr
    resolution = json.loads(resolved.stdout)
    assert resolution["system_map"] == str(system_map)
    assert resolution["system_map_source"] == "target-config"
    assert brief_result.returncode == 0, brief_result.stderr
    summary = json.loads(brief_result.stdout)["system_map"]
    assert summary["source"] == "target-config"
    assert summary["path"] == str(system_map)
