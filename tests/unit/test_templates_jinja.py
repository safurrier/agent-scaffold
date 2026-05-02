"""Unit tests for the Jinja2 template engine.

Tests render_template() and copy_tree() in isolation — no subprocess, no mise.
"""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _import_engine():
    """Ensure harness_toolkit.scaffold.templates is importable before each test."""
    from harness_toolkit.scaffold import templates  # noqa: F401


# ── render_template ───────────────────────────────────────────────────────────


def test_render_simple_variable(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "test.md.tmpl"
    tmpl.write_text("Hello {{ project_name }}!")
    assert render_template(tmpl, {"project_name": "myapp"}) == "Hello myapp!"


def test_render_conditional_true_branch(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "test.tmpl"
    tmpl.write_text("{% if stack == 'go' %}go{% else %}other{% endif %}")
    assert render_template(tmpl, {"stack": "go"}) == "go"


def test_render_conditional_false_branch(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "test.tmpl"
    tmpl.write_text("{% if stack == 'go' %}go{% else %}other{% endif %}")
    assert render_template(tmpl, {"stack": "python"}) == "other"


def test_render_loop(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "ws.tmpl"
    tmpl.write_text("{% for m in modules %}[{{ m }}]\n{% endfor %}")
    result = render_template(tmpl, {"modules": ["api", "worker"]})
    assert "[api]" in result
    assert "[worker]" in result


def test_render_undefined_variable_raises(tmp_path: Path) -> None:
    from jinja2 import UndefinedError

    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "test.tmpl"
    tmpl.write_text("Hello {{ missing_var }}!")
    with pytest.raises(UndefinedError):
        render_template(tmpl, {})


def test_render_preserves_trailing_newline(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import render_template

    tmpl = tmp_path / "test.tmpl"
    tmpl.write_text("line\n")
    assert render_template(tmpl, {}).endswith("\n")


# ── copy_tree ─────────────────────────────────────────────────────────────────


def test_copy_tree_processes_tmpl_files(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import copy_tree

    src = tmp_path / "src"
    src.mkdir()
    (src / "file.md.tmpl").write_text("Hello {{ name }}!")
    dst = tmp_path / "dst"
    copy_tree(src, dst, {"name": "world"})
    assert (dst / "file.md").read_text() == "Hello world!"


def test_copy_tree_strips_tmpl_extension(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import copy_tree

    src = tmp_path / "src"
    src.mkdir()
    (src / "config.toml.tmpl").write_text("name = '{{ project_name }}'")
    dst = tmp_path / "dst"
    copy_tree(src, dst, {"project_name": "myapp"})
    assert (dst / "config.toml").exists()
    assert not (dst / "config.toml.tmpl").exists()


def test_copy_tree_copies_plain_files_verbatim(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import copy_tree

    src = tmp_path / "src"
    src.mkdir()
    (src / "README.md").write_text("# plain file, no template vars")
    dst = tmp_path / "dst"
    copy_tree(src, dst, {"foo": "bar"})
    assert (dst / "README.md").read_text() == "# plain file, no template vars"


def test_copy_tree_handles_nested_directories(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.templates import copy_tree

    src = tmp_path / "src"
    (src / "sub").mkdir(parents=True)
    (src / "sub" / "deep.tmpl").write_text("{{ val }}")
    dst = tmp_path / "dst"
    copy_tree(src, dst, {"val": "hi"})
    assert (dst / "sub" / "deep").read_text() == "hi"


def test_copy_tree_handles_binary_files(tmp_path: Path) -> None:
    """Binary files should be copied without UnicodeDecodeError."""
    from harness_toolkit.scaffold.templates import copy_tree

    src = tmp_path / "src"
    src.mkdir()
    (src / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR")
    dst = tmp_path / "dst"
    copy_tree(src, dst, {})
    assert (dst / "image.png").exists()
    assert (dst / "image.png").read_bytes()[:4] == b"\x89PNG"
