"""Typed queries over Harness Kit lifecycle event records.

The JSONL ledger stays intentionally simple; this module is the seam that keeps
readiness and rendering code from knowing raw event payload keys.
"""

from __future__ import annotations

from dataclasses import dataclass

from harness_toolkit.kit.ledger.models import EventRecord


@dataclass(frozen=True)
class NoteEvent:
    kind: str
    text: str


@dataclass(frozen=True)
class ReviewEvent:
    backend: str
    reviewer: str
    rubrics: tuple[str, ...]
    summary: str
    disposition: str
    review_name: str = ""

    def as_payload(self) -> dict[str, object]:
        return {
            "backend": self.backend,
            "reviewer": self.reviewer,
            "rubrics": list(self.rubrics),
            "summary": self.summary,
            "disposition": self.disposition,
            "review_name": self.review_name,
        }


@dataclass(frozen=True)
class DangerousSkipEvent:
    check: str
    label: str
    reason: str
    mitigation: str
    event_seq: int | None = None
    diff_hash: str = ""

    def as_payload(self) -> dict[str, object]:
        payload: dict[str, object] = {
            "check": self.check,
            "label": self.label,
            "reason": self.reason,
            "mitigation": self.mitigation,
        }
        if self.event_seq is not None:
            payload["event_seq"] = self.event_seq
        if self.diff_hash:
            payload["diff_hash"] = self.diff_hash
        return payload


@dataclass(frozen=True)
class ArtifactEvent:
    kind: str
    label: str
    source_path: str
    artifact_path: str
    sha256: str
    size_bytes: int
    copied: bool
    redaction: str

    def as_payload(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "label": self.label,
            "source_path": self.source_path,
            "artifact_path": self.artifact_path,
            "sha256": self.sha256,
            "size_bytes": self.size_bytes,
            "copied": self.copied,
            "redaction": self.redaction,
        }


@dataclass(frozen=True)
class SyncCheckpointEvent:
    excluded_paths: tuple[str, ...]
    exclude_reason: str

    def as_payload(self) -> dict[str, object]:
        return {
            "excluded_paths": list(self.excluded_paths),
            "exclude_reason": self.exclude_reason,
        }


def _str(value: object) -> str:
    return value if isinstance(value, str) else "" if value is None else str(value)


def _str_tuple(value: object) -> tuple[str, ...]:
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def _optional_int(value: object) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) else None


def _int(value: object, default: int = 0) -> int:
    parsed = _optional_int(value)
    return default if parsed is None else parsed


def note_events(events: list[EventRecord]) -> list[NoteEvent]:
    return [
        NoteEvent(kind=_str(event.data.get("kind")), text=_str(event.data.get("text")))
        for event in events
        if event.type == "note_added"
    ]


def note_texts(events: list[EventRecord], kinds: tuple[str, ...]) -> list[str]:
    return [note.text for note in note_events(events) if note.kind in kinds]


def review_events(events: list[EventRecord]) -> list[ReviewEvent]:
    return [
        ReviewEvent(
            backend=_str(event.data.get("backend")),
            reviewer=_str(event.data.get("reviewer")),
            rubrics=_str_tuple(event.data.get("rubrics")),
            summary=_str(event.data.get("summary")),
            disposition=_str(event.data.get("disposition")),
            review_name=_str(event.data.get("review_name")),
        )
        for event in events
        if event.type == "review_added"
    ]


def review_payloads(events: list[EventRecord]) -> list[dict[str, object]]:
    return [review.as_payload() for review in review_events(events)]


def dangerous_skip_events(events: list[EventRecord]) -> list[DangerousSkipEvent]:
    return [
        DangerousSkipEvent(
            check=_str(event.data.get("check")),
            label=_str(event.data.get("label")),
            reason=_str(event.data.get("reason")),
            mitigation=_str(event.data.get("mitigation")),
            event_seq=_optional_int(event.data.get("event_seq")),
            diff_hash=_str(event.data.get("diff_hash")),
        )
        for event in events
        if event.type == "dangerous_skip_added"
    ]


def dangerous_skip_payloads(events: list[EventRecord]) -> list[dict[str, object]]:
    return [skip.as_payload() for skip in dangerous_skip_events(events)]


def artifact_events(events: list[EventRecord]) -> list[ArtifactEvent]:
    return [
        ArtifactEvent(
            kind=_str(event.data.get("kind")),
            label=_str(event.data.get("label")),
            source_path=_str(event.data.get("source_path")),
            artifact_path=_str(event.data.get("artifact_path")),
            sha256=_str(event.data.get("sha256")),
            size_bytes=_int(event.data.get("size_bytes")),
            copied=bool(event.data.get("copied")),
            redaction=_str(event.data.get("redaction")),
        )
        for event in events
        if event.type == "artifact_attached"
    ]


def artifact_payloads(events: list[EventRecord]) -> list[dict[str, object]]:
    return [artifact.as_payload() for artifact in artifact_events(events)]


def sync_checkpoint_events(events: list[EventRecord]) -> list[SyncCheckpointEvent]:
    return [
        SyncCheckpointEvent(
            excluded_paths=_str_tuple(event.data.get("excluded_paths")),
            exclude_reason=_str(event.data.get("exclude_reason")),
        )
        for event in events
        if event.type == "sync_checkpoint"
    ]
