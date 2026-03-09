"""E2E tests for the plan task."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from tests._docs_helpers import PLAN_REQUIRED_FILES, parse_meta_yaml, validate_meta_yaml
from tests._support import init_git_branch, init_project, mise, trust_mise

pytestmark = pytest.mark.e2e


def _find_plan_dirs(root: Path, slug: str) -> list[Path]:
    plans_dir = root / ".ai" / "plans"
    if not plans_dir.is_dir():
        return []
    return sorted(
        path
        for path in plans_dir.iterdir()
        if path.is_dir() and path.name.endswith(f"-{slug}")
    )


class TestPlanTaskInScaffoldRepo:
    def test_plan_creates_full_template_set(self, scaffold_copy: Path) -> None:
        init_git_branch(scaffold_copy, "feat/scaffold-plan-test")

        result = mise("plan", scaffold_copy, "scaffold-plan-happy-path", timeout=60)

        assert result.returncode == 0, (
            f"plan failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

        plan_dirs = _find_plan_dirs(scaffold_copy, "scaffold-plan-happy-path")
        assert len(plan_dirs) == 1

        plan_dir = plan_dirs[0]
        for filename in PLAN_REQUIRED_FILES:
            assert (plan_dir / filename).exists(), f"Missing plan file: {filename}"

        meta = parse_meta_yaml(plan_dir / "META.yaml")
        assert meta is not None
        assert meta.branch == "feat/scaffold-plan-test"
        errors = validate_meta_yaml(meta)
        assert not errors, f"Plan META.yaml errors: {'; '.join(errors)}"

    @pytest.mark.parametrize("slug", ["bad/slug", "Bad-Slug", "bad slug", "bad_slug"])
    def test_invalid_slug_rejected(self, scaffold_copy: Path, slug: str) -> None:
        init_git_branch(scaffold_copy, "feat/invalid-plan-slug")

        result = mise("plan", scaffold_copy, slug, timeout=60)

        assert result.returncode != 0
        assert "Invalid slug" in result.stderr

    def test_duplicate_slug_rejected(self, scaffold_copy: Path) -> None:
        init_git_branch(scaffold_copy, "feat/duplicate-plan-slug")

        first = mise("plan", scaffold_copy, "duplicate-plan-slug", timeout=60)
        second = mise("plan", scaffold_copy, "duplicate-plan-slug", timeout=60)

        assert first.returncode == 0, first.stderr
        assert second.returncode != 0
        assert "already exists" in second.stderr


class TestPlanTaskInGeneratedRepo:
    def test_plan_fails_on_default_branch(self, scaffold_copy: Path) -> None:
        result = init_project(
            scaffold_copy,
            name="plantest",
            shape="single",
            stack="python",
        )
        assert result.returncode == 0, result.stderr
        trust_mise(scaffold_copy)

        result = mise("plan", scaffold_copy, "generated-plan", timeout=60)

        assert result.returncode != 0
        assert "Create a feature branch" in result.stderr

    def test_plan_succeeds_on_feature_branch(self, scaffold_copy: Path) -> None:
        result = init_project(
            scaffold_copy,
            name="planfeaturetest",
            shape="single",
            stack="python",
        )
        assert result.returncode == 0, result.stderr
        trust_mise(scaffold_copy)
        result = mise("plan", scaffold_copy, "generated-plan", timeout=60)
        assert result.returncode != 0

        # The generated repo already has git metadata; switch to a feature branch.
        subprocess.run(
            ["git", "checkout", "-b", "feat/generated-plan"],
            cwd=scaffold_copy,
            check=True,
            capture_output=True,
        )

        result = mise("plan", scaffold_copy, "generated-plan", timeout=60)

        assert result.returncode == 0, (
            f"plan failed:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        )

        plan_dirs = _find_plan_dirs(scaffold_copy, "generated-plan")
        assert len(plan_dirs) == 1
        for filename in PLAN_REQUIRED_FILES:
            assert (plan_dirs[0] / filename).exists(), f"Missing plan file: {filename}"
