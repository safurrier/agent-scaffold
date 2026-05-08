from __future__ import annotations

from pathlib import Path

import pytest

from harness_toolkit.kit.local import (
    add_note,
    add_review,
    create_work,
    handoff,
    review_prompt,
    sync_checkpoint,
)
from tests.support.hk2_repo import git_init

pytestmark = pytest.mark.unit


def test_handoff_contains_lifecycle_sections(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")
    create_work(target, "rendering")
    add_note(target, kind="plan", text="Render parity handoff.")
    add_note(target, kind="context", text="Rendering parity context.")
    add_note(target, kind="decision", text="No committed spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    add_review(
        target,
        backend="codex",
        reviewer="codex-review",
        rubrics=("core-quality",),
        summary="Accepted for rendering parity.",
    )
    sync_checkpoint(target)

    result = handoff(target)

    for section in (
        "# Handoff",
        "## Context",
        "## Plan",
        "## Decisions and spec reflection",
        "## Validation evidence",
        "## Readiness",
        "## Review",
    ):
        assert section in result.content
    assert "Render parity handoff." in result.content
    assert "codex / codex-review" in result.content


def test_review_prompt_contains_dispatch_guidance(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")
    create_work(target, "review-prompt")
    add_note(target, kind="plan", text="Render review prompt.")

    result = review_prompt(target)

    assert "independent AI/tool reviewer" in result.prompt
    assert "fresh-context subagent" in result.prompt
    assert "codex review --uncommitted" in result.prompt
    assert "Do not answer this prompt yourself" in result.prompt
