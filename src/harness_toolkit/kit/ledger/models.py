"""Typed ledger records for Harness Kit JSONL state."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class EventRecord:
    schema_version: int
    seq: int
    type: str
    at: str
    data: dict[str, object]


@dataclass(frozen=True)
class EvidenceRecord:
    schema_version: int
    id: str
    type: str
    capture_mode: str
    kind: str
    command_display: str
    argv: list[str]
    shell_command: str
    cwd: str
    target: str
    branch: str
    git_sha: str
    dirty_before: bool
    dirty_after: bool
    exit_code: int
    status: str
    started_at: str
    ended_at: str
    duration_ms: int
    transcript_path: str
    redaction: str
    why: str = ""
    check_name: str = ""
    diff_hash: str = ""
    changed_paths: list[str] | None = None
