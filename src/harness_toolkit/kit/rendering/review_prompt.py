"""Fresh-context review prompt rendering."""

from __future__ import annotations

import shlex

from harness_toolkit.kit.ledger import lifecycle_events
from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.profiles.models import ReviewDefinition
from harness_toolkit.kit.readiness.policy import notes_by_kind, notes_by_kinds


def render_review_prompt(
    *,
    work_id: str,
    target_root: str,
    branch: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    changed_paths: list[str],
    profile_review: ReviewDefinition | None = None,
) -> str:
    lines = [
        "You are an independent AI/tool reviewer or fresh-context subagent reviewer for this HK lifecycle work.",
        "Do not rely on the implementation agent's self-review; review independently.",
        "Preferred review is a separate AI/tool reviewer, ideally a different model/runtime or context.",
        "Minimum fallback is a fresh-context subagent review. Implementation-agent self-review does not count.",
        "If your harness has a fresh-context review mechanism, dispatch this prompt to that reviewer now.",
        "",
        f"Work: {work_id}",
        f"Target: {target_root}",
        f"Branch: {branch}",
        "",
        "Plan:",
    ]
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "plan")] or ["- None recorded."]
    )
    lines.extend(["", "Context:"])
    lines.extend(
        [f"- {item}" for item in notes_by_kinds(events, ("context", "background"))]
        or ["- None recorded."]
    )
    lines.extend(["", "Decisions and spec reflection:"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "decision")]
        or ["- None recorded."]
    )
    for item in notes_by_kind(events, "spec-impact"):
        lines.append(f"  - Spec: {item}")
    supersessions = lifecycle_events.invariant_supersession_events(events)
    if supersessions:
        lines.extend(
            [
                "",
                "Invariant supersessions requiring explicit reviewer attention:",
            ]
        )
        for item in supersessions:
            lines.extend(
                [
                    f"- Invariant: {item.invariant}",
                    f"  Previous: {item.previous}",
                    f"  Reason: {item.reason}",
                ]
            )
            if item.replacement:
                lines.append(f"  Replacement: {item.replacement}")
            if item.removal_rationale:
                lines.append(f"  Removal rationale: {item.removal_rationale}")
            if item.docs:
                lines.append(
                    f"  Docs/system map claimed updated: {', '.join(item.docs)}"
                )
            lines.append(
                f"  Required commit trailer: Supersedes-Invariant: {item.invariant}"
            )
    lines.extend(["", "Validation evidence:"])
    if evidence:
        for record in evidence:
            lines.append(
                f"- {record.status}: `{record.command_display}` — {record.why or 'no rationale'}"
            )
    else:
        lines.append("- None recorded.")
    lines.extend(["", "Changed paths:"])
    lines.extend([f"- {path}" for path in changed_paths] or ["- none"])
    review_add_hint = "hk review add --backend subagent --reviewer reviewer-fresh-context --summary '...'"
    if profile_review is not None:
        lines.extend(
            [
                "",
                f"Profile review: {profile_review.name}",
                f"Purpose: {profile_review.purpose}",
                f"Backend: {profile_review.backend}",
            ]
        )
        if profile_review.dispatch_hint:
            lines.append(f"Dispatch hint: {profile_review.dispatch_hint}")
        if profile_review.instructions is not None:
            if profile_review.instructions.type == "file":
                lines.append(f"Instructions file: {profile_review.instructions.path}")
            lines.extend(["", "Profile review instructions:"])
            lines.append(profile_review.instructions.text.strip())
        review_add_hint = (
            f"hk review add --review {shlex.quote(profile_review.name)} "
            f"--backend {shlex.quote(profile_review.backend)} "
            "--reviewer reviewer-fresh-context --summary '...'"
        )
    lines.extend(
        [
            "",
            "Review task:",
            "1. Inspect the changed files and relevant tests.",
            "2. Check correctness, missed edge cases, docs/spec impact, validation adequacy, and HK handoff quality.",
            "   If invariant supersessions are listed, verify they are intentional, loudly documented, reflected in system map/docs/tests, and called out for commit/PR reviewers.",
            "3. Return blocking findings, non-blocking findings, and final disposition.",
            f"4. If accepted, the implementation agent must record you with `{review_add_hint}`.",
            "",
            "Dispatch hint for implementation agents:",
            "- If you have a fresh-context review mechanism, send this whole prompt to it now.",
            "- Examples: Pi `subagent` tool; Claude Code `Agent` tool (`Task` alias); Codex via Shell tool running `codex review --uncommitted`.",
            "- Do not answer this prompt yourself as the implementation agent.",
            "- After review tooling runs, re-run `hk status`; review tools may create agent-local state that must be removed or handled with `hk sync --exclude PATH --reason ...`.",
            "- If no independent AI/tool or fresh-context subagent is available, record `hk dangerously-skip review --label no-review --reason ... --mitigation ...`.",
        ]
    )
    return "\n".join(lines) + "\n"
