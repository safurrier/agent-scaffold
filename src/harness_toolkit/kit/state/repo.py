"""Shared repository identity and git-state helpers for Harness Kit."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

from harness_toolkit.kit.git.client import DEFAULT_GIT_CLIENT

ROOT_SCOPE = "root"


class RepoStateError(RuntimeError):
    """Expected repository target resolution failure."""


def git_root(path: Path) -> Path:
    if not path.exists():
        raise RepoStateError(f"target does not exist: {path}")
    if not path.is_dir():
        raise RepoStateError(f"target is not a directory: {path}")
    result = DEFAULT_GIT_CLIENT.root_result(path)
    if result.returncode != 0:
        detail = result.stderr_text.strip() or "not a git repository"
        raise RepoStateError(
            f"target is not inside a git repository: {path} ({detail})"
        )
    return Path(result.stdout_text.strip()).resolve()


def git_branch(path: Path) -> str:
    return DEFAULT_GIT_CLIENT.branch(path)


def git_remote(path: Path) -> str:
    return DEFAULT_GIT_CLIENT.remote_origin_url(path)


def repo_key(target_root: Path) -> str:
    identity = git_remote(target_root) or str(target_root.resolve())
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
    safe_name = re.sub(
        r"[^a-zA-Z0-9_.-]+", "-", Path(identity).stem or target_root.name
    )
    return f"{safe_name}-{digest}"


def scope_key(target_root: Path, target_scope: Path) -> str:
    try:
        relative = target_scope.resolve().relative_to(target_root.resolve())
    except ValueError:
        return ROOT_SCOPE
    if str(relative) == ".":
        return ROOT_SCOPE
    raw = str(relative).strip().strip("/")
    if not raw:
        return ROOT_SCOPE
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw)
