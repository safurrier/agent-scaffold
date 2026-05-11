"""Git worktree snapshot and diff-hash helpers for Harness Kit."""

from __future__ import annotations

import hashlib
import os
import stat
import subprocess
from pathlib import Path


def git_sha(path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def git_dirty(path: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return bool(result.stdout.strip()) if result.returncode == 0 else False


def agent_local_state_paths(path: Path, candidates: tuple[str, ...]) -> list[str]:
    """Return common agent-local paths that are currently part of git status."""
    present: list[str] = []
    for candidate in candidates:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", candidate],
            cwd=path,
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            present.append(candidate)
    return present


def git_pathspec_excludes(exclude_paths: tuple[str, ...] = ()) -> list[str]:
    return [f":(exclude){path}" for path in exclude_paths]


def git_tracked_paths_for_path(path: Path, candidate: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", candidate],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def git_status_for_path(path: Path, candidate: str) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", candidate],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def sync_exclude_safety_error(path: Path, candidate: str) -> str:
    tracked = git_tracked_paths_for_path(path, candidate)
    if tracked:
        return (
            "sync --exclude only supports untracked local-only paths; "
            f"refusing tracked paths or descendants under {candidate}: {', '.join(tracked[:3])}"
        )
    status = git_status_for_path(path, candidate).strip()
    if not status:
        return f"sync --exclude path is not present in git status: {candidate}"
    if any(not line.startswith("?? ") for line in status.splitlines()):
        return (
            "sync --exclude only supports untracked local-only paths; "
            f"refusing tracked or staged path: {candidate}"
        )
    return ""


def _hash_regular_file(hasher, full_path: Path) -> None:
    try:
        with full_path.open("rb") as file_obj:
            for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                hasher.update(chunk)
    except OSError:
        hasher.update(b"<unreadable>")


def _hash_directory_contents(hasher, root: Path) -> None:
    for current_root, dir_names, file_names in os.walk(root):
        dir_names.sort()
        file_names.sort()
        current = Path(current_root)
        try:
            relative_root = current.relative_to(root)
        except ValueError:
            relative_root = current
        hasher.update(b"dir-entry\0")
        hasher.update(str(relative_root).encode("utf-8", "surrogateescape"))
        hasher.update(b"\0")
        for file_name in file_names:
            full_path = current / file_name
            relative = full_path.relative_to(root)
            hasher.update(b"dir-file\0")
            hasher.update(str(relative).encode("utf-8", "surrogateescape"))
            hasher.update(b"\0")
            try:
                stat_result = full_path.lstat()
            except OSError:
                hasher.update(b"<missing>")
                hasher.update(b"\0")
                continue
            hasher.update(str(stat_result.st_mode).encode("ascii"))
            hasher.update(b"\0")
            if stat.S_ISLNK(stat_result.st_mode):
                try:
                    hasher.update(
                        os.readlink(full_path).encode("utf-8", "surrogateescape")
                    )
                except OSError:
                    hasher.update(b"<unreadable-symlink>")
            elif stat.S_ISREG(stat_result.st_mode):
                _hash_regular_file(hasher, full_path)
            hasher.update(b"\0")


def _hash_untracked_paths(hasher, path: Path, pathspec: list[str]) -> None:
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z", *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
    )
    if untracked.returncode != 0:
        return
    for raw_name in untracked.stdout.split(b"\0"):
        if not raw_name:
            continue
        relative = Path(raw_name.decode("utf-8", errors="surrogateescape"))
        full_path = path / relative
        hasher.update(b"untracked\0")
        hasher.update(raw_name)
        hasher.update(b"\0")
        try:
            stat_result = full_path.lstat()
        except OSError:
            hasher.update(b"<missing>")
            hasher.update(b"\0")
            continue
        hasher.update(str(stat_result.st_mode).encode("ascii"))
        hasher.update(b"\0")
        if stat.S_ISLNK(stat_result.st_mode):
            hasher.update(b"symlink\0")
            try:
                hasher.update(os.readlink(full_path).encode("utf-8", "surrogateescape"))
            except OSError:
                hasher.update(b"<unreadable-symlink>")
        elif stat.S_ISREG(stat_result.st_mode):
            hasher.update(b"file\0")
            _hash_regular_file(hasher, full_path)
        elif stat.S_ISDIR(stat_result.st_mode):
            hasher.update(b"dir\0")
            _hash_directory_contents(hasher, full_path)
        hasher.update(b"\0")


def git_diff_hash(path: Path, exclude_paths: tuple[str, ...] = ()) -> str:
    """Hash unstaged, staged, and status state for sync freshness."""
    hasher = hashlib.sha256()
    pathspec = (
        ["--", ".", *git_pathspec_excludes(exclude_paths)] if exclude_paths else []
    )
    commands = (
        ["git", "diff", "--no-ext-diff", "--binary", *pathspec],
        ["git", "diff", "--cached", "--no-ext-diff", "--binary", *pathspec],
        ["git", "status", "--porcelain", *pathspec],
    )
    for command in commands:
        result = subprocess.run(
            command,
            cwd=path,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        hasher.update("\0".join(command).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(result.stdout)
        hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def git_validation_diff_hash(path: Path, exclude_paths: tuple[str, ...] = ()) -> str:
    """Hash current worktree content for validation/review freshness.

    Unlike sync checkpoint hashing, this intentionally does not include the exact
    Git command argv in the digest. Adding a new exclude for generated/local-only
    files should not stale validation that covered the same source diff.
    """
    hasher = hashlib.sha256()
    pathspec = (
        ["--", ".", *git_pathspec_excludes(exclude_paths)] if exclude_paths else []
    )
    commands = (
        (b"diff", ["git", "diff", "--no-ext-diff", "--binary", *pathspec]),
        (
            b"cached-diff",
            ["git", "diff", "--cached", "--no-ext-diff", "--binary", *pathspec],
        ),
        (b"status", ["git", "status", "--porcelain", *pathspec]),
    )
    for label, command in commands:
        result = subprocess.run(command, cwd=path, capture_output=True, check=False)
        if result.returncode != 0:
            return ""
        hasher.update(label)
        hasher.update(b"\0")
        hasher.update(result.stdout)
        hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def _hash_worktree_path(hasher, root: Path, relative_text: str) -> None:
    full_path = root / relative_text
    hasher.update(b"worktree-path\0")
    hasher.update(relative_text.encode("utf-8", "surrogateescape"))
    hasher.update(b"\0")
    try:
        stat_result = full_path.lstat()
    except OSError:
        hasher.update(b"deleted\0")
        return
    hasher.update(str(stat_result.st_mode).encode("ascii"))
    hasher.update(b"\0")
    if stat.S_ISLNK(stat_result.st_mode):
        hasher.update(b"symlink\0")
        try:
            hasher.update(os.readlink(full_path).encode("utf-8", "surrogateescape"))
        except OSError:
            hasher.update(b"<unreadable-symlink>")
    elif stat.S_ISREG(stat_result.st_mode):
        hasher.update(b"file\0")
        _hash_regular_file(hasher, full_path)
    elif stat.S_ISDIR(stat_result.st_mode):
        hasher.update(b"dir\0")
        _hash_directory_contents(hasher, full_path)
    hasher.update(b"\0")


def git_validation_work_diff_hash(
    path: Path, *, base_sha: str, exclude_paths: tuple[str, ...] = ()
) -> str:
    """Hash active work content for validation/review freshness.

    The digest is path/content based instead of diff-output based so an unchanged
    validated file remains fresh after moving from unstaged/staged/untracked to
    committed representation.
    """
    if not base_sha.strip():
        return git_validation_diff_hash(path, exclude_paths)
    pathspec = ["--", ".", *git_pathspec_excludes(exclude_paths)]
    diff_result = subprocess.run(
        ["git", "diff", "--name-only", base_sha, *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if diff_result.returncode != 0:
        return ""
    untracked_result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if untracked_result.returncode != 0:
        return ""
    changed_paths = {
        line.strip().replace("\\", "/")
        for line in (
            *diff_result.stdout.splitlines(),
            *untracked_result.stdout.splitlines(),
        )
        if line.strip()
    }
    hasher = hashlib.sha256()
    hasher.update(b"validation-worktree\0")
    for relative_text in sorted(changed_paths):
        _hash_worktree_path(hasher, path, relative_text)
    return "sha256:" + hasher.hexdigest()


def git_work_diff_hash(
    path: Path, *, base_sha: str, exclude_paths: tuple[str, ...] = ()
) -> str:
    """Hash the work diff from the HK work start SHA to the current tree."""
    if not base_sha.strip():
        return git_diff_hash(path, exclude_paths)
    hasher = hashlib.sha256()
    pathspec = ["--", ".", *git_pathspec_excludes(exclude_paths)]
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--binary", base_sha, *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    hasher.update(b"work-diff\0")
    hasher.update(base_sha.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(result.stdout)
    hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def git_path_state_hash(path: Path, candidate: str) -> str:
    """Hash a literal untracked path's visible Git state and file contents."""
    hasher = hashlib.sha256()
    pathspec = ["--", candidate]
    commands = (
        ["git", "diff", "--no-ext-diff", "--binary", *pathspec],
        ["git", "diff", "--cached", "--no-ext-diff", "--binary", *pathspec],
        ["git", "status", "--porcelain", *pathspec],
    )
    for command in commands:
        result = subprocess.run(command, cwd=path, capture_output=True, check=False)
        if result.returncode != 0:
            return ""
        hasher.update("\0".join(command).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(result.stdout)
        hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def status_changed_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.endswith("/"):
            continue
        paths.append(path)
    return paths


def diff_changed_paths(root: Path, base_sha: str) -> list[str]:
    if not base_sha.strip():
        return []
    result = subprocess.run(
        ["git", "diff", "--name-only", base_sha, "--"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def untracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]
