"""E2E rollout checks for Harness Kit portable workflow.

These tests use synthetic repositories instead of cloning a real external project.
They prove the rollout contract we dogfooded manually: ``hk`` can attach to an
existing repo, create native-shaped plan state outside or beside the checkout,
and leave the target repository clean.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from tests._docs_helpers import PLAN_REQUIRED_FILES
from tests._support import SCAFFOLD_ROOT

pytestmark = pytest.mark.e2e


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    return env


def _git_init(path: Path) -> None:
    path.mkdir()
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, env=_git_env()
    )
    subprocess.run(
        ["git", "checkout", "-b", "feat/harness-kit-rollout"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    (path / "README.md").write_text("# synthetic target\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "chore: initial"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env()
        | {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


def _run_hk(*args: str, cwd: Path = SCAFFOLD_ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "hk", *args],
        cwd=cwd,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )


def _git_status(path: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        check=True,
        text=True,
        env=_git_env(),
    ).stdout


def _complete_portable_plan(plan_dir: Path) -> None:
    (plan_dir / "TODO.md").write_text("# TODO\n\n- [x] Prove portable rollout parity\n")
    (plan_dir / "DECISIONS.md").write_text(
        "# Decisions\n\n- Used Harness Kit portable workflow in a synthetic existing repo.\n"
    )
    (plan_dir / "VALIDATION.md").write_text(
        "# Validation\n\n- `git status --porcelain`\n  - Result: clean target repo.\n"
    )
    (plan_dir / "REVIEW.md").write_text(
        "# Review\n\n- External reviewer found no rollout parity blockers.\n"
    )


def test_harness_kit_external_mode_rollout_matches_plan_contract(
    tmp_path: Path,
) -> None:
    target = tmp_path / "existing-repo"
    _git_init(target)
    state_root = tmp_path / "hk-state"

    profiles = _run_hk("profile", "list", "--target", str(target), "--json")
    assert profiles.returncode == 0, profiles.stderr
    profile_payload = json.loads(profiles.stdout)
    assert {"generic", "python", "go", "rust", "rust-mise"} <= {
        row["name"] for row in profile_payload["profiles"]
    }

    plan = _run_hk(
        "plan",
        "rollout-parity",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--profile",
        "generic",
        "--json",
    )
    assert plan.returncode == 0, plan.stderr
    plan_payload = json.loads(plan.stdout)
    plan_dir = Path(plan_payload["plan_dir"])
    state_dir = Path(plan_payload["state_dir"])

    assert state_dir.is_relative_to(state_root)
    assert not (target / ".ai").exists()
    assert not (target / ".agent").exists()
    assert not (target / ".mise").exists()
    assert not (target / ".ai-local").exists()

    for required in PLAN_REQUIRED_FILES:
        assert (plan_dir / required).exists(), f"missing portable plan file: {required}"
        assert (
            SCAFFOLD_ROOT / "templates" / ".ai" / "plans" / "_templates" / required
        ).exists(), f"portable plan file lacks native template peer: {required}"

    checks = _run_hk(
        "checks", "--target", str(target), "--profile", "generic", "--json"
    )
    assert checks.returncode == 0, checks.stderr
    checks_payload = json.loads(checks.stdout)
    assert checks_payload["profile"] == "generic"
    assert any(check["command_template"] for check in checks_payload["checks"])
    assert _git_status(target) == ""

    _complete_portable_plan(plan_dir)
    sync = _run_hk(
        "sync-check",
        "--target",
        str(target),
        "--state-root",
        str(state_root),
        "--profile",
        "generic",
        "--json",
    )
    assert sync.returncode == 0, sync.stderr
    assert json.loads(sync.stdout)["checks"] == [
        "plan",
        "decisions",
        "validation",
        "review",
    ]
    assert _git_status(target) == ""


def test_harness_kit_overlay_mode_uses_local_exclude_without_tracked_files(
    tmp_path: Path,
) -> None:
    target = tmp_path / "existing-repo"
    _git_init(target)

    attach = _run_hk("attach", "--target", str(target), "--mode", "overlay", "--json")

    assert attach.returncode == 0, attach.stderr
    payload = json.loads(attach.stdout)
    state_dir = Path(payload["state_dir"])
    assert state_dir == target / ".ai-local" / "harness-kit" / "root"
    assert payload["ignored_by_local_git"] is True
    assert (
        "/.ai-local/harness-kit/" in (target / ".git" / "info" / "exclude").read_text()
    )
    assert _git_status(target) == ""

    plan = _run_hk(
        "plan",
        "overlay-parity",
        "--target",
        str(target),
        "--mode",
        "overlay",
        "--json",
    )
    assert plan.returncode == 0, plan.stderr
    plan_dir = Path(json.loads(plan.stdout)["plan_dir"])
    for required in PLAN_REQUIRED_FILES:
        assert (plan_dir / required).exists(), f"missing overlay plan file: {required}"
    assert _git_status(target) == ""
