"""Binary Harness Kit lifecycle readiness policy."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

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


@dataclass(frozen=True)
class RequiredProfileItem:
    name: str
    purpose: str
    matched_paths: tuple[str, ...]


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


def dangerous_skip_message(check_id: str, skips: list[dict[str, object]]) -> str:
    latest = skips[-1] if skips else {}
    label = str(latest.get("label") or "unlabeled")
    reason = str(latest.get("reason") or "")
    mitigation = str(latest.get("mitigation") or "")
    reason_text = f"; reason: {reason}" if reason else ""
    mitigation_text = f"; mitigation: {mitigation}" if mitigation else ""
    return f"{check_id} dangerously skipped: {label}{reason_text}{mitigation_text}"


def dangerous_skip_for_label(
    events: list[EventRecord], check_id: str, label: str
) -> list[dict[str, object]]:
    return [
        skip
        for skip in dangerous_skip_events(events, check_id)
        if str(skip.get("label") or "") == label
    ]


def _paths_text(paths: tuple[str, ...]) -> str:
    if not paths:
        return "changed path matched profile rule"
    preview = ", ".join(paths[:3])
    suffix = "" if len(paths) <= 3 else f", +{len(paths) - 3} more"
    return f"matched {preview}{suffix}"


def ready_for_events(
    *,
    work_id: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    sync_status: str,
    agent_local_warning: str = "",
    check_handoff: bool = True,
    handoff_check: Callable[[], None] | None = None,
    required_profile_checks: tuple[RequiredProfileItem, ...] = (),
    required_profile_reviews: tuple[RequiredProfileItem, ...] = (),
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
    validation_skips = dangerous_skip_events(events, "validation")
    validation_skipped = bool(validation_skips)
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
        else dangerous_skip_message("validation", validation_skips)
        if validation_skipped
        else "validation evidence with rationale failed"
        if failed_evidence_with_why
        else "missing validation evidence with --why",
    )
    review_skips = dangerous_skip_events(events, "review")
    review_skipped = bool(review_skips)
    reviews = accepted_review_events(events)
    recorded_reviews = review_events(events)
    add_check(
        "review",
        bool(reviews) or review_skipped,
        "external-enough review recorded"
        if reviews
        else dangerous_skip_message("review", review_skips)
        if review_skipped
        else SELF_REVIEW_GUIDANCE
        if recorded_reviews
        else "missing accepted external-enough review record; run a separate reviewer/subagent with fresh context",
    )
    for item in required_profile_checks:
        matching_evidence = [
            record
            for record in evidence
            if getattr(record, "check_name", "") == item.name
            and record.status == "pass"
        ]
        matching_skips = dangerous_skip_for_label(events, "validation", item.name)
        add_check(
            f"profile-check:{item.name}",
            bool(matching_evidence) or bool(matching_skips),
            f"required profile check recorded: {item.name} ({_paths_text(item.matched_paths)})"
            if matching_evidence
            else dangerous_skip_message("validation", matching_skips)
            if matching_skips
            else f"missing required profile check `{item.name}` ({_paths_text(item.matched_paths)}); run `hk validate --check {item.name} --why ... -- <native command>` or `hk dangerously-skip validation --label {item.name} --reason ... --mitigation ...`",
        )

    for item in required_profile_reviews:
        matching_reviews = [
            review
            for review in reviews
            if str(review.get("review_name") or "") == item.name
        ]
        matching_skips = dangerous_skip_for_label(events, "review", item.name)
        add_check(
            f"profile-review:{item.name}",
            bool(matching_reviews) or bool(matching_skips),
            f"required profile review recorded: {item.name} ({_paths_text(item.matched_paths)})"
            if matching_reviews
            else dangerous_skip_message("review", matching_skips)
            if matching_skips
            else f"missing required profile review `{item.name}` ({_paths_text(item.matched_paths)}); run `hk review prompt {item.name}` and record with `hk review add --review {item.name} ...`, or `hk dangerously-skip review --label {item.name} --reason ... --mitigation ...`",
        )

    sync_skips = dangerous_skip_events(events, "sync")
    sync_skipped = sync_status == "sync-dangerously-skipped"
    synced = sync_status == "synced" or sync_skipped
    sync_message = (
        "sync checkpoint fresh"
        if sync_status == "synced"
        else dangerous_skip_message("sync", sync_skips)
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
