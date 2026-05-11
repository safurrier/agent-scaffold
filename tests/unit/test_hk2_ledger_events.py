from __future__ import annotations

import json
from pathlib import Path

import pytest

from harness_toolkit.kit.ledger import lifecycle_events
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


def test_lifecycle_event_queries_hide_raw_payload_shape(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"
    append_event(
        work_dir,
        "note_added",
        {"kind": "plan", "text": "Use typed queries."},
        schema_version=1,
    )
    append_event(
        work_dir,
        "review_added",
        {
            "backend": "subagent",
            "reviewer": "fresh-context",
            "rubrics": ["core-quality"],
            "summary": "No blockers.",
            "disposition": "accepted",
            "review_name": "core-review",
        },
        schema_version=1,
    )
    append_event(
        work_dir,
        "dangerous_skip_added",
        {
            "check": "sync",
            "label": "agent-local",
            "reason": "Only local state.",
            "mitigation": "No source changes.",
            "event_seq": 2,
            "diff_hash": "sha256:abc",
        },
        schema_version=1,
    )
    append_event(
        work_dir,
        "artifact_attached",
        {
            "kind": "review-transcript",
            "label": "Review transcript",
            "source_path": "/tmp/review.md",
            "artifact_path": "artifacts/review.md",
            "sha256": "sha256:def",
            "size_bytes": 42,
            "copied": True,
            "redaction": "external",
        },
        schema_version=1,
    )
    append_event(
        work_dir,
        "sync_checkpoint",
        {
            "git_sha": "abc123",
            "diff_hash": "sha256:ghi",
            "event_seq": 4,
            "evidence_count": 0,
            "note_count": 1,
            "excluded_paths": [".pi"],
            "exclude_reason": "agent-local",
        },
        schema_version=1,
    )

    events = read_events(work_dir)

    assert lifecycle_events.note_texts(events, ("plan",)) == ["Use typed queries."]
    assert lifecycle_events.review_events(events)[0].review_name == "core-review"
    assert lifecycle_events.review_payloads(events)[0]["rubrics"] == ["core-quality"]
    assert lifecycle_events.dangerous_skip_events(events)[0].event_seq == 2
    assert lifecycle_events.artifact_events(events)[0].kind == "review-transcript"
    assert lifecycle_events.artifact_events(events)[0].size_bytes == 42
    assert lifecycle_events.sync_checkpoint_events(events)[0].excluded_paths == (".pi",)


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
