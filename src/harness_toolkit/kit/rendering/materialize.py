"""Materialized Markdown view rendering for HK2 ledgers."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.ledger.models import EventRecord
from harness_toolkit.kit.readiness.policy import notes_by_kinds


def write_note_views(views: Path, events: list[EventRecord]) -> None:
    views.mkdir(exist_ok=True)
    for filename, kinds, title in (
        ("plan.md", ("plan",), "Plan"),
        ("learning-log.md", ("learning",), "Learning Log"),
        ("decisions.md", ("decision",), "Decisions"),
        ("context.md", ("context", "background"), "Context"),
        ("background.md", ("context", "background"), "Context"),
        ("gaps.md", ("gap",), "Gaps"),
    ):
        items = notes_by_kinds(events, kinds)
        content = f"# {title}\n\n" + "\n".join(f"- {item}" for item in items)
        if not items:
            content += "None recorded."
        (views / filename).write_text(content + "\n")
