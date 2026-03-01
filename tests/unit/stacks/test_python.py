"""Unit tests for PythonStack."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_tools_toml_has_python_and_uv() -> None:
    from agent_scaffold.stacks.python import PythonStack

    tools = PythonStack().tools_toml()
    assert 'python = "3.12"' in tools
    assert "uv" in tools


def test_adr_notes_mentions_key_tools() -> None:
    from agent_scaffold.stacks.python import PythonStack

    notes = PythonStack().adr_notes()
    assert "uv" in notes
    assert "ruff" in notes
    assert "ty" in notes
    assert "pytest" in notes


def test_stack_notes_mentions_key_tools() -> None:
    from agent_scaffold.stacks.python import PythonStack

    notes = PythonStack().stack_notes()
    assert "ruff" in notes
    assert "ty" in notes
    assert "pytest" in notes
