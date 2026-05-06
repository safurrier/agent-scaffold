"""Binary Harness Kit lifecycle readiness policy."""

from __future__ import annotations

from collections.abc import Callable

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.diagnostics import ReadyCheck, ReadyResult

ACCEPTED_REVIEW_DISPOSITIONS = {
    "accepted",
    "approved",
    "pass",
    "passed",
    "no-blockers",
    "no blockers",
    "no-blocking-findings",
    "no_blocking_findings",
    "no-findings",
    "no_findings",
}
SELF_REVIEW_TOKENS = ("self", "same-agent", "implementation-agent", "worker-self")
SELF_REVIEW_GUIDANCE = (
    "review must be independent: preferred independent AI/tool reviewer; "
    "minimum fresh-context subagent; implementation-agent self-review does not count"
)


def notes_by_kind(events: list[EventRecord], kind: str) -> list[str]:
    return notes_by_kinds(events, (kind,))


def notes_by_kinds(events: list[EventRecord], kinds: tuple[str, ...]) -> list[str]:
    rows: list[str] = []
    for event in events:
        if event.type != "note_added":
            continue
        if event.data.get("kind") in kinds:
            rows.append(str(event.data.get("text", "")))
    return rows


def is_self_review_identity(value: str) -> bool:
    clean = value.strip().lower()
    if clean in {"", "self", "pending", "todo"}:
        return True
    return any(token in clean for token in SELF_REVIEW_TOKENS)


def review_events(events: list[EventRecord]) -> list[dict[str, object]]:
    return [event.data for event in events if event.type == "review_added"]


def accepted_review_events(events: list[EventRecord]) -> list[dict[str, object]]:
    accepted: list[dict[str, object]] = []
    for review in review_events(events):
        backend = str(review.get("backend", "")).strip().lower()
        reviewer = str(review.get("reviewer", "")).strip().lower()
        disposition = str(review.get("disposition", "")).strip().lower()
        if is_self_review_identity(backend):
            continue
        if is_self_review_identity(reviewer):
            continue
        if disposition not in ACCEPTED_REVIEW_DISPOSITIONS:
            continue
        accepted.append(review)
    return accepted


def dangerous_skip_events(
    events: list[EventRecord], check_id: str
) -> list[dict[str, object]]:
    return [
        event.data
        for event in events
        if event.type == "dangerous_skip_added" and event.data.get("check") == check_id
    ]


def ready_for_events(
    *,
    work_id: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    sync_status: str,
    agent_local_warning: str = "",
    check_handoff: bool = True,
    handoff_check: Callable[[], None] | None = None,
) -> ReadyResult:
    checks: list[ReadyCheck] = []

    def add_check(check_id: str, passed: bool, message: str) -> None:
        checks.append(
            ReadyCheck(
                id=check_id, status="pass" if passed else "fail", message=message
            )
        )

    context = notes_by_kinds(events, ("context", "background"))
    checks.append(
        ReadyCheck(
            id="context",
            status="info",
            message=(
                "context recorded"
                if context
                else "no context recorded; okay for trivial work, add hk context if it prevents rediscovery"
            ),
        )
    )
    add_check("plan", bool(notes_by_kind(events, "plan")), "plan recorded")
    has_decision = bool(notes_by_kind(events, "decision"))
    has_spec_reflection = bool(notes_by_kind(events, "spec-impact"))
    add_check(
        "decision",
        has_decision and has_spec_reflection,
        "decision and spec reflection recorded",
    )
    validation_skipped = bool(dangerous_skip_events(events, "validation"))
    passing_evidence_with_why = [
        record for record in evidence if record.why and record.status == "pass"
    ]
    failed_evidence_with_why = [
        record for record in evidence if record.why and record.status != "pass"
    ]
    add_check(
        "validation",
        bool(passing_evidence_with_why) or validation_skipped,
        "validation evidence with rationale recorded"
        if passing_evidence_with_why
        else "validation dangerously skipped"
        if validation_skipped
        else "validation evidence with rationale failed"
        if failed_evidence_with_why
        else "missing validation evidence with --why",
    )
    review_skipped = bool(dangerous_skip_events(events, "review"))
    reviews = accepted_review_events(events)
    recorded_reviews = review_events(events)
    add_check(
        "review",
        bool(reviews) or review_skipped,
        "external-enough review recorded"
        if reviews
        else "review dangerously skipped"
        if review_skipped
        else SELF_REVIEW_GUIDANCE
        if recorded_reviews
        else "missing accepted external-enough review record; run a separate reviewer/subagent with fresh context",
    )
    sync_skipped = sync_status == "sync-dangerously-skipped"
    synced = sync_status == "synced" or sync_skipped
    sync_message = (
        "sync checkpoint fresh"
        if sync_status == "synced"
        else "sync dangerously skipped"
        if sync_skipped
        else "sync checkpoint stale"
    )
    if not synced:
        sync_message += agent_local_warning
    add_check("sync", synced, sync_message)
    if check_handoff and handoff_check is not None:
        try:
            handoff_check()
        except Exception as e:  # pragma: no cover - defensive render check
            add_check("handoff", False, f"handoff render failed: {e}")
        else:
            add_check("handoff", True, "handoff renders")
    failed = [check for check in checks if check.status == "fail"]
    has_skips = bool(validation_skipped or review_skipped or sync_skipped)
    status = (
        "ready"
        if not failed and not has_skips
        else "ready-with-dangerous-skips"
        if not failed
        else "not-ready"
    )
    return ReadyResult(work_id=work_id, ready=not failed, status=status, checks=checks)


def lifecycle_phase(events: list[EventRecord], readiness: ReadyResult | None) -> str:
    if readiness is not None and readiness.ready:
        return "ready"
    has_plan = bool(notes_by_kind(events, "plan"))
    has_decision = bool(notes_by_kind(events, "decision")) and bool(
        notes_by_kind(events, "spec-impact")
    )
    has_validation = bool(
        readiness
        and any(
            check.id == "validation" and check.status == "pass"
            for check in readiness.checks
        )
    )
    has_review = bool(
        readiness
        and any(
            check.id == "review" and check.status == "pass"
            for check in readiness.checks
        )
    )
    if has_validation or has_review:
        return "finalizing"
    if has_plan and has_decision:
        return "implementing"
    return "planning"
