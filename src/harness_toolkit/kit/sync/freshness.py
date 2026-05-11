"""Sync checkpoint path normalization and exclusion metadata."""

from __future__ import annotations

from pathlib import Path
from typing import cast

from harness_toolkit.kit.git.snapshot import git_path_state_hash, git_status_for_path


class SyncFreshnessError(ValueError):
    """Raised when sync freshness inputs are invalid."""


def normalize_exclude_paths(exclude_paths: tuple[str | Path, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for path in exclude_paths:
        text = str(path).strip().replace("\\", "/")
        if not text:
            raise SyncFreshnessError("sync --exclude path cannot be empty")
        text = text.rstrip("/")
        if text in {"", "."}:
            raise SyncFreshnessError(
                "sync --exclude cannot exclude the repository root"
            )
        candidate = Path(text)
        if candidate.is_absolute():
            raise SyncFreshnessError("sync --exclude path must be relative")
        if ".." in candidate.parts:
            raise SyncFreshnessError("sync --exclude path cannot contain '..'")
        if text.startswith(":") or any(char in text for char in "*?["):
            raise SyncFreshnessError(
                "sync --exclude path must be a literal path, not a git pathspec"
            )
        normalized.append(text)
    return tuple(dict.fromkeys(normalized))


def excluded_path_metadata(
    path: Path, exclude_paths: tuple[str, ...]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in exclude_paths:
        status = git_status_for_path(path, candidate)
        rows.append(
            {
                "path": candidate,
                "status": status.strip(),
                "state_hash": git_path_state_hash(path, candidate),
            }
        )
    return rows


def excluded_path_state_changed(
    path: Path, recorded: object, *, expected_paths: tuple[str, ...] = ()
) -> bool:
    if not isinstance(recorded, list):
        return True
    rows: dict[str, str] = {}
    for item in recorded:
        if not isinstance(item, dict):
            return True
        row = cast("dict[object, object]", item)
        candidate = str(row.get("path") or "")
        recorded_hash = str(row.get("state_hash") or "")
        if not candidate or not recorded_hash:
            return True
        rows[candidate] = recorded_hash
    if expected_paths and set(rows) != set(expected_paths):
        return True
    for candidate, recorded_hash in rows.items():
        if git_path_state_hash(path, candidate) != recorded_hash:
            return True
    return False
