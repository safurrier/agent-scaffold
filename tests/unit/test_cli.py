"""Unit tests for the Click CLI using CliRunner.

Focuses on argument validation and error paths — no subprocess, no filesystem
mutations. Full init flow is covered by E2E tests.
"""

from __future__ import annotations

import pytest
from click.testing import CliRunner

pytestmark = pytest.mark.unit


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


# ── --version ─────────────────────────────────────────────────────────────────


def test_version_flag(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output


# ── --help ────────────────────────────────────────────────────────────────────


def test_root_help(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "agent-scaffold" in result.output.lower()


def test_init_help(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(cli, ["init", "--help"])
    assert result.exit_code == 0
    assert "--non-interactive" in result.output
    assert "--name" in result.output
    assert "--shape" in result.output
    assert "--stack" in result.output


# ── non-interactive validation ────────────────────────────────────────────────


def test_non_interactive_requires_name(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli, ["init", "--non-interactive", "--shape", "single", "--stack", "python"]
    )
    assert result.exit_code != 0
    assert "--name" in result.output


def test_non_interactive_requires_shape(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli, ["init", "--non-interactive", "--name", "myapp", "--stack", "python"]
    )
    assert result.exit_code != 0
    assert "--shape" in result.output


def test_non_interactive_requires_stack(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli, ["init", "--non-interactive", "--name", "myapp", "--shape", "single"]
    )
    assert result.exit_code != 0
    assert "--stack" in result.output


def test_invalid_name_rejected(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli,
        [
            "init",
            "--non-interactive",
            "--name",
            "My App!",
            "--shape",
            "single",
            "--stack",
            "python",
        ],
    )
    assert result.exit_code != 0


def test_invalid_shape_rejected(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli,
        [
            "init",
            "--non-interactive",
            "--name",
            "myapp",
            "--shape",
            "invalid",
            "--stack",
            "python",
        ],
    )
    assert result.exit_code != 0


def test_invalid_stack_rejected(runner: CliRunner) -> None:
    from agent_scaffold.cli import cli

    result = runner.invoke(
        cli,
        [
            "init",
            "--non-interactive",
            "--name",
            "myapp",
            "--shape",
            "single",
            "--stack",
            "rust",
        ],
    )
    assert result.exit_code != 0
