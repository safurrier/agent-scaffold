from __future__ import annotations

from pathlib import Path

import pytest

from harness_toolkit.kit.local import init_state, resolve_local_state
from harness_toolkit.kit.specs.operations import (
    init_spec_for_state,
    spec_outline_for_state,
    spec_promote_dry_run_for_state,
    spec_status_for_state,
)
from tests.support.hk2_repo import git_init

pytestmark = pytest.mark.unit


def test_spec_operations_create_status_outline_and_promote_preview(
    tmp_path: Path,
) -> None:
    target = git_init(tmp_path / "repo")
    init = init_state(target)

    # Reuse LocalState from the public init path to prove spec operations are a
    # focused seam over the same state model.
    state = resolve_local_state(target)
    created = init_spec_for_state(state)
    status = spec_status_for_state(state)
    outline = spec_outline_for_state(state)
    preview = spec_promote_dry_run_for_state(state)

    assert init.state_dir == str(state.state_dir)
    assert created.created is True
    assert status.source == "local"
    assert "# Local Project Specification" in outline.headings
    assert "Would write local spec" in preview


def test_committed_spec_wins_over_local_draft(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")
    init_state(target)
    state = resolve_local_state(target)
    init_spec_for_state(state)
    (target / "SPEC.md").write_text("# Committed Spec\n")

    status = spec_status_for_state(state)

    assert status.source == "committed"
    assert status.spec_path == str(target / "SPEC.md")
