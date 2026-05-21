from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _run_hk(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "hk", *args],
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
        ["git", "checkout", "-b", "main"],
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
        ["git", "commit", "--no-verify", "-m", "init"],
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


def _write_config(tmp_path: Path, repo: Path) -> Path:
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "demo"

[[targets]]
name = "repo"
path = "{repo}"
profile = "demo"

[profiles.demo]
title = "Demo"
summary = "Demo profile."
target_hint = "Use --target {repo}."
instructions = "Run checks."

[[profiles.demo.checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
applies_when = ["src/**"]
required_when = ["src/**"]
'''
    )
    return config


def test_checks_changed_includes_advisory_system_context(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('changed')\n")
    (repo / ".harness").mkdir()
    (repo / ".harness" / "system.toml").write_text(
        """
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
validation_checks = ["unit-tests"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
evidence = ["src/app.py"]
validation_checks = ["unit-tests"]
"""
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_config(tmp_path, repo)))

    result = _run_hk("checks", "--target", str(repo), "--changed", "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    context = payload["system_context"]
    assert context["advisory"] is True
    assert context["invariant_policy"] == "must_preserve_unless_superseded"
    assert context["conflict_protocol"] == "stop_confirm_record_decision"
    assert context["source"] == ".harness/system.toml"
    assert context["label_resolution"]["status"] == "resolved"
    assert context["matched_components"][0]["id"] == "core"
    assert (
        context["matched_components"][0]["relevant_check_labels"][0][
            "required_by_profile"
        ]
        is True
    )
    assert payload["suggested_checks"][0]["name"] == "unit-tests"

    text = _run_hk("checks", "--target", str(repo), "--changed")
    assert "System invariants for changed paths:" in text.stdout
    assert "Policy: must preserve surfaced invariants" in text.stdout
    assert "Must preserve core.owns-core: Core owns behavior." in text.stdout
    assert "stop and resolve the conflict" in text.stdout


def test_checks_changed_reports_invalid_system_map_without_using_matches(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('changed')\n")
    (repo / ".harness").mkdir()
    (repo / ".harness" / "system.toml").write_text(
        """
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
[[components]]
id = "core"
title = "Duplicate Core"
kind = "module"
paths = ["src/**"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
"""
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(_write_config(tmp_path, repo)))

    result = _run_hk("checks", "--target", str(repo), "--changed", "--json")

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["system_context"]
    assert context["source"] == ".harness/system.toml"
    assert context["matched_components"] == []
    assert context["warnings"][0]["severity"] == "error"
    assert "duplicate component id" in context["warnings"][0]["message"]

    text = _run_hk("checks", "--target", str(repo), "--changed")
    assert "Must preserve core.owns-core" not in text.stdout
    assert "error: duplicate component id" in text.stdout


def test_checks_changed_uses_target_config_system_map_repo_relative_paths(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('changed')\n")
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    external_map = maps_dir / "repo.toml"
    external_map.write_text(
        """
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
validation_checks = ["unit-tests"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
validation_checks = ["unit-tests"]
"""
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "demo"

[[targets]]
name = "repo"
path = "{repo}"
profile = "demo"
system_map = "system-maps/repo.toml"

[profiles.demo]
title = "Demo"
summary = "Demo profile."
target_hint = "Use --target {repo}."
instructions = "Run checks."

[[profiles.demo.checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
applies_when = ["src/**"]
required_when = ["src/**"]
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk("checks", "--target", str(repo), "--changed", "--json")

    assert result.returncode == 0, result.stderr
    context = json.loads(result.stdout)["system_context"]
    assert context["source"] == str(external_map)
    assert context["source_kind"] == "target-config"
    assert context["path_base"] == "repo-root"
    assert context["matched_components"][0]["id"] == "core"
    assert context["matched_components"][0]["matched_paths"] == ["src/app.py"]
    assert (
        context["matched_components"][0]["invariants"][0]["qualified_id"]
        == "core.owns-core"
    )


def test_checks_profile_override_tolerates_missing_target_profile_and_uses_system_map(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('changed')\n")
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    external_map = maps_dir / "repo.toml"
    external_map.write_text(
        """
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
"""
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "demo"

[[targets]]
name = "repo"
path = "{repo}"
profile = "missing-profile"
system_map = "system-maps/repo.toml"

[profiles.demo]
title = "Demo"
summary = "Demo profile."
target_hint = "Use --target {repo}."
instructions = "Run checks."

[[profiles.demo.checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
applies_when = ["src/**"]
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk(
        "checks", "--target", str(repo), "--profile", "demo", "--changed", "--json"
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["profile"] == "demo"
    assert payload["system_context"]["source_kind"] == "target-config"
    assert payload["system_context"]["source"] == str(external_map)
    assert payload["system_context"]["matched_components"][0]["id"] == "core"
