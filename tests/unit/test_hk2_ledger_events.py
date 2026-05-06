from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness_toolkit.kit.ledger.store import append_event, read_events, read_evidence

pytestmark = pytest.mark.unit


def test_typed_event_store_preserves_jsonl_shape(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"

    record = append_event(
        work_dir,
        "note_added",
        {"kind": "plan", "text": "Typed events preserve JSONL."},
        schema_version=1,
    )

    rows = [
        json.loads(line)
        for line in (work_dir / "events.jsonl").read_text().splitlines()
    ]
    assert rows == [
        {
            "schema_version": 1,
            "seq": record.seq,
            "type": "note_added",
            "at": record.at,
            "data": {"kind": "plan", "text": "Typed events preserve JSONL."},
        }
    ]
    assert read_events(work_dir) == [record]


def test_typed_evidence_reader_parses_existing_jsonl_shape(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    work_dir.mkdir()
    (work_dir / "evidence.jsonl").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "id": "evidence-1",
                "type": "command",
                "capture_mode": "argv",
                "kind": "test",
                "command_display": "python3 -c 'print(1)'",
                "argv": ["python3", "-c", "print(1)"],
                "shell_command": "",
                "cwd": str(tmp_path),
                "target": str(tmp_path),
                "branch": "feat/demo",
                "git_sha": "abc123",
                "dirty_before": False,
                "dirty_after": False,
                "exit_code": 0,
                "status": "pass",
                "started_at": "2026-01-01T00:00:00Z",
                "ended_at": "2026-01-01T00:00:01Z",
                "duration_ms": 1000,
                "transcript_path": "",
                "redaction": "default",
                "why": "parity",
            }
        )
        + "\n"
    )

    records = read_evidence(work_dir)

    assert len(records) == 1
    assert records[0].id == "evidence-1"
    assert records[0].why == "parity"
