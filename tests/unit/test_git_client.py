from __future__ import annotations

import ast
import os
import subprocess
from pathlib import Path

from harness_toolkit.kit.git.client import GitClient

ROOT = Path(__file__).resolve().parents[2]
KIT_ROOT = ROOT / "src" / "harness_toolkit" / "kit"


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    env |= {
        "GIT_AUTHOR_NAME": "Test",
        "GIT_AUTHOR_EMAIL": "test@example.com",
        "GIT_COMMITTER_NAME": "Test",
        "GIT_COMMITTER_EMAIL": "test@example.com",
    }
    return env


def _git_init(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, env=_git_env()
    )
    subprocess.run(
        ["git", "checkout", "-b", "main"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    (path / "README.md").write_text("# demo\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "initial"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )


def test_git_client_reports_worktree_info_for_file_target(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    worktree = tmp_path / "repo-worktree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        env=_git_env(),
    )

    info = GitClient().worktree_info(worktree / "README.md")

    assert info is not None
    assert info.repo_root == worktree.resolve()
    assert info.git_common_dir == (repo / ".git").resolve()


def test_git_client_clears_ambient_git_environment(tmp_path: Path, monkeypatch) -> None:
    repo = tmp_path / "repo"
    _git_init(repo)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "not-a-real-git-dir"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "not-a-real-work-tree"))

    assert GitClient().root(repo) == repo.resolve()


def test_kit_subprocess_execution_is_centralized() -> None:
    approved = {
        Path("capture/process.py"),
        Path("git/client.py"),
    }
    offenders: list[str] = []
    for path in sorted(KIT_ROOT.rglob("*.py")):
        relative = path.relative_to(KIT_ROOT)
        if relative in approved:
            continue
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            func = node.func
            if (
                isinstance(func, ast.Attribute)
                and func.attr in {"run", "Popen"}
                and isinstance(func.value, ast.Name)
                and func.value.id == "subprocess"
            ):
                offenders.append(f"{relative}:{node.lineno}: subprocess.{func.attr}")
    assert offenders == []
