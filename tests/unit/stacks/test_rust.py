"""Unit tests for RustStack."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_tools_toml_has_rust() -> None:
    from harness_toolkit.scaffold.stacks.rust import RustStack

    tools = RustStack().tools_toml()
    assert 'python = "3.12"' in tools
    assert 'uv = "latest"' in tools
    assert 'rust = "stable"' in tools


def test_adr_notes_mentions_key_tools() -> None:
    from harness_toolkit.scaffold.stacks.rust import RustStack

    notes = RustStack().adr_notes()
    assert "cargo fmt" in notes
    assert "cargo clippy" in notes
    assert "cargo check" in notes
    assert "cargo test" in notes


def test_stack_notes_mentions_key_tools() -> None:
    from harness_toolkit.scaffold.stacks.rust import RustStack

    notes = RustStack().stack_notes()
    assert "cargo fmt" in notes
    assert "clippy" in notes
    assert "cargo check" in notes
    assert "cargo test" in notes
