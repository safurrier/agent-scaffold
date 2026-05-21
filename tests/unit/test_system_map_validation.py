from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.system_map import check_label_findings, parse_system_map_file


def test_unresolved_check_label_warns_by_default_and_errors_in_strict(
    tmp_path: Path,
) -> None:
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
validation_checks = ["missing-check"]
"""
    )
    result = parse_system_map_file(path, repo_root=tmp_path)
    assert result.map is not None

    warnings = check_label_findings(result.map, known_check_labels={"unit-tests"})
    strict = check_label_findings(
        result.map, known_check_labels={"unit-tests"}, strict_profile=True
    )

    assert warnings[0].severity == "warning"
    assert warnings[0].check_label == "missing-check"
    assert strict[0].severity == "error"


def test_system_map_path_validation_uses_runtime_pathspec_semantics(
    tmp_path: Path,
) -> None:
    (tmp_path / ".harness").mkdir()
    (tmp_path / "src" / "nested").mkdir(parents=True)
    (tmp_path / "src" / "nested" / "app.py").write_text("print('ok')\n")
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
paths = ["src/*.py"]
"""
    )

    result = parse_system_map_file(path, repo_root=tmp_path)

    assert result.map is not None
    assert any(finding.code == "missing-path" for finding in result.findings)
