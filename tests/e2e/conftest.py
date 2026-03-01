"""Module-scoped fixtures for E2E tests.

These fixtures run a full ``init + setup`` cycle once per test module, which
is expensive but shared across all tests in that module.  Negative-path tests
must copy the ready project before mutating it (see ``py_single_mut`` /
``go_single_mut``).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from tests._support import (
    COPY_IGNORE,
    SCAFFOLD_ROOT,
    init_project,
    mise,
    trust_mise,
)

# ── Module-scoped "ready" fixtures (init + setup already done) ────────────


@pytest.fixture(scope="module")
def py_single_ready(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Initialized + set-up Python single project (module scope)."""
    dest = tmp_path_factory.mktemp("py-single") / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    trust_mise(dest)

    result = init_project(dest, name="testpyapp", shape="single", stack="python")
    assert result.returncode == 0, f"init failed:\n{result.stderr}"

    trust_mise(dest)

    result = mise("setup", dest, timeout=180)
    assert result.returncode == 0, f"setup failed:\n{result.stderr}"

    return dest


@pytest.fixture(scope="module")
def py_apps_ready(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Initialized + set-up Python apps workspace (module scope)."""
    dest = tmp_path_factory.mktemp("py-apps") / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    trust_mise(dest)

    result = init_project(
        dest, name="testplatform", shape="apps", stack="python", modules="api,worker"
    )
    assert result.returncode == 0, f"init failed:\n{result.stderr}"

    trust_mise(dest)

    result = mise("setup", dest, timeout=240)
    assert result.returncode == 0, f"setup failed:\n{result.stderr}"

    return dest


@pytest.fixture(scope="module")
def go_single_ready(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Initialized + set-up Go single project (module scope)."""
    dest = tmp_path_factory.mktemp("go-single") / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    trust_mise(dest)

    result = init_project(
        dest,
        name="testgoapp",
        shape="single",
        stack="go",
        go_module="github.com/test-org/testgoapp",
    )
    assert result.returncode == 0, f"init failed:\n{result.stderr}"

    trust_mise(dest)

    result = mise("setup", dest, timeout=300)
    assert result.returncode == 0, f"setup failed:\n{result.stderr}"

    return dest


@pytest.fixture(scope="module")
def go_apps_ready(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Initialized + set-up Go apps workspace (module scope)."""
    dest = tmp_path_factory.mktemp("go-apps") / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    trust_mise(dest)

    result = init_project(
        dest,
        name="testgoplatform",
        shape="apps",
        stack="go",
        modules="svc-a,svc-b",
        go_module="github.com/test-org/testgoplatform",
    )
    assert result.returncode == 0, f"init failed:\n{result.stderr}"

    trust_mise(dest)

    result = mise("setup", dest, timeout=300)
    assert result.returncode == 0, f"setup failed:\n{result.stderr}"

    return dest


# ── Function-scoped "mutable" copies for negative-path tests ─────────────


@pytest.fixture()
def py_single_mut(py_single_ready: Path, tmp_path: Path) -> Path:
    """Mutable copy of the initialized Python single project (re-runs setup)."""
    dest = tmp_path / "py-single"
    shutil.copytree(py_single_ready, dest, ignore=COPY_IGNORE)
    trust_mise(dest)
    mise("setup", dest, timeout=120)
    return dest


@pytest.fixture()
def go_single_mut(go_single_ready: Path, tmp_path: Path) -> Path:
    """Mutable copy of the initialized Go single project (re-runs setup)."""
    dest = tmp_path / "go-single"
    shutil.copytree(go_single_ready, dest, ignore=COPY_IGNORE)
    trust_mise(dest)
    mise("setup", dest, timeout=180)
    return dest
