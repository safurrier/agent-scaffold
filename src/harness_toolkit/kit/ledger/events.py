"""Typed lifecycle event constructors for Harness Kit."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.ledger.models import EventRecord
from harness_toolkit.kit.ledger.store import append_event as store_append_event


def append_lifecycle_event(
    work_dir: Path, event_type: str, data: dict[str, object], *, schema_version: int
) -> EventRecord:
    return store_append_event(work_dir, event_type, data, schema_version=schema_version)
