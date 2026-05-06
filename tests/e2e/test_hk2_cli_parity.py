from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.hk2_repo import git_init, run_hk

pytestmark = pytest.mark.e2e


def test_hk2_cli_lifecycle_happy_path(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")

    commands = [
        (
            "start",
            "cli-parity",
            "--plan",
            "Exercise CLI parity",
            "--target",
            str(target),
        ),
        (
            "decide",
            "No committed spec impact for parity smoke.",
            "--spec-impact",
            "not-needed",
            "--target",
            str(target),
        ),
        (
            "validate",
            "--why",
            "Native command evidence still captures pass status.",
            "--target",
            str(target),
            "--",
            "python3",
            "-c",
            "print('ok')",
        ),
        (
            "review",
            "add",
            "--backend",
            "codex",
            "--reviewer",
            "codex-review",
            "--rubric",
            "core-quality",
            "--summary",
            "Accepted for parity.",
            "--target",
            str(target),
        ),
        ("sync", "--target", str(target)),
    ]
    for command in commands:
        result = run_hk(*command)
        assert result.returncode == 0, (command, result.stdout, result.stderr)

    ready = run_hk("ready", "--target", str(target), "--json")
    assert ready.returncode == 0, ready.stderr
    payload = json.loads(ready.stdout)
    assert payload["ready"] is True
    assert payload["status"] == "ready"

    handoff = run_hk("handoff", "--target", str(target))
    assert handoff.returncode == 0, handoff.stderr
    assert "## Validation evidence" in handoff.stdout
    assert "## Review" in handoff.stdout


def test_profile_config_cli_parity(tmp_path: Path) -> None:
    repo = git_init(tmp_path / "repo")
    module = repo / "module"
    module.mkdir()
    config = tmp_path / "harness.toml"
    prompt = tmp_path / "review.md"
    prompt.write_text("Review prompt from file.\n")
    config.write_text(
        f"""
[[targets]]
name = "base-target"
path = {str(repo)!r}
profile = "base"

[[targets]]
name = "module-target"
path = {str(module)!r}
profile = "module"

[profiles.base]
title = "Base Profile"
summary = "Base profile"
target_hint = "Base target"
instructions = "Use base checks."

[[profiles.base.checks]]
name = "base-tests"
purpose = "Base tests"
command_template = "pytest"
run_from = "target"

[profiles.module]
title = "Module Profile"
summary = "Module profile"
target_hint = "Module target"
instructions = "Use module checks."

[[profiles.module.checks]]
name = "module-tests"
purpose = "Module tests"
command_template = "pytest module"
run_from = "target"

[[profiles.module.reviews]]
name = "module-review"
purpose = "Fresh review"
backend = "codex"
rubric = "core-quality"
dispatch_hint = "codex review --uncommitted"
prompt_file = {str(prompt)!r}
"""
    )
    env = {"HARNESS_KIT_CONFIG": str(config)}

    resolved = run_hk("profile", "resolve", "--target", str(module), "--json", env=env)
    assert resolved.returncode == 0, resolved.stderr
    assert json.loads(resolved.stdout)["profile"] == "module"

    checks = run_hk("checks", "--target", str(module), "--json", env=env)
    assert checks.returncode == 0, checks.stderr
    payload = json.loads(checks.stdout)
    assert payload["profile"] == "module"
    assert payload["checks"][0]["name"] == "module-tests"
    assert payload["reviews"][0]["prompt_file_text"] == "Review prompt from file.\n"


@pytest.mark.xfail(
    reason="Chunk 8 deletes legacy surfaces after baseline parity is in place"
)
def test_removed_legacy_surfaces_are_not_in_root_help() -> None:
    root = run_hk("--help")
    assert root.returncode == 0
    assert "legacy" not in root.stdout.lower()
    assert "attach" not in root.stdout.lower()


@pytest.mark.xfail(reason="Chunk 8 deletes legacy status fallback flags")
def test_status_mode_is_not_a_legacy_entrypoint(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")

    result = run_hk("status", "--target", str(target), "--mode", "overlay")

    assert result.returncode != 0
    assert "mode" in (result.stderr + result.stdout).lower()
