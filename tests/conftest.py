"""Shared fixtures and helpers for agent-scaffold tests."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent

# Directories / files that change between runs and shouldn't be copied
_COPY_IGNORE = shutil.ignore_patterns(
    ".git",
    "__pycache__",
    "*.pyc",
    ".venv",
    ".mypy_cache",
    ".ruff_cache",
)


# ── Helpers ───────────────────────────────────────────────────────────────────


def mise(
    task: str, cwd: Path, *extra_args: str, timeout: int = 300
) -> subprocess.CompletedProcess[str]:
    """Run ``mise run <task>`` in *cwd* and return the completed process.

    Extra args (if any) are passed after ``--`` so they reach the task script.
    """
    cmd = ["mise", "run", task]
    if extra_args:
        cmd += ["--", *extra_args]
    return subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def init_project(
    cwd: Path,
    *,
    name: str,
    shape: str,
    stack: str,
    modules: str = "",
    go_module: str = "",
    no_hooks: bool = True,
    no_examples: bool = False,
    timeout: int = 120,
) -> subprocess.CompletedProcess[str]:
    """Run ``mise run init --non-interactive ...`` and return the process."""
    args: list[str] = [
        "--non-interactive",
        "--name",
        name,
        "--shape",
        shape,
        "--stack",
        stack,
    ]
    if modules:
        args += ["--modules", modules]
    if go_module:
        args += ["--go-module", go_module]
    if no_hooks:
        args.append("--no-hooks")
    if no_examples:
        args.append("--no-examples")
    return mise("init", cwd, *args, timeout=timeout)


def _trust_mise(path: Path) -> None:
    """Trust the .mise.toml at *path* so tasks can run in temp directories."""
    mise_toml = path / ".mise.toml"
    if mise_toml.exists():
        subprocess.run(
            ["mise", "trust", str(mise_toml)],
            cwd=path,
            capture_output=True,
        )


# ── Fixtures available to all test sub-packages ───────────────────────────────


@pytest.fixture()
def scaffold_copy(tmp_path: Path) -> Path:
    """Fresh copy of the scaffold in a temp directory (function-scoped)."""
    dest = tmp_path / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=_COPY_IGNORE)
    _trust_mise(dest)
    return dest
