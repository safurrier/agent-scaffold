"""Unit tests for GoStack."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_tools_toml_has_go_gofumpt_golangci() -> None:
    from agent_scaffold.stacks.go import GoStack

    tools = GoStack().tools_toml()
    assert 'python = "3.12"' in tools
    assert 'uv = "latest"' in tools
    assert "go = " in tools
    assert "gofumpt" in tools
    assert "golangci-lint" in tools


def test_adr_notes_mentions_key_tools() -> None:
    from agent_scaffold.stacks.go import GoStack

    notes = GoStack().adr_notes()
    assert "go" in notes
    assert "gofumpt" in notes
    assert "golangci-lint" in notes


def test_stack_notes_mentions_key_tools() -> None:
    from agent_scaffold.stacks.go import GoStack

    notes = GoStack().stack_notes()
    assert "gofumpt" in notes
    assert "golangci-lint" in notes
    assert "go vet" in notes
