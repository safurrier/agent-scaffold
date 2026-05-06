"""Readiness diagnostics shared by ready, status, and rendering."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReadyCheck:
    id: str
    status: str
    message: str


@dataclass(frozen=True)
class ReadyResult:
    work_id: str
    ready: bool
    status: str
    checks: list[ReadyCheck]
