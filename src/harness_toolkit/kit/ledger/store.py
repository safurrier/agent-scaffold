"""JSONL-backed ledger store for Harness Kit lifecycle events and evidence."""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord


class LedgerStoreError(RuntimeError):
    """Raised when persisted ledger JSONL cannot be read safely."""


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _shape_error(path: Path, line_number: int, kind: str) -> LedgerStoreError:
    return LedgerStoreError(
        f"Malformed {kind} JSONL in {path} at line {line_number}: invalid {kind} shape"
    )


def _object_row(
    path: Path, line_number: int, row: object, kind: str
) -> dict[str, object]:
    if not isinstance(row, dict):
        raise _shape_error(path, line_number, kind)
    return cast("dict[str, object]", row)


def _required_int(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> int:
    value = data.get(key)
    if not isinstance(value, int) or isinstance(value, bool):
        raise _shape_error(path, line_number, kind)
    return value


def _required_str(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> str:
    value = data.get(key)
    if not isinstance(value, str):
        raise _shape_error(path, line_number, kind)
    return value


def _optional_str(
    data: dict[str, object],
    key: str,
    *,
    path: Path,
    line_number: int,
    kind: str,
    default: str = "",
) -> str:
    if key not in data:
        return default
    return _required_str(data, key, path=path, line_number=line_number, kind=kind)


def _required_bool(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> bool:
    value = data.get(key)
    if not isinstance(value, bool):
        raise _shape_error(path, line_number, kind)
    return value


def _required_str_list(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> list[str]:
    value = data.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise _shape_error(path, line_number, kind)
    return [str(item) for item in cast("list[str]", value)]


def _optional_str_list(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> list[str]:
    if key not in data:
        return []
    return _required_str_list(data, key, path=path, line_number=line_number, kind=kind)


def _optional_list(
    data: dict[str, object], key: str, *, path: Path, line_number: int, kind: str
) -> list[object]:
    if key not in data:
        return []
    value = data.get(key)
    if not isinstance(value, list):
        raise _shape_error(path, line_number, kind)
    return cast("list[object]", value)


def _validate_event_payload(
    event_type: str, event_data: dict[str, object], *, path: Path, line_number: int
) -> dict[str, object]:
    kind = "ledger"
    if event_type == "work_started":
        _required_str(event_data, "slug", path=path, line_number=line_number, kind=kind)
        _required_str(
            event_data, "target_root", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "target_scope", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "branch", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "git_sha", path=path, line_number=line_number, kind=kind
        )
    elif event_type == "note_added":
        _required_str(event_data, "kind", path=path, line_number=line_number, kind=kind)
        _required_str(event_data, "text", path=path, line_number=line_number, kind=kind)
    elif event_type == "command_captured":
        _required_str(
            event_data, "evidence_id", path=path, line_number=line_number, kind=kind
        )
        _required_int(
            event_data, "exit_code", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "status", path=path, line_number=line_number, kind=kind
        )
        _optional_str(event_data, "why", path=path, line_number=line_number, kind=kind)
    elif event_type == "sync_checkpoint":
        _required_str(
            event_data, "git_sha", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "diff_hash", path=path, line_number=line_number, kind=kind
        )
        _required_int(
            event_data, "event_seq", path=path, line_number=line_number, kind=kind
        )
        _required_int(
            event_data, "evidence_count", path=path, line_number=line_number, kind=kind
        )
        _required_int(
            event_data, "note_count", path=path, line_number=line_number, kind=kind
        )
        _optional_str_list(
            event_data, "excluded_paths", path=path, line_number=line_number, kind=kind
        )
        _optional_str(
            event_data, "exclude_reason", path=path, line_number=line_number, kind=kind
        )
        _optional_list(
            event_data, "excluded", path=path, line_number=line_number, kind=kind
        )
    elif event_type == "review_added":
        _required_str(
            event_data, "backend", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "reviewer", path=path, line_number=line_number, kind=kind
        )
        _optional_str_list(
            event_data, "rubrics", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "summary", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "disposition", path=path, line_number=line_number, kind=kind
        )
    elif event_type == "artifact_attached":
        _required_str(event_data, "kind", path=path, line_number=line_number, kind=kind)
        _optional_str(
            event_data, "label", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "source_path", path=path, line_number=line_number, kind=kind
        )
        _optional_str(
            event_data, "artifact_path", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "sha256", path=path, line_number=line_number, kind=kind
        )
        _required_int(
            event_data, "size_bytes", path=path, line_number=line_number, kind=kind
        )
        _required_bool(
            event_data, "copied", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "redaction", path=path, line_number=line_number, kind=kind
        )
    elif event_type == "dangerous_skip_added":
        _required_str(
            event_data, "check", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "label", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "reason", path=path, line_number=line_number, kind=kind
        )
        _required_str(
            event_data, "mitigation", path=path, line_number=line_number, kind=kind
        )
        if "event_seq" in event_data:
            _required_int(
                event_data, "event_seq", path=path, line_number=line_number, kind=kind
            )
        if "diff_hash" in event_data:
            _required_str(
                event_data, "diff_hash", path=path, line_number=line_number, kind=kind
            )
        if "git_sha" in event_data:
            _required_str(
                event_data, "git_sha", path=path, line_number=line_number, kind=kind
            )
    return event_data


def parse_event_row(
    data: dict[str, object], *, path: Path, line_number: int
) -> EventRecord:
    event_data = data.get("data")
    if not isinstance(event_data, dict):
        raise _shape_error(path, line_number, "ledger")
    event_type = _required_str(
        data, "type", path=path, line_number=line_number, kind="ledger"
    )
    typed_event_data = _validate_event_payload(
        event_type,
        cast("dict[str, object]", event_data),
        path=path,
        line_number=line_number,
    )
    return EventRecord(
        schema_version=_required_int(
            data, "schema_version", path=path, line_number=line_number, kind="ledger"
        ),
        seq=_required_int(
            data, "seq", path=path, line_number=line_number, kind="ledger"
        ),
        type=event_type,
        at=_required_str(data, "at", path=path, line_number=line_number, kind="ledger"),
        data=typed_event_data,
    )


def next_seq(events_path: Path) -> int:
    if not events_path.exists():
        return 1
    seq = 0
    for line_number, line in enumerate(events_path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            raise LedgerStoreError(
                f"Malformed ledger JSONL in {events_path} at line {line_number}: {e.msg}"
            ) from e
        event = parse_event_row(
            _object_row(events_path, line_number, row, "ledger"),
            path=events_path,
            line_number=line_number,
        )
        seq = max(seq, event.seq)
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
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            raise LedgerStoreError(
                f"Malformed ledger JSONL in {path} at line {line_number}: {e.msg}"
            ) from e
        events.append(
            parse_event_row(
                _object_row(path, line_number, row, "ledger"),
                path=path,
                line_number=line_number,
            )
        )
    return events


def parse_evidence(
    data: dict[str, object], *, path: Path, line_number: int
) -> EvidenceRecord:
    kind = "evidence"
    return EvidenceRecord(
        schema_version=_required_int(
            data, "schema_version", path=path, line_number=line_number, kind=kind
        ),
        id=_required_str(data, "id", path=path, line_number=line_number, kind=kind),
        type=_required_str(data, "type", path=path, line_number=line_number, kind=kind),
        capture_mode=_required_str(
            data, "capture_mode", path=path, line_number=line_number, kind=kind
        ),
        kind=_required_str(data, "kind", path=path, line_number=line_number, kind=kind),
        command_display=_required_str(
            data, "command_display", path=path, line_number=line_number, kind=kind
        ),
        argv=_required_str_list(
            data, "argv", path=path, line_number=line_number, kind=kind
        ),
        shell_command=_optional_str(
            data, "shell_command", path=path, line_number=line_number, kind=kind
        ),
        cwd=_required_str(data, "cwd", path=path, line_number=line_number, kind=kind),
        target=_required_str(
            data, "target", path=path, line_number=line_number, kind=kind
        ),
        branch=_required_str(
            data, "branch", path=path, line_number=line_number, kind=kind
        ),
        git_sha=_required_str(
            data, "git_sha", path=path, line_number=line_number, kind=kind
        ),
        dirty_before=_required_bool(
            data, "dirty_before", path=path, line_number=line_number, kind=kind
        ),
        dirty_after=_required_bool(
            data, "dirty_after", path=path, line_number=line_number, kind=kind
        ),
        exit_code=_required_int(
            data, "exit_code", path=path, line_number=line_number, kind=kind
        ),
        status=_required_str(
            data, "status", path=path, line_number=line_number, kind=kind
        ),
        started_at=_required_str(
            data, "started_at", path=path, line_number=line_number, kind=kind
        ),
        ended_at=_required_str(
            data, "ended_at", path=path, line_number=line_number, kind=kind
        ),
        duration_ms=_required_int(
            data, "duration_ms", path=path, line_number=line_number, kind=kind
        ),
        transcript_path=_required_str(
            data, "transcript_path", path=path, line_number=line_number, kind=kind
        ),
        redaction=_required_str(
            data, "redaction", path=path, line_number=line_number, kind=kind
        ),
        why=_optional_str(data, "why", path=path, line_number=line_number, kind=kind),
        check_name=_optional_str(
            data, "check_name", path=path, line_number=line_number, kind=kind
        ),
        diff_hash=_optional_str(
            data, "diff_hash", path=path, line_number=line_number, kind=kind
        ),
        changed_paths=_optional_str_list(
            data, "changed_paths", path=path, line_number=line_number, kind=kind
        ),
        timed_out=data.get("timed_out") is True,
        truncated=data.get("truncated") is True,
        transcript_bytes=_required_int(
            data, "transcript_bytes", path=path, line_number=line_number, kind=kind
        )
        if "transcript_bytes" in data
        else 0,
    )


def read_evidence(work_dir: Path) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    path = work_dir / "evidence.jsonl"
    if not path.exists():
        return records
    for line_number, line in enumerate(path.read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError as e:
            raise LedgerStoreError(
                f"Malformed evidence JSONL in {path} at line {line_number}: {e.msg}"
            ) from e
        records.append(
            parse_evidence(
                _object_row(path, line_number, row, "evidence"),
                path=path,
                line_number=line_number,
            )
        )
    return records
