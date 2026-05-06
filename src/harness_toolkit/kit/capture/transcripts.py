"""Transcript path helpers for command evidence capture."""

from __future__ import annotations

from pathlib import Path


def transcript_path(work_dir: Path, evidence_id: str) -> Path:
    return work_dir / "artifacts" / f"{evidence_id}.transcript.log"
