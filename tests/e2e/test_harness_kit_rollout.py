"""E2E rollout checks for Harness Kit 2 lifecycle behavior.

These tests use synthetic repositories instead of cloning a real external project.
They prove the rollout contract we dogfooded manually: ``hk`` can run the HK2
lifecycle in an existing repo, keep Harness Kit state local/ignored, and produce
readiness plus handoff output without legacy plan-artifact commands.
"""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

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


def test_harness_kit_lifecycle_rollout_reaches_ready(tmp_path: Path) -> None:
    target = tmp_path / "existing-repo"
    _git_init(target)

    profiles = _run_hk("profile", "list", "--target", str(target), "--json")
    assert profiles.returncode == 0, profiles.stderr
    profile_payload = json.loads(profiles.stdout)
    assert {"generic", "python", "go", "rust", "rust-mise"} <= {
        row["name"] for row in profile_payload["profiles"]
    }

    commands = [
        (
            "start",
            "rollout-parity",
            "--plan",
            "Exercise HK2 lifecycle rollout parity.",
            "--target",
            str(target),
        ),
        (
            "context",
            "Synthetic existing repo rollout; Harness Kit state must stay local.",
            "--target",
            str(target),
        ),
        (
            "decide",
            "No committed spec impact for synthetic rollout.",
            "--spec-impact",
            "not-needed",
            "--target",
            str(target),
        ),
        (
            "validate",
            "--why",
            "Native command evidence records rollout validation.",
            "--target",
            str(target),
            "--",
            "python3",
            "-c",
            "print('ok')",
        ),
        (
            "review",
            "add",
            "--backend",
            "subagent",
            "--reviewer",
            "rollout-fresh-context",
            "--rubric",
            "core-quality",
            "--summary",
            "Rollout parity accepted.",
            "--target",
            str(target),
        ),
        ("sync", "--target", str(target)),
    ]
    for command in commands:
        result = _run_hk(*command)
        assert result.returncode == 0, (command, result.stdout, result.stderr)

    ready = _run_hk("ready", "--target", str(target), "--json")
    assert ready.returncode == 0, ready.stderr
    assert json.loads(ready.stdout)["status"] == "ready"

    handoff = _run_hk("handoff", "--target", str(target))
    assert handoff.returncode == 0, handoff.stderr
    assert "## Validation evidence" in handoff.stdout
    assert "## Review" in handoff.stdout
    assert not (target / ".ai").exists()
    assert not (target / ".agent").exists()
    assert _git_status(target) == ""


def test_legacy_hk1_command_surfaces_are_removed(tmp_path: Path) -> None:
    target = tmp_path / "existing-repo"
    _git_init(target)

    root = _run_hk("--help")
    legacy = _run_hk("legacy", "plan", "rollout", "--target", str(target))
    attach = _run_hk("attach", "--target", str(target))
    status_mode = _run_hk("status", "--target", str(target), "--mode", "overlay")

    assert root.returncode == 0
    assert "legacy" not in root.stdout.lower()
    assert "attach" not in root.stdout.lower()
    assert legacy.returncode != 0
    assert attach.returncode != 0
    assert status_mode.returncode != 0
    assert _git_status(target) == ""
