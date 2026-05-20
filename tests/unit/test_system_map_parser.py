from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.system_map import parse_system_map_file


def _write_valid_map(repo: Path) -> Path:
    (repo / ".harness").mkdir()
    (repo / "src").mkdir()
    (repo / "docs").mkdir()
    (repo / "src" / "app.py").write_text("print('ok')\n")
    (repo / "docs" / "architecture.md").write_text("# arch\n")
    path = repo / ".harness" / "system.toml"
    path.write_text(
        """
version = 1

[system]
name = "demo"
summary = "Demo system."

[[components]]
id = "app-state"
title = "App state"
kind = "state-machine"
paths = ["src/app.py"]
read_before_editing = ["docs/architecture.md"]
validation_checks = ["unit-tests"]

[[components.invariants]]
id = "mutation-owned"
statement = "The app module owns mutation."
evidence = ["src/app.py"]
validation_checks = ["unit-tests"]
"""
    )
    return path


def test_valid_system_map_parses(tmp_path: Path) -> None:
    path = _write_valid_map(tmp_path)

    result = parse_system_map_file(path, repo_root=tmp_path)

    assert result.ok is True
    assert result.map is not None
    assert result.map.system.name == "demo"
    assert result.map.components[0].id == "app-state"
    assert result.map.invariant_count == 1


def test_duplicate_component_and_missing_path_fail(tmp_path: Path) -> None:
    (tmp_path / ".harness").mkdir()
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "app.py").write_text("print('ok')\n")
    path = tmp_path / ".harness" / "system.toml"
    path.write_text(
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
[[components]]
id = "core"
title = "Core again"
kind = "module"
paths = ["missing.py"]
"""
    )

    result = parse_system_map_file(path, repo_root=tmp_path)

    assert result.ok is False
    codes = {finding.code for finding in result.findings}
    assert "duplicate-component-id" in codes
    assert "missing-path" in codes


def test_relation_endpoint_must_reference_component(tmp_path: Path) -> None:
    path = _write_valid_map(tmp_path)
    with path.open("a") as file:
        file.write(
            """
[[relations]]
from = "app-state"
to = "missing-component"
kind = "calls"
rule = "App calls missing."
"""
        )

    result = parse_system_map_file(path, repo_root=tmp_path)

    assert result.ok is False
    assert "unknown-relation-endpoint" in {finding.code for finding in result.findings}
