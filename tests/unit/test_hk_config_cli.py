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
        env=_git_env(),
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


def _write_config(tmp_path: Path, repo: Path, *, map_label: str = "unit-tests") -> Path:
    maps_dir = tmp_path / "system-maps"
    maps_dir.mkdir()
    (maps_dir / "repo.toml").write_text(
        f'''
version = 1
[system]
name = "demo"
summary = "Demo."
[[components]]
id = "core"
title = "Core"
kind = "module"
paths = ["src/**"]
read_before_editing = ["README.md"]
validation_checks = ["{map_label}"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
evidence = ["src/app.py"]
validation_checks = ["{map_label}"]
'''.lstrip()
    )
    config = tmp_path / "harness.toml"
    config.write_text(
        f'''
version = 1
profiles_dir = "profiles"
default_profile = "demo"

[[targets]]
name = "repo"
path = "{repo}"
profile = "demo"
system_map = "system-maps/repo.toml"
'''.lstrip()
    )
    profiles_dir = tmp_path / "profiles"
    profiles_dir.mkdir()
    (profiles_dir / "demo.toml").write_text(
        f"""
name = "demo"
title = "Demo"
summary = "Demo profile."
target_hint = "Use --target {repo}."
instructions = "Run checks."

[[checks]]
name = "unit-tests"
purpose = "Run unit tests."
command_template = "uv run pytest"
run_from = "repo-root"
applies_when = ["src/**"]
required_when = ["src/**"]

[[reviews]]
name = "demo-review"
purpose = "Review source changes."
backend = "fresh-context-subagent"
applies_when = ["src/**"]
required_when = ["src/**"]
""".lstrip()
    )
    return config


def test_config_help_describes_agent_facing_options() -> None:
    validate_help = _run_hk("config", "validate", "--help")
    assert validate_help.returncode == 0, validate_help.stderr
    assert "Target repository or scoped path whose HK config" in validate_help.stdout
    assert "should be validated" in validate_help.stdout
    assert "Treat unresolved system-map validation/review check" in validate_help.stdout
    assert "labels as errors instead of advisory warnings" in validate_help.stdout
    assert "does not run profile check commands" in validate_help.stdout

    explain_help = _run_hk("config", "explain", "--help")
    assert explain_help.returncode == 0, explain_help.stderr
    assert "Pass exactly one path source" in explain_help.stdout
    assert "Explicit repo-root-relative path to explain" in explain_help.stdout
    assert "does not execute checks" in explain_help.stdout


def test_config_json_errors_are_structured_for_repo_state_failures(
    tmp_path: Path,
) -> None:
    target = tmp_path / "not-a-repo"
    target.mkdir()

    result = _run_hk("config", "validate", "--target", str(target), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["findings"][0]["code"] == "repo-state-error"


def test_config_inspect_exits_nonzero_for_error_findings(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    missing_profiles = tmp_path / "missing-profiles"

    result = _run_hk(
        "config",
        "inspect",
        "--target",
        str(repo),
        "--profiles-dir",
        str(missing_profiles),
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["findings"][0]["severity"] == "error"


def test_config_inspect_reports_target_profile_and_system_map(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    config = _write_config(tmp_path, repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk("config", "inspect", "--target", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["config_path"] == str(config)
    assert payload["resolution"]["profile"] == "demo"
    assert payload["resolution"]["match_kind"] == "direct"
    assert payload["system_map"]["source"] == "target-config"
    assert payload["system_map"]["status"] == "valid"


def test_config_validate_strict_labels_promotes_unresolved_label_to_error(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    config = _write_config(tmp_path, repo, map_label="missing-check")
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    relaxed = _run_hk("config", "validate", "--target", str(repo), "--json")
    assert relaxed.returncode == 0, relaxed.stderr
    relaxed_payload = json.loads(relaxed.stdout)
    assert relaxed_payload["ok"] is True
    assert relaxed_payload["findings"][0]["code"] == "unresolved-check-label"
    assert relaxed_payload["findings"][0]["severity"] == "warning"

    strict = _run_hk(
        "config", "validate", "--target", str(repo), "--strict-labels", "--json"
    )
    assert strict.returncode == 1
    strict_payload = json.loads(strict.stdout)
    assert strict_payload["ok"] is False
    assert strict_payload["findings"][0]["severity"] == "error"


def test_config_validate_reports_missing_default_profile(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    config = _write_config(tmp_path, repo)
    config.write_text(
        config.read_text().replace(
            'default_profile = "demo"', 'default_profile = "missing-default"'
        )
    )
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk("config", "validate", "--target", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert any(
        finding["code"] == "missing-default-profile" for finding in payload["findings"]
    )


def test_config_explain_requires_changed_or_path(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    config = _write_config(tmp_path, repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk("config", "explain", "--target", str(repo), "--json")

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["findings"][0]["code"] == "missing-path-source"
    assert (
        "requires --changed or at least one --path" in payload["findings"][0]["message"]
    )


def test_config_explain_rejects_changed_and_path_together(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    config = _write_config(tmp_path, repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk(
        "config",
        "explain",
        "--target",
        str(repo),
        "--changed",
        "--path",
        "src/app.py",
        "--json",
    )

    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["ok"] is False
    assert payload["findings"][0]["code"] == "conflicting-path-source"
    assert "either --changed or --path, not both" in payload["findings"][0]["message"]


def test_config_explain_path_reuses_changed_path_suggestions(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    config = _write_config(tmp_path, repo)
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk(
        "config",
        "explain",
        "--target",
        str(repo),
        "--path",
        "src/app.py",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["source_engine"] == "profile-checks-view"
    assert payload["paths"] == ["src/app.py"]
    assert payload["checks"][0]["name"] == "unit-tests"
    assert payload["checks"][0]["required"] is True
    assert payload["reviews"][0]["name"] == "demo-review"
    assert payload["system_context"]["matched_components"][0]["id"] == "core"
    assert (
        payload["system_context"]["matched_components"][0]["invariants"][0][
            "qualified_id"
        ]
        == "core.owns-core"
    )


def test_config_audit_is_advisory_for_unresolved_label(
    tmp_path: Path, monkeypatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git_init(repo)
    (repo / "src").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    config = _write_config(tmp_path, repo, map_label="missing-check")
    monkeypatch.setenv("HARNESS_KIT_CONFIG", str(config))

    result = _run_hk("config", "audit", "--target", str(repo), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["findings"][0]["code"] == "unresolved-check-label"
    assert payload["findings"][0]["severity"] == "warning"
