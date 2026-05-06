from __future__ import annotations

import pytest

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.policy import lifecycle_phase, ready_for_events

pytestmark = pytest.mark.unit


def event(seq: int, kind: str, text: str) -> EventRecord:
    return EventRecord(
        schema_version=1,
        seq=seq,
        type="note_added",
        at="2026-01-01T00:00:00Z",
        data={"kind": kind, "text": text},
    )


def review(seq: int) -> EventRecord:
    return EventRecord(
        schema_version=1,
        seq=seq,
        type="review_added",
        at="2026-01-01T00:00:00Z",
        data={
            "backend": "codex",
            "reviewer": "codex-review",
            "rubrics": ["core-quality"],
            "summary": "Accepted.",
            "disposition": "accepted",
        },
    )


def evidence() -> EvidenceRecord:
    return EvidenceRecord(
        schema_version=1,
        id="evidence-1",
        type="command",
        capture_mode="argv",
        kind="test",
        command_display="python3 -c 'print(1)'",
        argv=["python3", "-c", "print(1)"],
        shell_command="",
        cwd=".",
        target=".",
        branch="feat/demo",
        git_sha="abc123",
        dirty_before=False,
        dirty_after=False,
        exit_code=0,
        status="pass",
        started_at="2026-01-01T00:00:00Z",
        ended_at="2026-01-01T00:00:01Z",
        duration_ms=1000,
        transcript_path="",
        redaction="default",
        why="proves parity",
    )


def test_readiness_policy_accepts_complete_lifecycle() -> None:
    events = [
        event(1, "plan", "Plan"),
        event(2, "decision", "Decision"),
        event(3, "spec-impact", "not-needed"),
        review(4),
    ]

    result = ready_for_events(
        work_id="work",
        events=events,
        evidence=[evidence()],
        sync_status="synced",
        check_handoff=True,
        handoff_check=lambda: None,
    )

    assert result.ready is True
    assert result.status == "ready"
    assert {check.id: check.status for check in result.checks}["review"] == "pass"
    assert lifecycle_phase(events, result) == "ready"


def test_readiness_policy_rejects_self_review() -> None:
    events = [
        event(1, "plan", "Plan"),
        event(2, "decision", "Decision"),
        event(3, "spec-impact", "not-needed"),
        EventRecord(
            schema_version=1,
            seq=4,
            type="review_added",
            at="2026-01-01T00:00:00Z",
            data={
                "backend": "self",
                "reviewer": "implementation-agent",
                "rubrics": ["core-quality"],
                "summary": "Looks good to me.",
                "disposition": "accepted",
            },
        ),
    ]

    result = ready_for_events(
        work_id="work",
        events=events,
        evidence=[evidence()],
        sync_status="synced",
    )

    review_check = {check.id: check for check in result.checks}["review"]
    assert result.ready is False
    assert review_check.status == "fail"
    assert "self-review" in review_check.message
