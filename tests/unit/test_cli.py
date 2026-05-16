"""Unit tests for the Cyclopts harness-scaffold CLI."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

pytestmark = pytest.mark.cli

ROOT = Path(__file__).resolve().parents[2]


def _run_scaffold(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "harness-scaffold", *args],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )


# ── --version ─────────────────────────────────────────────────────────────────


def test_version_flag() -> None:
    result = _run_scaffold("--version")
    assert result.returncode == 0
    assert "0.2.0" in result.stdout


# ── --help ────────────────────────────────────────────────────────────────────


def test_root_help() -> None:
    result = _run_scaffold("--help")
    assert result.returncode == 0
    assert "harness-scaffold" in result.stdout.lower()


def test_legacy_agent_scaffold_command_is_not_registered() -> None:
    result = subprocess.run(
        ["uv", "run", "agent-scaffold", "--help"],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
    )

    assert result.returncode != 0


def test_init_help() -> None:
    result = _run_scaffold("init", "--help")
    assert result.returncode == 0
    assert "--non-interactive" in result.stdout
    assert "--name" in result.stdout
    assert "--shape" in result.stdout
    assert "--stack" in result.stdout


# ── non-interactive validation ────────────────────────────────────────────────


def test_non_interactive_requires_name() -> None:
    result = _run_scaffold(
        "init", "--non-interactive", "--shape", "single", "--stack", "python"
    )
    assert result.returncode != 0
    assert "--name" in result.stderr


def test_non_interactive_requires_shape() -> None:
    result = _run_scaffold(
        "init", "--non-interactive", "--name", "myapp", "--stack", "python"
    )
    assert result.returncode != 0
    assert "--shape" in result.stderr


def test_non_interactive_requires_stack() -> None:
    result = _run_scaffold(
        "init", "--non-interactive", "--name", "myapp", "--shape", "single"
    )
    assert result.returncode != 0
    assert "--stack" in result.stderr


def test_invalid_name_rejected() -> None:
    result = _run_scaffold(
        "init",
        "--non-interactive",
        "--name",
        "My App!",
        "--shape",
        "single",
        "--stack",
        "python",
    )
    assert result.returncode != 0


def test_invalid_shape_rejected() -> None:
    result = _run_scaffold(
        "init",
        "--non-interactive",
        "--name",
        "myapp",
        "--shape",
        "invalid",
        "--stack",
        "python",
    )
    assert result.returncode != 0


def test_invalid_stack_rejected() -> None:
    result = _run_scaffold(
        "init",
        "--non-interactive",
        "--name",
        "myapp",
        "--shape",
        "single",
        "--stack",
        "ruby",
    )
    assert result.returncode != 0
