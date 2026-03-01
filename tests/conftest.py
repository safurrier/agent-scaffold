"""Shared fixtures for agent-scaffold tests."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests._support import COPY_IGNORE, SCAFFOLD_ROOT, trust_mise

# ── Fixtures available to all test sub-packages ───────────────────────────


@pytest.fixture()
def scaffold_copy(tmp_path: Path) -> Path:
    """Fresh copy of the scaffold in a temp directory (function-scoped)."""
    dest = tmp_path / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    trust_mise(dest)
    return dest
