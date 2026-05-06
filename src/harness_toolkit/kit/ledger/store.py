"""JSONL-backed ledger store for HK2 lifecycle events and evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def next_seq(events_path: Path) -> int:
    if not events_path.exists():
        return 1
    seq = 0
    for line in events_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        value = row.get("seq")
        if isinstance(value, int):
            seq = max(seq, value)
    return seq + 1


def append_event(
    work_dir: Path,
    event_type: str,
    data: dict[str, object],
    *,
    schema_version: int,
) -> EventRecord:
    events_path = work_dir / "events.jsonl"
    seq = next_seq(events_path)
    record = EventRecord(
        schema_version=schema_version,
        seq=seq,
        type=event_type,
        at=utc_now(),
        data=data,
    )
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a") as file:
        file.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record


def read_events(work_dir: Path) -> list[EventRecord]:
    events: list[EventRecord] = []
    path = work_dir / "events.jsonl"
    if not path.exists():
        return events
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        events.append(
            EventRecord(
                schema_version=int(data["schema_version"]),
                seq=int(data["seq"]),
                type=str(data["type"]),
                at=str(data["at"]),
                data=dict(data.get("data", {})),
            )
        )
    return events


def _int_field(data: dict[str, object], key: str) -> int:
    value = data[key]
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    raise TypeError(f"field {key} must be int-compatible")


def _string_list_field(data: dict[str, object], key: str) -> list[str]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return []
    return [str(item) for item in cast("list[object]", value)]


def parse_evidence(data: dict[str, object]) -> EvidenceRecord:
    return EvidenceRecord(
        schema_version=_int_field(data, "schema_version"),
        id=str(data["id"]),
        type=str(data["type"]),
        capture_mode=str(data["capture_mode"]),
        kind=str(data["kind"]),
        command_display=str(data["command_display"]),
        argv=_string_list_field(data, "argv"),
        shell_command=str(data.get("shell_command", "")),
        cwd=str(data["cwd"]),
        target=str(data["target"]),
        branch=str(data["branch"]),
        git_sha=str(data["git_sha"]),
        dirty_before=bool(data["dirty_before"]),
        dirty_after=bool(data["dirty_after"]),
        exit_code=_int_field(data, "exit_code"),
        status=str(data["status"]),
        started_at=str(data["started_at"]),
        ended_at=str(data["ended_at"]),
        duration_ms=_int_field(data, "duration_ms"),
        transcript_path=str(data["transcript_path"]),
        redaction=str(data["redaction"]),
        why=str(data.get("why", "")),
    )


def read_evidence(work_dir: Path) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    path = work_dir / "evidence.jsonl"
    if not path.exists():
        return records
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        records.append(parse_evidence(json.loads(line)))
    return records
