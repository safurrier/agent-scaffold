from __future__ import annotations

import os
import subprocess
from dataclasses import asdict
from pathlib import Path

from harness_toolkit.kit.local import brief


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


def test_brief_reports_no_system_map_as_null(tmp_path: Path) -> None:
    _git_init(tmp_path)

    result = brief(tmp_path)

    assert result.system_map is None
    assert asdict(result)["system_map"] is None


def test_brief_summarizes_valid_system_map(tmp_path: Path) -> None:
    _git_init(tmp_path)
    (tmp_path / ".harness").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')\n")
    (tmp_path / ".harness" / "system.toml").write_text(
        """
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/app.py"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
evidence = ["src/app.py"]
"""
    )

    result = brief(tmp_path)

    assert result.system_map is not None
    assert result.system_map.status == "valid"
    assert result.system_map.path == ".harness/system.toml"
    assert result.system_map.components == 1
    assert result.system_map.invariants == 1


def test_brief_summarizes_invalid_system_map_without_crashing(tmp_path: Path) -> None:
    _git_init(tmp_path)
    (tmp_path / ".harness").mkdir()
    (tmp_path / ".harness" / "system.toml").write_text("not toml =")

    result = brief(tmp_path)

    assert result.system_map is not None
    assert result.system_map.status == "invalid"
    assert result.system_map.errors_count == 1


def test_brief_prefers_target_config_system_map_over_repo_local(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / ".harness").mkdir()
    (repo / ".harness" / "system.toml").write_text(
        """
version = 1
[system]
name = "repo-local"
summary = "Repo-local map."
"""
    )
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    external_map = maps_dir / "repo.toml"
    external_map.write_text(
        """
version = 1
[system]
name = "target-config"
summary = "Target-config map."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["README.md"]
"""
    )
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

    result = brief(repo)

    assert result.system_map is not None
    assert result.system_map.source == "target-config"
    assert result.system_map.path == str(external_map)
    assert result.system_map.overrides == ".harness/system.toml"
    assert result.system_map.components == 1


def test_brief_tolerates_missing_configured_profile_and_still_loads_system_map(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    external_map = maps_dir / "repo.toml"
    external_map.write_text(
        """
version = 1
[system]
name = "target-config"
summary = "Target-config map."
"""
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
default_profile = "generic"

[[targets]]
name = "repo"
path = "{repo}"
profile = "missing-profile"
system_map = "system-maps/repo.toml"
'''.lstrip()
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = brief(repo)

    assert result.system_map is not None
    assert result.system_map.source == "target-config"
    assert result.system_map.path == str(external_map)
