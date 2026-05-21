from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.system_map import (
    parse_system_map_file,
    system_context_for_changed_paths,
)


def test_system_context_matches_changed_paths_and_marks_required_labels(
    tmp_path: Path,
) -> None:
    (tmp_path / ".harness").mkdir()
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "app.py").write_text("print('ok')\n")
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
paths = ["pkg/**"]
validation_checks = ["unit-tests"]
[[components.invariants]]
id = "owns-core"
statement = "Core owns behavior."
evidence = ["pkg/app.py"]
validation_checks = ["unit-tests"]
"""
    )
    loaded = parse_system_map_file(path, repo_root=tmp_path)
    assert loaded.map is not None

    context = system_context_for_changed_paths(
        loaded.map,
        source=".harness/system.toml",
        changed_paths=("pkg/app.py",),
        target=tmp_path,
        repo_root=tmp_path,
        profile_name="demo",
        known_check_labels={"unit-tests"},
        required_check_labels={"unit-tests"},
    )

    assert context.advisory is True
    assert context.label_resolution.status == "resolved"
    assert context.matched_components[0].id == "core"
    assert context.matched_components[0].matched_paths == ("pkg/app.py",)
    assert (
        context.matched_components[0].relevant_check_labels[0].required_by_profile
        is True
    )
    assert context.matched_components[0].invariants[0].qualified_id == "core.owns-core"
