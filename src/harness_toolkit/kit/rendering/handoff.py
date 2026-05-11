"""Handoff markdown rendering for Harness Kit lifecycle state."""

from __future__ import annotations

from harness_toolkit.kit.ledger import lifecycle_events
from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.diagnostics import ReadyResult
from harness_toolkit.kit.readiness.policy import notes_by_kind, notes_by_kinds


def artifact_events(events: list[EventRecord]) -> list[lifecycle_events.ArtifactEvent]:
    return lifecycle_events.artifact_events(events)


def dangerous_skip_records(
    events: list[EventRecord],
) -> list[lifecycle_events.DangerousSkipEvent]:
    return lifecycle_events.dangerous_skip_events(events)


def format_dangerous_skip(skip: lifecycle_events.DangerousSkipEvent) -> str:
    check = skip.check or "unknown"
    label = skip.label or "unlabeled"
    return f"- {check}: {label} — reason: {skip.reason}; mitigation: {skip.mitigation}"


def artifact_display_path(artifact: lifecycle_events.ArtifactEvent) -> str:
    path = artifact.artifact_path or artifact.source_path
    return path or "<unrecorded>"


def evidence_label(record: EvidenceRecord) -> str:
    return f" [{record.check_name}]" if record.check_name else ""


def review_label(review: lifecycle_events.ReviewEvent) -> str:
    return f" [{review.review_name}]" if review.review_name else ""


def render_handoff_pr_markdown(
    *,
    work_id: str,
    branch: str,
    git_sha: str,
    dirty: bool,
    sync_status: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    readiness: ReadyResult,
) -> str:
    plan_items = notes_by_kind(events, "plan")
    decision_items = notes_by_kind(events, "decision")
    learning_items = notes_by_kind(events, "learning")
    gap_items = notes_by_kind(events, "gap")
    lines = [
        "## Summary",
        f"- Work: `{work_id}` on `{branch}` at `{git_sha}`",
        f"- Readiness: `{readiness.status}`; sync: `{sync_status}`; dirty: `{str(dirty).lower()}`",
    ]
    lines.extend(
        [f"- {item}" for item in plan_items]
        or ["- See commit history for implementation details."]
    )
    if decision_items:
        lines.extend(["", "## Decisions", *[f"- {item}" for item in decision_items]])
    if learning_items or gap_items:
        lines.append("")
        lines.append("## Notes for reviewers")
        lines.extend([f"- Learning: {item}" for item in learning_items])
        lines.extend([f"- Gap: {item}" for item in gap_items])
    lines.extend(["", "## Validation"])
    if evidence:
        for record in evidence:
            why = f" — {record.why}" if record.why else ""
            lines.append(
                f"- `{record.command_display}`{evidence_label(record)}: {record.status} (exit {record.exit_code}){why}"
            )
    else:
        lines.append("- No validation evidence recorded in HK.")
    skips = dangerous_skip_records(events)
    if skips:
        lines.extend(["", "## Dangerous skips"])
        lines.extend(format_dangerous_skip(skip) for skip in skips)
    artifacts = artifact_events(events)
    if artifacts:
        lines.extend(["", "## Attached artifacts"])
        for artifact in artifacts:
            label = artifact.label.strip()
            label_text = f" — {label}" if label else ""
            lines.append(
                f"- {artifact.kind}: `{artifact_display_path(artifact)}`{label_text}"
            )
    if not readiness.ready:
        lines.extend(["", "## Open readiness checks"])
        for check in readiness.checks:
            if check.status != "pass":
                lines.append(f"- {check.id}: {check.message}")
    return "\n".join(lines) + "\n"


def render_summary_markdown(
    *,
    work_id: str,
    branch: str,
    git_sha: str,
    dirty: bool,
    sync_status: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    readiness: ReadyResult,
) -> str:
    lines = [
        "# HK Readiness Summary",
        "",
        f"- Work: `{work_id}`",
        f"- Branch: `{branch}` at `{git_sha}`",
        f"- Readiness: `{readiness.status}`",
        f"- Sync: `{sync_status}`",
        f"- Dirty: `{str(dirty).lower()}`",
    ]
    plan_items = notes_by_kind(events, "plan")
    if plan_items:
        lines.extend(["", "## Plan", *[f"- {item}" for item in plan_items]])
    lines.extend(["", "## Validation"])
    if evidence:
        for record in evidence:
            transcript = (
                f"; transcript: `{record.transcript_path}`"
                if record.transcript_path
                else ""
            )
            why = f" — {record.why}" if record.why else ""
            lines.append(
                f"- {record.status}: `{record.command_display}`{evidence_label(record)} (exit {record.exit_code}{transcript}){why}"
            )
    else:
        lines.append("- None recorded.")
    reviews = lifecycle_events.review_events(events)
    skips = dangerous_skip_records(events)
    review_skips = [skip for skip in skips if skip.check == "review"]
    lines.extend(["", "## Review"])
    if reviews:
        for review in reviews:
            rubrics = ", ".join(review.rubrics)
            lines.append(
                f"- {review.backend} / {review.reviewer}{review_label(review)} ({rubrics}): {review.summary} [{review.disposition}]"
            )
    elif review_skips:
        lines.append("- No review recorded; see dangerous review skip below.")
    else:
        lines.append("- None recorded.")
    lines.extend(["", "## Dangerous skips"])
    if skips:
        lines.extend(format_dangerous_skip(skip) for skip in skips)
    else:
        lines.append("- None recorded.")
    artifacts = artifact_events(events)
    if artifacts:
        lines.extend(["", "## Attached artifacts"])
        for artifact in artifacts:
            label = artifact.label.strip()
            label_text = f" — {label}" if label else ""
            lines.append(
                f"- {artifact.kind}: `{artifact_display_path(artifact)}`{label_text}"
            )
    lines.extend(["", "## Readiness checks"])
    for check in readiness.checks:
        lines.append(f"- {check.id}: {check.status} — {check.message}")
    return "\n".join(lines) + "\n"


def render_handoff_markdown(
    *,
    work_id: str,
    branch: str,
    git_sha: str,
    dirty: bool,
    sync_status: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    readiness: ReadyResult,
) -> str:
    lines = [
        "# Handoff",
        "",
        "## Summary",
        f"- Work: `{work_id}`",
        f"- Branch: `{branch}`",
        f"- Git SHA: `{git_sha}`",
        f"- Dirty: `{str(dirty).lower()}`",
        f"- Sync status: `{sync_status}`",
        "",
        "## Context",
    ]
    lines.extend(
        [f"- {item}" for item in notes_by_kinds(events, ("context", "background"))]
        or ["- None recorded."]
    )
    lines.extend(["", "## Plan"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "plan")] or ["- None recorded."]
    )
    lines.extend(["", "## Decisions and spec reflection"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "decision")]
        or ["- None recorded."]
    )
    spec_impact = notes_by_kind(events, "spec-impact")
    if spec_impact:
        lines.extend([f"  - Spec: {item}" for item in spec_impact])
    lines.extend(["", "## Learning"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "learning")]
        or ["- None recorded."]
    )
    lines.extend(["", "## Gaps"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "gap")] or ["- None recorded."]
    )
    lines.extend(["", "## Validation evidence"])
    if evidence:
        for record in evidence:
            transcript = (
                f" — `{record.transcript_path}`" if record.transcript_path else ""
            )
            if record.why:
                verb = (
                    "validates" if record.status == "pass" else "attempted to validate"
                )
                why = f" — {verb}: {record.why}"
            else:
                why = ""
            lines.append(
                f"- `{record.command_display}`: {record.status} (exit {record.exit_code}){why}{transcript}"
            )
    else:
        lines.append("- No validation evidence recorded.")
    lines.extend(["", "## Readiness"])
    lines.append(f"- Status: `{readiness.status}`")
    for check in readiness.checks:
        lines.append(f"- {check.id}: {check.status} — {check.message}")
    lines.extend(["", "## Review"])
    reviews = lifecycle_events.review_events(events)
    if reviews:
        for review in reviews:
            rubrics = ", ".join(review.rubrics)
            lines.append(
                f"- {review.backend} / {review.reviewer}{review_label(review)} ({rubrics}): {review.summary} [{review.disposition}]"
            )
    else:
        lines.append("- None recorded.")
    artifacts = artifact_events(events)
    if artifacts:
        lines.extend(["", "## Attached artifacts"])
        for artifact in artifacts:
            label = artifact.label.strip()
            label_text = f" — {label}" if label else ""
            copied = "copied" if artifact.copied else "referenced"
            lines.append(
                f"- {artifact.kind}: `{artifact_display_path(artifact)}` ({copied}, {artifact.size_bytes} bytes, {artifact.sha256}){label_text}"
            )
    sync_exclusions = [
        checkpoint
        for checkpoint in lifecycle_events.sync_checkpoint_events(events)
        if checkpoint.excluded_paths
    ]
    if sync_exclusions:
        lines.extend(["", "## Sync exclusions"])
        for checkpoint in sync_exclusions:
            path_text = ", ".join(checkpoint.excluded_paths)
            lines.append(f"- {path_text}: {checkpoint.exclude_reason}")
    skips = dangerous_skip_records(events)
    if skips:
        lines.extend(["", "## Dangerous skips"])
        lines.extend(format_dangerous_skip(skip) for skip in skips)
    return "\n".join(lines) + "\n"
