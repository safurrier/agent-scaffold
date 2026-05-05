from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from harness_toolkit.kit.local import (
    LocalWorkflowError,
    add_note,
    add_review,
    brief,
    capture_command,
    create_work,
    git_diff_hash,
    handoff,
    init_spec,
    init_state,
    materialize_work,
    ready,
    spec_outline,
    spec_promote_dry_run,
    spec_status,
    sync_checkpoint,
)

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    return env


def _git_init(path: Path) -> None:
    path.mkdir()
    subprocess.run(
        ["git", "init"], cwd=path, check=True, capture_output=True, env=_git_env()
    )
    subprocess.run(
        ["git", "checkout", "-b", "feat/demo"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    (path / "README.md").write_text("# demo\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "chore: initial"],
        cwd=path,
        check=True,
        capture_output=True,
        env=_git_env()
        | {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


def _git_status(path: Path) -> str:
    return subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        check=True,
        text=True,
        env=_git_env(),
    ).stdout


def _run_hk(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["uv", "run", "hk", *args],
        cwd=ROOT,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )


def test_brief_is_read_only_and_does_not_recommend_commands(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    (target / "AGENTS.md").write_text("# Agents\n")
    (target / ".mise.toml").write_text("[tasks.check]\nrun = 'pytest'\n")

    result = brief(target)

    assert result.state_exists is False
    assert "AGENTS.md" in result.repo_surfaces
    assert ".mise.toml" in result.repo_surfaces
    payload = json.dumps(result.__dict__)
    assert "recommended_profile" not in payload
    assert "recommended_command" not in payload
    assert "confidence" not in payload
    assert _git_status(target) == "?? .mise.toml\n?? AGENTS.md\n"


def test_init_work_note_materialize_keep_local_state_ignored(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    init = init_state(target)
    work = create_work(target, "demo-work")
    note = add_note(target, kind="learning", text="Local state is okay when ignored.")
    plan = add_note(target, kind="plan", text="Adopt the agreed lightweight plan.")
    background = add_note(
        target, kind="background", text="Planning happened in chat first."
    )
    materialized = materialize_work(target)
    views = Path(materialized.path).parent

    assert init.ignored_by_local_git is True
    assert Path(work.work_dir, "events.jsonl").exists()
    assert note.seq == 2
    assert plan.seq == 3
    assert background.seq == 4
    assert "Adopt the agreed lightweight plan" in Path(materialized.path).read_text()
    assert "Planning happened in chat first" in Path(materialized.path).read_text()
    assert "Adopt the agreed lightweight plan" in (views / "plan.md").read_text()
    assert "Planning happened in chat first" in (views / "background.md").read_text()
    assert _git_status(target) == ""


def test_external_state_creates_no_checkout_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    state_home = tmp_path / "state-home"
    monkeypatch.setenv("XDG_STATE_HOME", str(state_home))

    init = init_state(target, no_local_files=True)
    work = create_work(target, "external-work", no_local_files=True)

    assert Path(init.state_dir).is_relative_to(state_home)
    assert not (target / ".harness-local").exists()
    assert Path(work.work_dir).exists()
    assert _git_status(target) == ""


def test_sync_checkpoint_is_binary_freshness_check(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "sync-work")

    before = sync_checkpoint(target, check=True)
    synced = sync_checkpoint(target)
    after = sync_checkpoint(target, check=True)
    add_note(target, kind="gap", text="Full suite not run.")
    stale = sync_checkpoint(target, check=True)

    assert before.synced is False
    assert synced.synced is True
    assert after.synced is True
    assert stale.synced is False
    assert "score" not in json.dumps(stale.__dict__).lower()


def test_sync_checkpoint_tracks_untracked_and_staged_changes(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "sync-work")
    sync_checkpoint(target)

    (target / "untracked.txt").write_text("new\n")
    untracked = sync_checkpoint(target, check=True)
    subprocess.run(
        ["git", "add", "untracked.txt"], cwd=target, check=True, env=_git_env()
    )
    staged = sync_checkpoint(target, check=True)

    assert untracked.synced is False
    assert staged.synced is False


def test_sync_checkpoint_tracks_untracked_content_changes(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "sync-work")
    untracked = target / "untracked.txt"
    untracked.write_text("v1\n")
    sync_checkpoint(target)

    untracked.write_text("v2\n")
    stale = sync_checkpoint(target, check=True)

    assert stale.synced is False


def test_git_diff_hash_streams_untracked_file_content(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    untracked = target / "large-untracked.bin"
    untracked.write_bytes((b"0123456789abcdef" * 1024) + b"v1")
    first = git_diff_hash(target)

    def fail_read_bytes(self: Path) -> bytes:
        raise AssertionError(f"read_bytes should not be used for {self}")

    monkeypatch.setattr(Path, "read_bytes", fail_read_bytes)
    untracked.write_bytes((b"0123456789abcdef" * 1024) + b"v2")
    second = git_diff_hash(target)

    assert first.startswith("sha256:")
    assert second.startswith("sha256:")
    assert second != first


def test_capture_records_redacted_success_and_failed_command(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "capture-work")

    success = capture_command(
        target,
        ("python3", "-c", "print('token=abc123456789012345')"),
        kind="test",
    )
    split_secret = capture_command(
        target,
        ("python3", "-c", "print('ok')", "--token", "abc123456789012345 withspace"),
    )
    failure = capture_command(target, ("python3", "-c", "raise SystemExit(7)"))

    transcript = Path(success.transcript_path).read_text()
    evidence = Path(success.transcript_path).parents[1] / "evidence.jsonl"
    evidence_text = evidence.read_text()
    assert success.exit_code == 0
    assert split_secret.exit_code == 0
    assert "token=[REDACTED]" in transcript
    assert "abc123456789012345" not in transcript
    assert "abc123456789012345" not in evidence_text
    assert "withspace" not in evidence_text
    assert failure.exit_code == 7


def test_hk_dev_preserves_caller_cwd_for_target_dot(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    result = subprocess.run(
        [str(ROOT / "scripts" / "hk-dev"), "brief", "--target", ".", "--json"],
        cwd=target,
        capture_output=True,
        check=False,
        text=True,
        timeout=120,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert Path(payload["target_root"]) == target.resolve()


def test_capture_missing_command_records_failed_evidence(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "missing-command")

    result = capture_command(target, ("definitely-not-a-real-command-hk",))

    transcript = Path(result.transcript_path).read_text()
    assert result.exit_code == 127
    assert result.status == "fail"
    assert "failed to start command" in transcript


def test_handoff_labels_failed_evidence_as_attempted_validation(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "failed-evidence")
    capture_command(
        target,
        ("python3", "-c", "raise SystemExit(2)"),
        why="Focused failing command.",
    )

    result = handoff(target)

    assert "attempted to validate: Focused failing command" in result.content
    assert "validates: Focused failing command" not in result.content


def test_handoff_does_not_overclaim_without_evidence(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "handoff-work")
    add_note(target, kind="decision", text="Keep the shell primary.")

    result = handoff(target)

    assert "Keep the shell primary" in result.content
    assert "No validation evidence recorded" in result.content


def test_lifecycle_ready_requires_plan_decision_validation_review_and_sync(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "ready-work")
    add_note(target, kind="context", text="Cyclopts is the CLI convention.")
    missing = ready(target)

    add_note(target, kind="plan", text="Implement the lifecycle facade.")
    add_note(target, kind="decision", text="Use validate as the primary evidence verb.")
    add_note(target, kind="spec-impact", text="SPEC documents lifecycle-first HK2.")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Focused lifecycle smoke test.",
    )
    add_review(
        target,
        backend="manual_external",
        reviewer="Alex",
        rubrics=("core-quality",),
        summary="No blocking findings.",
    )
    sync_checkpoint(target)
    done = ready(target)
    handoff_result = handoff(target)

    assert missing.ready is False
    assert any(
        check.id == "plan" and check.status == "fail" for check in missing.checks
    )
    assert done.ready is True
    assert done.status == "ready"
    assert "## Context" in handoff_result.content
    assert "Focused lifecycle smoke test" in handoff_result.content
    assert "manual_external / Alex" in handoff_result.content


def test_cli_evidence_bare_command_gives_list_hint() -> None:
    result = _run_hk("evidence", "--target", ".")

    assert result.returncode != 0
    assert "hk evidence list --target <repo> --json" in result.stderr


def test_cli_root_help_hides_legacy_sync_check() -> None:
    root = _run_hk("--help")
    legacy = _run_hk("legacy", "sync-check", "--help")

    assert root.returncode == 0
    assert legacy.returncode == 0
    assert "sync-check" not in root.stdout
    assert "hk legacy sync-check" in legacy.stdout


def test_cli_review_help_warns_self_review_does_not_count() -> None:
    result = _run_hk("review", "add", "--help")

    assert result.returncode == 0
    assert "Self-review does not satisfy readiness" in result.stdout
    assert "reviewer-fresh-context" in result.stdout


def test_review_add_rejects_self_review_identity(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "review-self")

    with pytest.raises(LocalWorkflowError, match="self-review does not count"):
        add_review(
            target,
            backend="manual_external",
            reviewer="implementation-agent-self-check",
            rubrics=("core-quality",),
            summary="I checked my own implementation.",
        )


def test_ready_warns_when_agent_local_state_makes_sync_stale(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "agent-state")
    add_note(target, kind="plan", text="Implement the lifecycle facade.")
    add_note(target, kind="decision", text="Use validate as the primary evidence verb.")
    add_note(target, kind="spec-impact", text="No spec impact declared.")
    capture_command(target, ("python3", "-c", "print('ok')"), why="Smoke test.")
    add_review(
        target,
        backend="manual_external",
        reviewer="Alex",
        rubrics=("core-quality",),
        summary="No blocking findings.",
    )
    sync_checkpoint(target)
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}")

    result = ready(target)

    assert result.ready is False
    assert any(
        check.id == "sync"
        and ".pi" in check.message
        and "agent-local state" in check.message
        for check in result.checks
    )


def test_generated_handoff_views_do_not_make_synced_work_stale(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "handoff-sync")
    add_note(target, kind="decision", text="Keep generated views non-semantic.")
    sync_checkpoint(target)

    rendered = handoff(target)
    materialized = materialize_work(target)
    checked = sync_checkpoint(target, check=True)
    repo_brief = brief(target)

    assert "Sync status: `synced`" in rendered.content
    assert Path(materialized.path).exists()
    assert checked.synced is True
    assert repo_brief.sync_status == "synced"


def test_local_spec_can_be_created_and_promoted_as_dry_run(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)

    created = init_spec(target)
    status = spec_status(target)
    outline = spec_outline(target)
    promote = spec_promote_dry_run(target)

    assert created.created is True
    assert status.source == "local"
    assert "# Local Project Specification" in outline.headings
    assert "Would write local spec" in promote
    assert not (target / "SPEC.md").exists()


def test_spec_init_uses_committed_spec_without_creating_unreachable_local_draft(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    (target / "SPEC.md").write_text("# Committed Spec\n")
    subprocess.run(["git", "add", "SPEC.md"], cwd=target, check=True, env=_git_env())
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "docs: add spec"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env()
        | {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )

    created = init_spec(target)
    status = spec_status(target)
    outline = spec_outline(target)

    assert created.created is False
    assert created.source == "committed"
    assert Path(created.spec_path) == target / "SPEC.md"
    assert status.spec_path == created.spec_path
    assert outline.headings == ["# Committed Spec"]
    assert not (
        target / ".harness-local" / "harness-kit" / "root" / "spec" / "SPEC.md"
    ).exists()


def test_cli_spec_outline_json_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("spec", "init", "--local", "--target", str(target), "--json").returncode
        == 0
    )

    result = _run_hk("spec", "outline", "--target", str(target), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "# Local Project Specification" in payload["headings"]


def test_cli_handoff_rejects_invalid_format(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("work", "start", "handoff-format", "--target", str(target)).returncode
        == 0
    )

    result = _run_hk("handoff", "--target", str(target), "--format", "xml")

    assert result.returncode != 0


def test_cli_note_from_file_records_plan_note(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    plan_file = tmp_path / "plan.md"
    plan_file.write_text(
        "Plan:\n- Translate external planning into one durable note.\n"
    )
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("work", "start", "plan-note", "--target", str(target)).returncode == 0
    )

    result = _run_hk(
        "note",
        "--target",
        str(target),
        "--kind",
        "plan",
        "--from-file",
        str(plan_file),
        "--json",
    )
    handoff_result = _run_hk("handoff", "--target", str(target))

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "plan"
    assert "Translate external planning" in payload["text"]
    assert "## Plan" in handoff_result.stdout
    assert "Translate external planning" in handoff_result.stdout


def test_cli_note_rejects_text_and_from_file(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    plan_file = tmp_path / "plan.md"
    plan_file.write_text("Plan\n")
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("work", "start", "plan-note", "--target", str(target)).returncode == 0
    )

    result = _run_hk(
        "note",
        "inline text",
        "--target",
        str(target),
        "--kind",
        "plan",
        "--from-file",
        str(plan_file),
    )

    assert result.returncode != 0
    assert "Use either note TEXT or --from-file" in result.stderr


def test_ready_rejects_failed_validation_and_rejected_review(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "not-ready-work")
    add_note(target, kind="plan", text="Implement the lifecycle facade.")
    add_note(target, kind="decision", text="Use validate as the primary evidence verb.")
    add_note(target, kind="spec-impact", text="SPEC documents lifecycle-first HK2.")
    capture_command(
        target,
        ("python3", "-c", "raise SystemExit(9)"),
        kind="test",
        why="This intentionally fails.",
    )
    add_review(
        target,
        backend="manual_external",
        reviewer="Alex",
        rubrics=("core-quality",),
        summary="Blocking findings remain.",
        disposition="rejected",
    )
    sync_checkpoint(target)

    result = ready(target)

    assert result.ready is False
    assert any(
        check.id == "validation"
        and check.status == "fail"
        and "failed" in check.message
        for check in result.checks
    )
    assert any(
        check.id == "review" and check.status == "fail" for check in result.checks
    )


def test_cli_context_from_file_avoids_shell_fragile_text(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    context_file = tmp_path / "context.md"
    context_file.write_text("Use `uv sync --extra dev` before full validation.\n")
    assert _run_hk("start", "context-file", "--target", str(target)).returncode == 0

    result = _run_hk(
        "context",
        "--from-file",
        str(context_file),
        "--target",
        str(target),
        "--json",
    )
    handoff_result = _run_hk("handoff", "--target", str(target))

    assert result.returncode == 0, result.stderr
    assert "uv sync --extra dev" in json.loads(result.stdout)["text"]
    assert "uv sync --extra dev" in handoff_result.stdout


def test_cli_lifecycle_commands_record_handoff_and_ready(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    start = _run_hk("start", "cli-life", "--target", str(target), "--json")
    context = _run_hk(
        "context", "Important repo fact.", "--target", str(target), "--json"
    )
    plan = _run_hk("plan", "Implement the feature.", "--target", str(target), "--json")
    decide = _run_hk(
        "decide",
        "Keep lifecycle commands primary.",
        "--spec-impact",
        "SPEC updated.",
        "--target",
        str(target),
        "--json",
    )
    validate = _run_hk(
        "validate",
        "--target",
        str(target),
        "--kind",
        "test",
        "--why",
        "Smoke test validates CLI evidence.",
        "--json",
        "--",
        "python3",
        "-c",
        "print('validated')",
    )
    review = _run_hk(
        "review",
        "add",
        "--target",
        str(target),
        "--backend",
        "manual_external",
        "--reviewer",
        "Alex",
        "--rubric",
        "core-quality",
        "--summary",
        "No blocking findings.",
        "--json",
    )
    sync = _run_hk("sync", "--target", str(target), "--json")
    ready_result = _run_hk("ready", "--target", str(target), "--json")
    handoff_result = _run_hk("handoff", "--target", str(target))

    assert start.returncode == 0, start.stderr
    assert json.loads(context.stdout)["kind"] == "context"
    assert json.loads(plan.stdout)["kind"] == "plan"
    assert decide.returncode == 0, decide.stderr
    assert validate.returncode == 0, validate.stderr
    assert "validated" in validate.stderr
    assert review.returncode == 0, review.stderr
    assert sync.returncode == 0, sync.stderr
    payload = json.loads(ready_result.stdout)
    assert ready_result.returncode == 0, ready_result.stderr
    assert payload["ready"] is True
    assert "## Context" in handoff_result.stdout
    assert "Smoke test validates CLI evidence" in handoff_result.stdout


def test_cli_validate_requires_why(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("start", "validate-why", "--target", str(target)).returncode == 0

    result = _run_hk(
        "validate",
        "--target",
        str(target),
        "--",
        "python3",
        "-c",
        "print('missing why')",
    )

    assert result.returncode != 0


def test_cli_capture_json_stdout_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("work", "start", "capture-json", "--target", str(target)).returncode
        == 0
    )

    result = _run_hk(
        "capture",
        "--target",
        str(target),
        "--kind",
        "test",
        "--json",
        "--",
        "python3",
        "-c",
        "print('hello from command')",
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["status"] == "pass"
    assert "hello from command" in result.stderr


def test_cli_capture_preserves_wrapped_exit_code(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_result = _run_hk("init", "--target", str(target), "--json")
    work_result = _run_hk(
        "work", "start", "cli-capture", "--target", str(target), "--json"
    )

    result = _run_hk(
        "capture",
        "--target",
        str(target),
        "--kind",
        "test",
        "--",
        "python3",
        "-c",
        "raise SystemExit(5)",
    )

    assert init_result.returncode == 0, init_result.stderr
    assert work_result.returncode == 0, work_result.stderr
    assert result.returncode == 5
    assert "status=fail" in result.stdout
