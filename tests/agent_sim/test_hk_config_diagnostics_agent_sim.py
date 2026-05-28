from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.support.hk2_repo import git_init, run_hk

pytestmark = pytest.mark.agent_sim


def _payload(result) -> dict[str, Any]:
    assert result.stdout, result.stderr
    return json.loads(result.stdout)


def _env(config: Path) -> dict[str, str]:
    return {"HARNESS_KIT_CONFIG": str(config)}


def _write_config_fixture(
    tmp_path: Path,
    repo: Path,
    *,
    default_profile: str = "demo",
    target_profile: str = "demo",
    map_label: str = "unit-tests",
    write_system_map: bool = True,
) -> Path:
    (repo / "src").mkdir(exist_ok=True)
    (repo / "src" / "app.py").write_text("print('ok')\n")
    (repo / "docs").mkdir(exist_ok=True)
    (repo / "docs" / "guide.md").write_text("# guide\n")

    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir(exist_ok=True)
    (profiles_dir / "demo.toml").write_text(
        f"""
name = "demo"
title = "Demo"
summary = "Demo profile."
target_hint = "Use --target {repo}."
instructions = "Run the checks that match the changed paths."

[[checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
applies_when = ["src/**"]
required_when = ["src/**"]

[[checks]]
name = "docs-check"
purpose = "Check docs changes."
command_template = "markdownlint docs"
run_from = "repo-root"
applies_when = ["docs/**"]
required_when = ["docs/**"]

[[reviews]]
name = "source-review"
purpose = "Review source changes."
backend = "fresh-context-subagent"
applies_when = ["src/**"]
required_when = ["src/**"]
""".lstrip()
    )

    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir(exist_ok=True)
    if write_system_map:
        (maps_dir / "repo.toml").write_text(
            f"""
version = 1
[system]
name = "demo"
summary = "Demo system map."

[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
validation_checks = ["unit-tests"]

[[components.invariants]]
id = "core-tested"
statement = "Core changes should stay covered by tests."
evidence = ["src/app.py"]
validation_checks = ["unit-tests"]

[[components]]
id = "docs"
title = "Docs"
kind = "docs"
paths = ["docs/**"]
validation_checks = ["{map_label}"]
""".lstrip()
        )

    config = tmp_path / "harness.toml"
    config.write_text(
        f"""
version = 1
profiles_dir = "profiles"
default_profile = "{default_profile}"

[[targets]]
name = "repo"
path = "{repo}"
profile = "{target_profile}"
system_map = "system-maps/repo.toml"
""".lstrip()
    )
    return config


def test_agent_sim_config_validate_diagnoses_missing_default_profile(
    tmp_path: Path,
) -> None:
    repo = git_init(tmp_path / "repo")
    config = _write_config_fixture(tmp_path, repo, default_profile="missing-default")

    result = run_hk(
        "config", "validate", "--target", str(repo), "--json", env=_env(config)
    )

    assert result.returncode == 1
    payload = _payload(result)
    assert payload["ok"] is False
    assert any(
        finding["code"] == "missing-default-profile"
        and "missing-default" in finding["message"]
        for finding in payload["findings"]
    )


def test_agent_sim_config_validate_catches_missing_target_system_map(
    tmp_path: Path,
) -> None:
    repo = git_init(tmp_path / "repo")
    config = _write_config_fixture(tmp_path, repo, write_system_map=False)

    result = run_hk(
        "config", "validate", "--target", str(repo), "--json", env=_env(config)
    )

    assert result.returncode == 1
    payload = _payload(result)
    assert payload["ok"] is False
    assert any(
        finding["code"] == "missing-target-system-map"
        for finding in payload["findings"]
    )


def test_agent_sim_config_validate_distinguishes_advisory_and_strict_stale_labels(
    tmp_path: Path,
) -> None:
    repo = git_init(tmp_path / "repo")
    config = _write_config_fixture(tmp_path, repo, map_label="old-docs-check")

    relaxed = run_hk(
        "config", "validate", "--target", str(repo), "--json", env=_env(config)
    )
    assert relaxed.returncode == 0, relaxed.stderr
    relaxed_payload = _payload(relaxed)
    assert relaxed_payload["ok"] is True
    assert any(
        finding["code"] == "unresolved-check-label" and finding["severity"] == "warning"
        for finding in relaxed_payload["findings"]
    )

    strict = run_hk(
        "config",
        "validate",
        "--target",
        str(repo),
        "--strict-labels",
        "--json",
        env=_env(config),
    )
    assert strict.returncode == 1
    strict_payload = _payload(strict)
    assert strict_payload["ok"] is False
    assert any(
        finding["code"] == "unresolved-check-label" and finding["severity"] == "error"
        for finding in strict_payload["findings"]
    )


def test_agent_sim_config_explain_handles_changed_and_explicit_paths(
    tmp_path: Path,
) -> None:
    repo = git_init(tmp_path / "repo")
    config = _write_config_fixture(tmp_path, repo)
    (repo / "src" / "app.py").write_text("print('changed')\n")
    (repo / "docs" / "guide.md").write_text("# changed\n")

    changed = run_hk(
        "config",
        "explain",
        "--target",
        str(repo),
        "--changed",
        "--json",
        env=_env(config),
    )
    assert changed.returncode == 0, changed.stderr
    changed_payload = _payload(changed)
    check_names = {check["name"] for check in changed_payload["checks"]}
    assert {"unit-tests", "docs-check"}.issubset(check_names)
    component_ids = {
        component["id"]
        for component in changed_payload["system_context"]["matched_components"]
    }
    assert {"core", "docs"}.issubset(component_ids)

    explicit = run_hk(
        "config",
        "explain",
        "--target",
        str(repo),
        "--path",
        "src/app.py",
        "--json",
        env=_env(config),
    )
    assert explicit.returncode == 0, explicit.stderr
    explicit_payload = _payload(explicit)
    assert explicit_payload["paths"] == ["src/app.py"]
    assert [check["name"] for check in explicit_payload["checks"]] == ["unit-tests"]
