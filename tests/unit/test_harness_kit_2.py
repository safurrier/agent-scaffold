from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from harness_toolkit.kit.local import (
    add_note,
    brief,
    capture_command,
    create_work,
    handoff,
    init_spec,
    init_state,
    materialize_work,
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
    materialized = materialize_work(target)

    assert init.ignored_by_local_git is True
    assert Path(work.work_dir, "events.jsonl").exists()
    assert note.seq == 2
    assert "Local state is okay" in Path(materialized.path).read_text()
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


def test_handoff_does_not_overclaim_without_evidence(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "handoff-work")
    add_note(target, kind="decision", text="Keep the shell primary.")

    result = handoff(target)

    assert "Keep the shell primary" in result.content
    assert "No validation evidence recorded" in result.content


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
