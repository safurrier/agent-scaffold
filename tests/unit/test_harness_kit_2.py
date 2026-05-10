from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from harness_toolkit.kit.local import (
    LocalWorkflowError,
    add_dangerous_skip,
    add_note,
    add_review,
    attach_artifact,
    brief,
    capture_command,
    create_work,
    export_handoff_dir,
    git_diff_hash,
    handoff,
    init_spec,
    init_state,
    materialize_work,
    read_evidence,
    ready,
    spec_outline,
    spec_promote_dry_run,
    spec_status,
    status,
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


def test_init_requires_git_repo(tmp_path: Path) -> None:
    target = tmp_path / "not-a-repo"
    target.mkdir()

    with pytest.raises(LocalWorkflowError, match="not inside a git repository"):
        init_state(target)


def test_artifact_attach_copies_hashes_and_renders_in_handoff(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "attach-artifact")
    artifact = tmp_path / "pi-session.jsonl"
    artifact.write_text('{"event":"message"}\n')

    result = attach_artifact(
        target,
        source_path=artifact,
        kind="agent-session",
        label="Pi session transcript",
        redaction="unknown",
    )
    rendered = handoff(target)

    copied = Path(result.artifact_path)
    assert result.kind == "agent-session"
    assert result.copied is True
    assert copied.exists()
    assert copied.read_text() == artifact.read_text()
    assert result.sha256.startswith("sha256:")
    assert "## Attached artifacts" in rendered.content
    assert "agent-session" in rendered.content
    assert "Pi session transcript" in rendered.content


def test_artifact_attach_can_record_without_copying(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "reference-artifact")
    artifact = tmp_path / "codex-review.md"
    artifact.write_text("# Review\n")

    result = attach_artifact(
        target,
        source_path=artifact,
        kind="codex-review",
        label="Codex review transcript",
        redaction="external",
        copy=False,
    )
    rendered = handoff(target)

    assert result.copied is False
    assert result.artifact_path == ""
    assert result.source_path == str(artifact.resolve())
    assert "referenced" in rendered.content
    assert str(artifact.resolve()) in rendered.content


def test_artifact_attach_requires_active_work_and_valid_file(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)

    with pytest.raises(LocalWorkflowError, match="No active work"):
        attach_artifact(
            target, source_path=tmp_path / "missing.log", kind="agent-session"
        )

    create_work(target, "attach-errors")
    with pytest.raises(LocalWorkflowError, match="does not exist"):
        attach_artifact(
            target, source_path=tmp_path / "missing.log", kind="agent-session"
        )
    with pytest.raises(LocalWorkflowError, match="invalid artifact kind"):
        attach_artifact(target, source_path=target / "README.md", kind="Agent Session")


def test_cli_artifact_attach_json_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    artifact = tmp_path / "session.jsonl"
    artifact.write_text('{"event":"message"}\n')
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk(
            "start",
            "attach-cli",
            "--target",
            str(target),
            "--plan",
            "Attach artifact.",
            "--json",
        ).returncode
        == 0
    )

    result = _run_hk(
        "artifact",
        "attach",
        "--path",
        str(artifact),
        "--kind",
        "agent-session",
        "--label",
        "Pi session transcript",
        "--target",
        str(target),
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["kind"] == "agent-session"
    assert payload["copied"] is True
    assert Path(payload["artifact_path"]).exists()


def test_handoff_dir_export_writes_generated_package_and_checks_freshness(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-package")
    add_note(target, kind="plan", text="Export a generated HK handoff package.")
    add_note(target, kind="decision", text="HK ledger remains canonical.")
    add_note(target, kind="spec-impact", text="Spec updated for generated exports.")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Synthetic validation for export package.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="fresh-context",
        rubrics=("export",),
        summary="No blockers.",
    )
    sync_checkpoint(target)
    output = target / ".ai" / "hk" / "demo-export"
    output.mkdir(parents=True)
    escaped_file = output.parent / "outside.txt"
    escaped_file.write_text("must survive cleanup\n")
    outside_artifacts = target / "outside-artifacts"
    outside_artifacts.mkdir()
    symlink_victim = outside_artifacts / "victim.txt"
    symlink_victim.write_text("must also survive cleanup\n")
    (output / "artifacts").symlink_to(outside_artifacts, target_is_directory=True)
    (output / "SUMMARY.md").write_text("old generated shape\n")
    (output / "META.json").write_text(
        json.dumps(
            {
                "files": [
                    "SUMMARY.md",
                    "META.json",
                    "../outside.txt",
                    "artifacts/victim.txt",
                ]
            }
        )
    )

    exported = export_handoff_dir(target, output_path=output)
    checked = export_handoff_dir(target, output_path=output, check=True)
    sync_checkpoint(target)
    checked_after_sync = export_handoff_dir(target, output_path=output, check=True)

    assert exported.path == str(output)
    assert checked.checked is True
    assert checked.fresh is True
    assert checked_after_sync.fresh is True
    readme = (output / "README.md").read_text()
    assert readme.startswith("# HK export")
    assert "Export a generated HK handoff package" in readme
    assert "Synthetic validation" in readme
    assert "hk export --format handoff-dir" in readme
    assert not (output / "SUMMARY.md").exists()
    assert escaped_file.read_text() == "must survive cleanup\n"
    assert symlink_victim.read_text() == "must also survive cleanup\n"
    assert not (output / "artifacts").is_symlink()
    metadata = json.loads((output / "meta.json").read_text())
    assert metadata["work_id"] == exported.work_id
    assert metadata["event_count"] >= 5
    assert metadata["evidence_count"] == 1
    assert metadata["diff_hash"].startswith("sha256:")
    assert metadata["files"] == ["README.md", "meta.json", "artifacts/README.md"]
    assert metadata["file_hashes"]["README.md"].startswith("sha256:")

    (target / "src.py").write_text("print('new source change')\n")
    with pytest.raises(LocalWorkflowError, match="stale metadata: diff_hash"):
        export_handoff_dir(target, output_path=output, check=True)
    (target / "src.py").unlink()
    export_handoff_dir(target, output_path=output)

    (output / "README.md").write_text("tampered\n")
    with pytest.raises(LocalWorkflowError, match="modified generated files"):
        export_handoff_dir(target, output_path=output, check=True)
    export_handoff_dir(target, output_path=output)

    add_note(target, kind="learning", text="Exports become stale after ledger changes.")
    with pytest.raises(LocalWorkflowError, match="stale metadata"):
        export_handoff_dir(target, output_path=output, check=True)


def test_cli_export_rejects_check_without_handoff_dir_format(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk(
            "start",
            "cli-export-error",
            "--target",
            str(target),
            "--plan",
            "Check export error.",
        ).returncode
        == 0
    )

    result = _run_hk("export", "--check", "--target", str(target))

    assert result.returncode == 1
    assert "require --format handoff-dir" in result.stderr


def test_cli_handoff_dir_export_json_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    output = target / ".ai" / "hk" / "cli-export"
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk(
            "start",
            "cli-export",
            "--target",
            str(target),
            "--plan",
            "Export through the CLI.",
            "--json",
        ).returncode
        == 0
    )

    result = _run_hk(
        "export",
        "--format",
        "handoff-dir",
        "--output",
        str(output),
        "--target",
        str(target),
        "--json",
    )
    check = _run_hk(
        "export",
        "--format",
        "handoff-dir",
        "--output",
        str(output),
        "--target",
        str(target),
        "--check",
        "--json",
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload["format"] == "handoff-dir"
    assert payload["path"] == str(output)
    assert check.returncode == 0, check.stderr
    assert json.loads(check.stdout)["checked"] is True


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


def test_git_diff_hash_tracks_untracked_symlink_identity(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    first_target = tmp_path / "outside-a.txt"
    second_target = tmp_path / "outside-b.txt"
    first_target.write_text("same bytes\n")
    second_target.write_text("same bytes\n")
    link = target / "external-link"
    link.symlink_to(first_target)
    first = git_diff_hash(target)

    link.unlink()
    link.symlink_to(second_target)
    second = git_diff_hash(target)

    assert first.startswith("sha256:")
    assert second.startswith("sha256:")
    assert second != first


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


@pytest.mark.parametrize(
    "bad_row",
    (
        "{not-json}\n",
        "{}\n",
        "[]\n",
        '{"seq": 1}\n',
        json.dumps(
            {
                "schema_version": 1,
                "seq": 2,
                "type": "sync_checkpoint",
                "at": "2026-01-01T00:00:00+00:00",
                "data": {
                    "event_seq": "not-an-int",
                    "diff_hash": "sha256:abc",
                    "excluded_paths": [],
                },
            }
        )
        + "\n",
    ),
)
def test_malformed_ledger_jsonl_fails_loudly(tmp_path: Path, bad_row: str) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "bad-ledger")
    Path(work.work_dir, "events.jsonl").write_text(bad_row)

    with pytest.raises(LocalWorkflowError, match="Malformed ledger JSONL"):
        add_note(target, kind="learning", text="This should not append.")


@pytest.mark.parametrize(
    "bad_row",
    (
        "{}\n",
        json.dumps(
            {
                "schema_version": 1,
                "id": "ev",
                "type": "command",
                "capture_mode": "captured",
                "kind": "test",
                "command_display": "cmd",
                "argv": "not-a-list",
                "cwd": ".",
                "target": ".",
                "branch": "main",
                "git_sha": "abc",
                "dirty_before": "false",
                "dirty_after": "false",
                "exit_code": 0,
                "status": "pass",
                "started_at": "now",
                "ended_at": "now",
                "duration_ms": 1,
                "transcript_path": "",
                "redaction": "builtin",
                "why": [],
            }
        )
        + "\n",
    ),
)
def test_malformed_evidence_jsonl_fails_loudly(tmp_path: Path, bad_row: str) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "bad-evidence")
    Path(work.work_dir, "evidence.jsonl").write_text(bad_row)

    with pytest.raises(LocalWorkflowError, match="Malformed evidence JSONL"):
        read_evidence(Path(work.work_dir))


def test_capture_rejects_shell_and_argv_together(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "capture-conflict")

    with pytest.raises(LocalWorkflowError, match="either --shell TEXT or argv"):
        capture_command(target, ("python3", "-V"), shell_command="echo nope")


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
    add_note(
        target, kind="spec-impact", text="SPEC documents lifecycle-first Harness Kit."
    )
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
    assert "hk evidence list --target . --json" in result.stderr


def test_cli_root_help_removes_legacy_commands() -> None:
    root = _run_hk("--help")
    legacy = _run_hk("legacy", "sync-check", "--help")
    attach = _run_hk("attach", "--help")

    assert root.returncode == 0
    assert "legacy" not in root.stdout.lower()
    assert "│ attach" not in root.stdout.lower()
    assert "legacy" not in legacy.stdout.lower()
    assert "sync-check" not in legacy.stdout.lower()
    assert "usage: hk attach" not in attach.stdout.lower()


def test_cli_review_help_warns_self_review_does_not_count() -> None:
    result = _run_hk("review", "add", "--help")

    assert result.returncode == 0
    assert (
        "Implementation-agent self-review does not satisfy readiness" in result.stdout
    )
    assert "independent AI/tool reviewer" in result.stdout
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


def test_dangerously_skip_sync_satisfies_readiness_and_handoff(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "skip-sync")
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
    stale = ready(target)

    skip = add_dangerous_skip(
        target,
        check="sync",
        label="agent-local-state",
        reason="Only .pi agent-local state changed after the last checkpoint.",
        mitigation="No source files changed after the sync checkpoint.",
    )
    done = ready(target)
    checked = sync_checkpoint(target, check=True)
    rendered = handoff(target)

    assert stale.ready is False
    assert skip.check == "sync"
    assert skip.label == "agent-local-state"
    assert checked.synced is True
    assert "sync dangerously skipped: agent-local-state" in checked.message
    assert done.ready is True
    assert done.status == "ready-with-dangerous-skips"
    assert any(
        check.id == "sync"
        and check.status == "pass"
        and "dangerously skipped" in check.message
        for check in done.checks
    )
    assert "Sync status: `sync-dangerously-skipped`" in rendered.content
    assert "## Dangerous skips" in rendered.content
    assert "Only .pi agent-local state changed" in rendered.content
    assert "No source files changed after the sync checkpoint" in rendered.content


def test_sync_exclude_allows_literal_untracked_local_path_without_stale_ready(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-sync")
    add_note(target, kind="plan", text="Implement the lifecycle facade.")
    add_note(target, kind="decision", text="Use validate as the primary evidence verb.")
    add_note(target, kind="spec-impact", text="none: No spec impact declared.")
    capture_command(target, ("python3", "-c", "print('ok')"), why="Smoke test.")
    add_review(
        target,
        backend="manual_external",
        reviewer="Alex",
        rubrics=("core-quality",),
        summary="No blocking findings.",
    )
    (target / "tmp-output").mkdir()
    (target / "tmp-output" / "session.json").write_text("{}")

    synced = sync_checkpoint(
        target,
        exclude_paths=("tmp-output",),
        reason="Only explicit local scratch output changed.",
    )
    done = ready(target)
    rendered = handoff(target)

    assert synced.synced is True
    assert done.ready is True
    assert done.status == "ready"
    assert "Sync status: `synced`" in rendered.content
    assert "## Sync exclusions" in rendered.content
    assert "tmp-output: Only explicit local scratch output changed." in rendered.content
    assert "## Dangerous skips" not in rendered.content


def test_sync_exclude_rejects_missing_reason_and_absent_path(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-errors")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}")

    with pytest.raises(LocalWorkflowError, match="requires --reason"):
        sync_checkpoint(target, exclude_paths=(".pi",))

    with pytest.raises(LocalWorkflowError, match="not present in git status"):
        sync_checkpoint(target, exclude_paths=(".pi/missing",), reason="Nope.")


@pytest.mark.parametrize(
    "exclude_path", (".", "/tmp/outside", "../outside", ":(glob)*", "*.py")
)
def test_sync_exclude_rejects_broad_or_pathspec_paths(
    tmp_path: Path, exclude_path: str
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-pathspec")

    with pytest.raises(LocalWorkflowError, match="sync --exclude"):
        sync_checkpoint(
            target,
            exclude_paths=(exclude_path,),
            reason="Should not be accepted.",
        )


def test_sync_exclude_rejects_tracked_source_paths(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-tracked")
    (target / "README.md").write_text("# modified\n")

    with pytest.raises(LocalWorkflowError, match="tracked paths or descendants"):
        sync_checkpoint(
            target,
            exclude_paths=("README.md",),
            reason="Tracked source changes must not be hidden.",
        )


def test_sync_exclude_rejects_staged_new_paths(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-staged")
    (target / "generated.txt").write_text("generated\n")
    subprocess.run(
        ["git", "add", "generated.txt"], cwd=target, check=True, env=_git_env()
    )

    with pytest.raises(LocalWorkflowError, match="tracked paths or descendants"):
        sync_checkpoint(
            target,
            exclude_paths=("generated.txt",),
            reason="Staged paths must not be hidden.",
        )


def test_sync_exclude_allows_untracked_literal_paths_without_allowlist(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-untracked-literal")
    (target / "src").mkdir()
    (target / "src" / "scratch.py").write_text("print('local')\n")

    synced = sync_checkpoint(
        target,
        exclude_paths=("src/scratch.py",),
        reason="Explicit local scratch file is intentionally excluded.",
    )

    assert synced.synced is True
    assert sync_checkpoint(target, check=True).synced is True


def test_sync_exclude_rejects_source_directory_with_tracked_descendants(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-source-dir")
    (target / "src").mkdir()
    (target / "src" / "app.py").write_text("print('tracked')\n")
    subprocess.run(["git", "add", "src/app.py"], cwd=target, check=True, env=_git_env())
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "add source"],
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
    (target / "src" / "tmp.log").write_text("local\n")

    with pytest.raises(LocalWorkflowError, match="tracked paths or descendants"):
        sync_checkpoint(
            target,
            exclude_paths=("src",),
            reason="Source directories with tracked descendants must not be excluded.",
        )


def test_sync_check_revalidates_stored_excludes_for_tracked_descendants(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-later-tracked-agent-local")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent state.",
    )
    (target / ".pi" / "tracked_source.py").write_text("print(1)\n")
    subprocess.run(
        ["git", "add", ".pi/tracked_source.py"],
        cwd=target,
        check=True,
        env=_git_env(),
    )

    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


def test_sync_exclude_rejects_agent_local_path_with_tracked_descendants(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    (target / ".pi").mkdir()
    (target / ".pi" / "tracked.txt").write_text("v1\n")
    subprocess.run(
        ["git", "add", ".pi/tracked.txt"], cwd=target, check=True, env=_git_env()
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "track pi file"],
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
    init_state(target)
    create_work(target, "exclude-tracked-agent-local")
    (target / ".pi" / "session.json").write_text("{}\n")

    with pytest.raises(LocalWorkflowError, match="tracked paths or descendants"):
        sync_checkpoint(
            target,
            exclude_paths=(".pi",),
            reason="Agent-local state with tracked descendants is unsafe.",
        )


def test_sync_exclude_does_not_hide_source_changes_after_checkpoint(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-source-change")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent session state changed.",
    )

    (target / "README.md").write_text("# changed\n")
    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False


def test_dangerously_skip_sync_requires_prior_checkpoint(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "skip-sync-without-checkpoint")

    with pytest.raises(LocalWorkflowError, match="requires a prior `hk sync`"):
        add_dangerous_skip(
            target,
            check="sync",
            label="missing-checkpoint",
            reason="No checkpoint exists yet.",
            mitigation="Run sync first.",
        )


def test_dangerously_skip_sync_goes_stale_after_later_work(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "skip-sync-stale")
    sync_checkpoint(target)
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}")
    add_dangerous_skip(
        target,
        check="sync",
        label="agent-local-state",
        reason="Only .pi agent-local state changed after checkpoint.",
        mitigation="No source files changed after the sync checkpoint.",
    )
    fresh = sync_checkpoint(target, check=True)

    add_note(
        target, kind="learning", text="A later lifecycle note should stale the skip."
    )
    stale = sync_checkpoint(target, check=True)

    assert fresh.synced is True
    assert "sync dangerously skipped: agent-local-state" in fresh.message
    assert stale.synced is False


def test_status_coaches_next_actions(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "coach-me")

    result = status(target)

    assert result.active_work.endswith("coach-me")
    assert result.ready_status == "not-ready"
    assert result.phase == "planning"
    assert any(action.startswith("plan:") for action in result.next_actions)
    assert any(
        action.startswith("context (optional):") for action in result.next_actions
    )
    assert any(action.startswith("decision:") for action in result.next_actions)
    assert any(action.startswith("validation:") for action in result.next_actions)
    assert any(action.startswith("review required:") for action in result.next_actions)


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


def test_cli_spec_promote_dry_run_json_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("spec", "init", "--local", "--target", str(target), "--json").returncode
        == 0
    )

    result = _run_hk("spec", "promote", "--dry-run", "--target", str(target), "--json")

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert "Would write local spec" in payload["preview"]


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


def test_cli_handoff_pr_format_renders_pr_body(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "handoff-pr", "--target", str(target), "--plan", "Ship it"
        ).returncode
        == 0
    )

    result = _run_hk("handoff", "--target", str(target), "--format", "pr")

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("## Summary")
    assert "## Validation" in result.stdout
    assert "# Handoff" not in result.stdout


def test_cli_handoff_pr_format_discloses_dangerous_skips(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "handoff-pr-skip", "--target", str(target), "--plan", "Ship it"
        ).returncode
        == 0
    )
    assert (
        _run_hk(
            "dangerously-skip",
            "review",
            "--label",
            "no-review",
            "--reason",
            "No independent reviewer before handoff.",
            "--mitigation",
            "Human review before merge.",
            "--target",
            str(target),
        ).returncode
        == 0
    )

    result = _run_hk("handoff", "--target", str(target), "--format", "pr")

    assert result.returncode == 0, result.stderr
    assert "## Dangerous skips" in result.stdout
    assert "no-review" in result.stdout
    assert "No independent reviewer before handoff." in result.stdout
    assert "Human review before merge." in result.stdout


def test_cli_dangerously_skip_requires_mitigation(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk("start", "skip-needs-mitigation", "--target", str(target)).returncode
        == 0
    )

    result = _run_hk(
        "dangerously-skip",
        "review",
        "--label",
        "no-review",
        "--reason",
        "No reviewer available.",
        "--target",
        str(target),
    )

    assert result.returncode != 0
    assert "--mitigation" in result.stderr


def test_cli_summary_renders_human_readiness_digest(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "summary-work", "--target", str(target), "--plan", "Ship it"
        ).returncode
        == 0
    )
    assert (
        _run_hk(
            "dangerously-skip",
            "review",
            "--label",
            "no-review",
            "--reason",
            "No independent reviewer before handoff.",
            "--mitigation",
            "Human review before merge.",
            "--target",
            str(target),
        ).returncode
        == 0
    )

    result = _run_hk("summary", "--target", str(target))

    assert result.returncode == 0, result.stderr
    assert result.stdout.startswith("# HK Readiness Summary")
    assert "## Validation" in result.stdout
    assert "## Review" in result.stdout
    assert "## Dangerous skips" in result.stdout
    assert "no-review" in result.stdout
    assert "Human review before merge." in result.stdout


def test_cli_handoff_format_json_is_not_a_file_format(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "handoff-json", "--target", str(target), "--plan", "Ship it"
        ).returncode
        == 0
    )

    result = _run_hk("handoff", "--target", str(target), "--format", "json")

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
    add_note(
        target, kind="spec-impact", text="SPEC documents lifecycle-first Harness Kit."
    )
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


def test_cli_start_plan_and_context_seed_lifecycle_notes(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    result = _run_hk(
        "start",
        "seeded-work",
        "--target",
        str(target),
        "--context",
        "Use Cyclopts conventions.",
        "--plan",
        "Implement the seeded lifecycle plan.",
        "--json",
    )
    handoff_result = _run_hk("handoff", "--target", str(target))
    status_result = _run_hk("status", "--target", str(target), "--json")

    assert result.returncode == 0, result.stderr
    assert "Use Cyclopts conventions." in handoff_result.stdout
    assert "Implement the seeded lifecycle plan." in handoff_result.stdout
    payload = json.loads(status_result.stdout)
    assert payload["active_work"].endswith("seeded-work")
    assert not any(action.startswith("plan:") for action in payload["next_actions"])


def test_cli_plan_without_active_work_points_to_start(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    result = _run_hk("plan", "legacy-looking-slug", "--target", str(target))

    assert result.returncode != 0
    assert "No active work. Run `hk start demo-work --plan" in result.stderr
    assert "hk legacy" not in result.stderr


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


def test_cli_decide_rejects_unknown_spec_impact(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "bad-spec-impact", "--target", str(target), "--plan", "Plan."
        ).returncode
        == 0
    )

    result = _run_hk(
        "decide",
        "Freeform impact should be rejected.",
        "--spec-impact",
        "freeform",
        "--target",
        str(target),
    )

    assert result.returncode != 0


def test_cli_decide_records_structured_spec_impact_refs(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "spec-impact", "--target", str(target), "--plan", "Plan."
        ).returncode
        == 0
    )

    result = _run_hk(
        "decide",
        "Update the lifecycle CLI shape.",
        "--spec-impact",
        "updated",
        "--spec-ref",
        "SPEC.md",
        "--spec-ref",
        "docs/harness-kit-lifecycle-design.md",
        "--target",
        str(target),
        "--json",
    )
    handoff_result = _run_hk("handoff", "--target", str(target))

    assert result.returncode == 0, result.stderr
    assert "updated: Spec/docs updated or verified." in handoff_result.stdout
    assert "SPEC.md" in handoff_result.stdout
    assert "docs/harness-kit-lifecycle-design.md" in handoff_result.stdout


def test_cli_review_prompt_prints_fresh_context_prompt(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert (
        _run_hk(
            "start", "review-prompt", "--target", str(target), "--plan", "Plan."
        ).returncode
        == 0
    )
    assert (
        _run_hk(
            "decide",
            "No behavior change.",
            "--spec-impact",
            "none",
            "--target",
            str(target),
        ).returncode
        == 0
    )

    result = _run_hk("review", "prompt", "--target", str(target))

    assert result.returncode == 0, result.stderr
    assert "independent AI/tool reviewer" in result.stdout
    assert "fresh-context subagent" in result.stdout
    assert "Minimum fallback" in result.stdout
    assert "Plan." in result.stdout
    assert "hk review add --backend subagent" in result.stdout


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
        "updated",
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
