from __future__ import annotations

import json
from pathlib import Path

import pytest

from tests.support.hk2_repo import git_init, run_hk

pytestmark = pytest.mark.agent_sim


def _json(result) -> dict[str, object]:
    assert result.returncode == 0, (result.stdout, result.stderr)
    return json.loads(result.stdout)


def test_agent_sim_happy_path_reaches_ready_through_public_cli(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")

    start = _json(
        run_hk(
            "start",
            "agent-sim-happy-path",
            "--plan",
            "Exercise the public HK lifecycle like an implementation agent.",
            "--target",
            str(target),
            "--json",
        )
    )
    assert start["work_id"]

    context = _json(
        run_hk(
            "context",
            "Fixture repo uses README.md as the changed file.",
            "--target",
            str(target),
            "--json",
        )
    )
    assert context["kind"] == "context"

    (target / "README.md").write_text("# demo\n\nAgent simulation touched this file.\n")

    decision = _json(
        run_hk(
            "decide",
            "README-only fixture change has no product spec impact.",
            "--spec-impact",
            "not-needed",
            "--target",
            str(target),
            "--json",
        )
    )
    assert decision["kind"] == "decision"

    validation = _json(
        run_hk(
            "validate",
            "--why",
            "Native command evidence proves the agent simulation command path works.",
            "--target",
            str(target),
            "--json",
            "--",
            "python3",
            "-c",
            "print('agent sim ok')",
        )
    )
    assert validation["status"] == "pass"

    review = _json(
        run_hk(
            "review",
            "add",
            "--backend",
            "subagent",
            "--reviewer",
            "reviewer-fresh-context",
            "--rubric",
            "agent-sim-quality",
            "--summary",
            "No blockers for happy-path simulation.",
            "--target",
            str(target),
            "--json",
        )
    )
    assert review["reviewer"] == "reviewer-fresh-context"

    sync = _json(run_hk("sync", "--target", str(target), "--json"))
    assert sync["synced"] is True

    status = _json(run_hk("status", "--target", str(target), "--json"))
    assert status["ready_status"] == "ready"
    next_actions = status["next_actions"]
    assert isinstance(next_actions, list)
    assert "handoff: hk handoff" in next_actions

    ready = _json(run_hk("ready", "--target", str(target), "--json"))
    assert ready["ready"] is True
    assert ready["status"] == "ready"

    summary = run_hk("summary", "--target", str(target))
    assert summary.returncode == 0, summary.stderr
    assert "- Readiness: `ready`" in summary.stdout

    handoff = run_hk("handoff", "--target", str(target))
    assert handoff.returncode == 0, handoff.stderr
    assert "## Validation evidence" in handoff.stdout
    assert "## Review" in handoff.stdout


def test_agent_sim_local_state_churn_stales_sync_exclusion(tmp_path: Path) -> None:
    target = git_init(tmp_path / "repo")
    _json(
        run_hk(
            "start",
            "agent-local-churn",
            "--plan",
            "Exercise excluded agent-local state freshness.",
            "--target",
            str(target),
            "--json",
        )
    )
    local_state = target / ".pi" / "session.json"
    local_state.parent.mkdir()
    local_state.write_text("{}\n")

    sync = _json(
        run_hk(
            "sync",
            "--exclude",
            ".pi",
            "--reason",
            "Only local agent state.",
            "--target",
            str(target),
            "--json",
        )
    )
    assert sync["synced"] is True

    local_state.write_text('{"changed": true}\n')
    checked = run_hk("sync", "--check", "--target", str(target), "--json")

    assert checked.returncode == 1
    payload = json.loads(checked.stdout)
    assert payload["synced"] is False
    assert "excluded path changed" in payload["message"]
