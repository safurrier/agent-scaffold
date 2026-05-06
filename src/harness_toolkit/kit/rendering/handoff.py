"""Handoff markdown rendering for HK2 lifecycle state."""

from __future__ import annotations

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.diagnostics import ReadyResult
from harness_toolkit.kit.readiness.policy import (
    notes_by_kind,
    notes_by_kinds,
    review_events,
)


def artifact_events(events: list[EventRecord]) -> list[dict[str, object]]:
    return [event.data for event in events if event.type == "artifact_attached"]


def artifact_display_path(artifact: dict[str, object]) -> str:
    path = str(artifact.get("artifact_path") or artifact.get("source_path") or "")
    return path or "<unrecorded>"


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
                f"- `{record.command_display}`: {record.status} (exit {record.exit_code}){why}"
            )
    else:
        lines.append("- No validation evidence recorded in HK.")
    skips = [event.data for event in events if event.type == "dangerous_skip_added"]
    if skips:
        lines.extend(["", "## Dangerous skips"])
        for skip in skips:
            lines.append(f"- {skip.get('check')}: {skip.get('reason')}")
    artifacts = artifact_events(events)
    if artifacts:
        lines.extend(["", "## Attached artifacts"])
        for artifact in artifacts:
            label = str(artifact.get("label") or "").strip()
            label_text = f" — {label}" if label else ""
            lines.append(
                f"- {artifact.get('kind')}: `{artifact_display_path(artifact)}`{label_text}"
            )
    if not readiness.ready:
        lines.extend(["", "## Open readiness checks"])
        for check in readiness.checks:
            if check.status != "pass":
                lines.append(f"- {check.id}: {check.message}")
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
    reviews = review_events(events)
    if reviews:
        for review in reviews:
            raw_rubrics = review.get("rubrics", [])
            rubrics_list = raw_rubrics if isinstance(raw_rubrics, list) else []
            rubrics = ", ".join(str(item) for item in rubrics_list)
            lines.append(
                f"- {review.get('backend')} / {review.get('reviewer')} ({rubrics}): {review.get('summary')} [{review.get('disposition')}]"
            )
    else:
        lines.append("- None recorded.")
    artifacts = artifact_events(events)
    if artifacts:
        lines.extend(["", "## Attached artifacts"])
        for artifact in artifacts:
            label = str(artifact.get("label") or "").strip()
            label_text = f" — {label}" if label else ""
            copied = "copied" if artifact.get("copied") else "referenced"
            lines.append(
                f"- {artifact.get('kind')}: `{artifact_display_path(artifact)}` ({copied}, {artifact.get('size_bytes')} bytes, {artifact.get('sha256')}){label_text}"
            )
    sync_exclusions = [
        event.data
        for event in events
        if event.type == "sync_checkpoint" and event.data.get("excluded_paths")
    ]
    if sync_exclusions:
        lines.extend(["", "## Sync exclusions"])
        for checkpoint in sync_exclusions:
            paths = checkpoint.get("excluded_paths", [])
            path_text = (
                ", ".join(str(path) for path in paths)
                if isinstance(paths, list)
                else str(paths)
            )
            lines.append(f"- {path_text}: {checkpoint.get('exclude_reason')}")
    skips = [event.data for event in events if event.type == "dangerous_skip_added"]
    if skips:
        lines.extend(["", "## Dangerous skips"])
        for skip in skips:
            lines.append(f"- {skip.get('check')}: {skip.get('reason')}")
    return "\n".join(lines) + "\n"
