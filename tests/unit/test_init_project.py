"""Unit tests for config validation and name utilities.

These tests import and call the Python functions directly — no subprocess,
no temp dirs, very fast.
"""

from __future__ import annotations

import pytest

from harness_toolkit.scaffold.config import to_module_name, validate_name

pytestmark = pytest.mark.unit


# ── validate_name ─────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "name",
    ["myproject", "my-project", "my-proj-123", "a", "abc123"],
)
def test_validate_name_valid(name: str) -> None:
    assert validate_name(name) == name


@pytest.mark.parametrize(
    "name",
    [
        "MyProject",  # uppercase
        "my_project",  # underscore
        "1project",  # leading digit
        "my project",  # space
        "my.project",  # dot
        "",  # empty
        "-myproject",  # leading hyphen
    ],
)
def test_validate_name_invalid(name: str) -> None:
    with pytest.raises(ValueError):
        validate_name(name)


# ── to_module_name ────────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("myproject", "myproject"),
        ("my-project", "my_project"),
        ("my-long-project-name", "my_long_project_name"),
        ("abc", "abc"),
    ],
)
def test_to_module_name(name: str, expected: str) -> None:
    assert to_module_name(name) == expected
