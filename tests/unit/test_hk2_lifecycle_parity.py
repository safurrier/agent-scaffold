from __future__ import annotations

from pathlib import Path

import pytest

from harness_toolkit.kit.local import (
    add_dangerous_skip,
    add_note,
    add_review,
    capture_command,
    create_work,
    ready,
    sync_checkpoint,
)
from tests.support.hk2_repo import git_init

pytestmark = pytest.mark.integration


def test_lifecycle_happy_path_reaches_ready(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")

    create_work(target, "parity")
    add_note(target, kind="plan", text="Exercise parity lifecycle.")
    add_note(target, kind="decision", text="No committed spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    result = add_review(
        target,
        backend="codex",
        reviewer="codex-review",
        summary="Accepted for parity.",
    )
    assert result.backend == "codex"

    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Smoke validation proves native command evidence.",
    )
    sync_checkpoint(target)

    readiness = ready(target)

    assert readiness.ready is True
    assert readiness.status == "ready"
    assert {check.id: check.status for check in readiness.checks}["review"] == "pass"


def test_lifecycle_missing_review_can_be_dangerously_skipped(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")

    create_work(target, "skip-review")
    add_note(target, kind="plan", text="Exercise dangerous review skip.")
    add_note(target, kind="decision", text="No committed spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Smoke validation proves native command evidence.",
    )
    add_dangerous_skip(
        target,
        check="review",
        label="fixture-no-review",
        reason="No independent reviewer in parity fixture.",
        mitigation="Covered by parity test assertions.",
    )
    sync_checkpoint(target)

    readiness = ready(target)

    assert readiness.ready is True
    assert readiness.status == "ready-with-dangerous-skips"
