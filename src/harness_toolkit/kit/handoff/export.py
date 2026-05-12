"""Filesystem helpers for generated HK handoff exports."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


class HandoffExportError(RuntimeError):
    """Raised when writing a handoff export would be unsafe."""


def reject_symlink_ancestors(path: Path) -> None:
    for parent in path.parents:
        if parent == parent.parent:
            break
        if parent.exists() and parent.is_symlink():
            raise HandoffExportError(
                f"refusing export path with symlinked parent: {parent}"
            )


def prepare_generated_directory(path: Path) -> None:
    if path.is_symlink():
        path.unlink()
    path.mkdir(exist_ok=True)


def safe_write_generated_file(path: Path, content: str) -> None:
    """Write generated content without following an existing file symlink."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.is_symlink():
        path.unlink()
    if path.exists() and not path.is_file():
        raise HandoffExportError(f"refusing to overwrite non-file export path: {path}")
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w") as file_obj:
            file_obj.write(content)
        tmp_path.replace(path)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def safe_copy_generated_file(source: Path, destination: Path) -> None:
    """Copy generated binary/text content without following an existing symlink."""
    if source.is_symlink():
        raise HandoffExportError(f"refusing to copy symlinked export source: {source}")
    if not source.is_file():
        raise HandoffExportError(f"export artifact source is not a file: {source}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.is_symlink():
        destination.unlink()
    if destination.exists() and not destination.is_file():
        raise HandoffExportError(
            f"refusing to overwrite non-file export path: {destination}"
        )
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{destination.name}.", suffix=".tmp", dir=destination.parent
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as file_obj, source.open("rb") as source_obj:
            while chunk := source_obj.read(1024 * 1024):
                file_obj.write(chunk)
        tmp_path.replace(destination)
    finally:
        if tmp_path.exists():
            tmp_path.unlink()
