"""Fresh-context review prompt rendering."""

from __future__ import annotations

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.policy import notes_by_kind, notes_by_kinds


def render_review_prompt(
    *,
    work_id: str,
    target_root: str,
    branch: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    changed_paths: list[str],
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
    lines.extend(
        [
            "",
            "Review task:",
            "1. Inspect the changed files and relevant tests.",
            "2. Check correctness, missed edge cases, docs/spec impact, validation adequacy, and HK handoff quality.",
            "3. Return blocking findings, non-blocking findings, and final disposition.",
            "4. If accepted, the implementation agent must record you with `hk review add --backend subagent --reviewer reviewer-fresh-context --rubric core-quality --summary '...'`.",
            "",
            "Dispatch hint for implementation agents:",
            "- If you have a fresh-context review mechanism, send this whole prompt to it now.",
            "- Examples: Pi `subagent` tool; Claude Code `Agent` tool (`Task` alias); Codex via Shell tool running `codex review --uncommitted`.",
            "- Do not answer this prompt yourself as the implementation agent.",
            "- After review tooling runs, re-run `hk status`; review tools may create agent-local state that must be removed or handled with `hk sync --exclude PATH --reason ...`.",
            "- If no independent AI/tool or fresh-context subagent is available, record `hk dangerously-skip review --reason ...`.",
        ]
    )
    return "\n".join(lines) + "\n"
