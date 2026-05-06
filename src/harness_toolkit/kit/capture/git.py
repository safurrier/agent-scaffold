"""Git inspection adapter for evidence capture."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_toolkit.kit.state.repo import git_branch


@dataclass(frozen=True)
class GitSnapshot:
    branch: str
    git_sha: str
    dirty: bool


def snapshot(path: Path, *, git_sha: str, dirty: bool) -> GitSnapshot:
    return GitSnapshot(branch=git_branch(path), git_sha=git_sha, dirty=dirty)
