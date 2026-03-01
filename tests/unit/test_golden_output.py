"""Golden output tests — verify generated file content is deterministic.

These tests call run_init() directly as a Python function (no subprocess
through mise, no network). They are fast and belong in the unit test layer.

Note: run_init() calls git_init() internally (subprocess git in tmp_path),
which is acceptable for these tests.
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from agent_scaffold.common import run_init
from agent_scaffold.config import Config
from tests._support import COPY_IGNORE, SCAFFOLD_ROOT

pytestmark = pytest.mark.unit

# Fixed test constants — same across all golden tests
_NAME = "goldenapp"


# ── helpers ────────────────────────────────────────────────────────────────


def _scaffold_copy(tmp_path: Path) -> Path:
    """Copy the scaffold into tmp_path for direct run_init() use."""
    dest = tmp_path / "scaffold"
    shutil.copytree(SCAFFOLD_ROOT, dest, ignore=COPY_IGNORE)
    return dest


def _init(
    root: Path,
    *,
    shape: str,
    stack: str,
    modules: list[str] | None = None,
) -> Path:
    """Run run_init directly and return root."""
    config = Config(
        name=_NAME,
        description="A golden test project",
        shape=shape,
        stack=stack,
        modules=modules or [],
        author_name="Test Author",
        author_email="test@example.com",
        go_module="github.com/test-org/goldenapp" if stack == "go" else "",
        install_hooks=False,
        keep_examples=True,
    )
    run_init(root, config)
    return root


# ── Python Single ────────────────────────────────────────────────────────


class TestPythonSingleGolden:
    @pytest.fixture(autouse=True)
    def project(self, tmp_path: Path) -> None:
        self._root = _init(_scaffold_copy(tmp_path), shape="single", stack="python")

    def test_mise_toml_content(self) -> None:
        content = (self._root / ".mise.toml").read_text()
        assert 'SCAFFOLD_PROJECT_NAME  = "goldenapp"' in content
        assert 'SCAFFOLD_PROJECT_STACK = "python"' in content
        assert 'SCAFFOLD_PROJECT_SHAPE = "single"' in content
        assert 'python = "3.12"' in content
        assert 'uv = "latest"' in content

    def test_pyproject_toml_has_project_name(self) -> None:
        content = (self._root / "pyproject.toml").read_text()
        assert 'name = "goldenapp"' in content
        assert "pytest" in content

    def test_readme_has_project_name(self) -> None:
        content = (self._root / "README.md").read_text()
        assert "goldenapp" in content

    def test_agents_md_structure(self) -> None:
        content = (self._root / "AGENTS.md").read_text()
        assert "goldenapp" in content
        assert "## WHY" in content
        assert "## WHAT" in content
        assert "## HOW" in content

    def test_gitignore_has_python_entries(self) -> None:
        content = (self._root / ".gitignore").read_text()
        assert "__pycache__/" in content
        assert ".venv/" in content

    def test_ci_workflow_content(self) -> None:
        content = (self._root / ".github" / "workflows" / "ci.yml").read_text()
        assert "mise run ci" in content
        assert "mise run verify" in content
        assert "upload-artifact" in content

    def test_architecture_doc(self) -> None:
        content = (self._root / "docs" / "architecture.md").read_text()
        assert "Invariants" in content

    def test_adr_mentions_stack(self) -> None:
        content = (
            self._root / "docs" / "decisions" / "0001-stack-choice.md"
        ).read_text()
        assert "python" in content

    def test_scaffold_artifacts_removed(self) -> None:
        assert not (self._root / "stacks").exists()
        assert not (self._root / "templates").exists()
        assert not (self._root / "SPEC.md").exists()

    def test_agent_skills_generated(self) -> None:
        assert (self._root / ".agent" / "skills" / "README.md").exists()
        assert (
            self._root / ".agent" / "skills" / "example-skill" / "SKILL.md"
        ).exists()


# ── Python Apps ──────────────────────────────────────────────────────────


class TestPythonAppsGolden:
    @pytest.fixture(autouse=True)
    def project(self, tmp_path: Path) -> None:
        self._root = _init(
            _scaffold_copy(tmp_path),
            shape="apps",
            stack="python",
            modules=["api", "worker"],
        )

    def test_workspace_toml_structure(self) -> None:
        content = (self._root / "workspace.toml").read_text()
        assert "[modules.api]" in content
        assert "[modules.worker]" in content
        assert "apps/api" in content
        assert "apps/worker" in content

    def test_gitignore_exists(self) -> None:
        gi = self._root / ".gitignore"
        assert gi.exists()
        content = gi.read_text()
        assert "__pycache__/" in content

    def test_mise_toml_apps_shape(self) -> None:
        content = (self._root / ".mise.toml").read_text()
        assert 'SCAFFOLD_PROJECT_SHAPE = "apps"' in content

    def test_per_module_pyproject(self) -> None:
        for mod in ["api", "worker"]:
            pyproj = self._root / "apps" / mod / "pyproject.toml"
            assert pyproj.exists(), f"Missing pyproject.toml for {mod}"

    def test_scaffold_artifacts_removed(self) -> None:
        assert not (self._root / "stacks").exists()
        assert not (self._root / "templates").exists()


# ── Go Single ────────────────────────────────────────────────────────────


class TestGoSingleGolden:
    @pytest.fixture(autouse=True)
    def project(self, tmp_path: Path) -> None:
        self._root = _init(_scaffold_copy(tmp_path), shape="single", stack="go")

    def test_go_mod_content(self) -> None:
        content = (self._root / "go.mod").read_text()
        assert "github.com/test-org/goldenapp" in content

    def test_mise_toml_go_tools(self) -> None:
        content = (self._root / ".mise.toml").read_text()
        assert "go = " in content
        assert "gofumpt" in content
        assert "golangci-lint" in content

    def test_gitignore_has_go_entries(self) -> None:
        content = (self._root / ".gitignore").read_text()
        assert "bin/" in content

    def test_dockerfile_generated(self) -> None:
        assert (self._root / "Dockerfile").exists()

    def test_golangci_yml_generated(self) -> None:
        assert (self._root / ".golangci.yml").exists()

    def test_scaffold_artifacts_removed(self) -> None:
        assert not (self._root / "stacks").exists()
        assert not (self._root / "templates").exists()


# ── Go Apps ──────────────────────────────────────────────────────────────


class TestGoAppsGolden:
    @pytest.fixture(autouse=True)
    def project(self, tmp_path: Path) -> None:
        self._root = _init(
            _scaffold_copy(tmp_path),
            shape="apps",
            stack="go",
            modules=["svc-a", "svc-b"],
        )

    def test_workspace_toml(self) -> None:
        content = (self._root / "workspace.toml").read_text()
        assert "[modules.svc-a]" in content
        assert "[modules.svc-b]" in content

    def test_per_module_go_mod(self) -> None:
        for mod in ["svc-a", "svc-b"]:
            go_mod = self._root / "apps" / mod / "go.mod"
            assert go_mod.exists(), f"Missing go.mod for {mod}"

    def test_gitignore_exists(self) -> None:
        assert (self._root / ".gitignore").exists()

    def test_scaffold_artifacts_removed(self) -> None:
        assert not (self._root / "stacks").exists()
        assert not (self._root / "templates").exists()
