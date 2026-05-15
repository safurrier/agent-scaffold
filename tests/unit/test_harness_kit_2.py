from __future__ import annotations

import hashlib
import json
import os
import subprocess
from dataclasses import asdict
from pathlib import Path

import pytest

import harness_toolkit.kit.local as local_module
from harness_toolkit.kit.local import (
    LocalWorkflowError,
    add_dangerous_skip,
    add_note,
    add_review,
    artifact_records,
    attach_artifact,
    brief,
    capture_command,
    create_work,
    export_handoff_dir,
    git_diff_hash,
    handoff,
    handoff_export_status,
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

pytestmark = pytest.mark.integration

ROOT = Path(__file__).resolve().parents[2]


def _git_env() -> dict[str, str]:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
        env.pop(name, None)
    env.setdefault("GIT_AUTHOR_NAME", "Test")
    env.setdefault("GIT_AUTHOR_EMAIL", "test@example.com")
    env.setdefault("GIT_COMMITTER_NAME", "Test")
    env.setdefault("GIT_COMMITTER_EMAIL", "test@example.com")
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
    assert result.git.available is True
    assert result.git.worktree_root == str(target)
    assert result.git.git_dir == str(target / ".git")
    assert result.git.git_common_dir == str(target / ".git")
    assert result.git.is_linked_worktree is False
    assert result.handoff_export.state == "no-active-work"
    assert result.handoff_export.path is None
    assert result.handoff_export.commands is not None
    assert "hk start" in result.handoff_export.commands["start"]
    external_result = brief(target, no_local_files=True)
    assert external_result.handoff_export.commands is not None
    assert "--no-local-files" in external_result.handoff_export.commands["start"]
    assert "AGENTS.md" in result.repo_surfaces
    assert ".mise.toml" in result.repo_surfaces
    payload = json.dumps(asdict(result))
    assert "recommended_profile" not in payload
    assert "recommended_command" not in payload
    assert "confidence" not in payload
    assert _git_status(target) == "?? .mise.toml\n?? AGENTS.md\n"


def test_brief_handoff_export_missing_avoids_expensive_freshness_check(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "missing-export")
    add_note(target, kind="plan", text="Check missing export cheaply.")

    resolve_calls = 0
    real_resolve_local_state = local_module.resolve_local_state

    def count_resolve_local_state(
        target_arg: Path, *, no_local_files: bool = False
    ) -> local_module.LocalState:
        nonlocal resolve_calls
        resolve_calls += 1
        return real_resolve_local_state(target_arg, no_local_files=no_local_files)

    def fail_ready_for_work(*args: object, **kwargs: object) -> None:
        raise AssertionError("missing export status should not compute readiness")

    monkeypatch.setattr(local_module, "resolve_local_state", count_resolve_local_state)
    monkeypatch.setattr(local_module, "ready_for_work", fail_ready_for_work)

    result = brief(target)

    assert resolve_calls == 1
    assert result.handoff_export.state == "missing"
    assert result.handoff_export.fresh is False
    assert result.handoff_export.stale_reasons == ["metadata missing"]


def test_brief_does_not_label_separate_git_dir_as_linked_worktree(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    git_dir = tmp_path / "separate-git-dir"
    target.mkdir()
    subprocess.run(
        ["git", "init", "--separate-git-dir", str(git_dir), str(target)],
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "checkout", "-b", "feat/demo"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    (target / "README.md").write_text("# demo\n")
    subprocess.run(
        ["git", "add", "README.md"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "chore: initial"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )

    result = brief(target)

    assert result.git.available is True
    assert result.git.git_dir == str(git_dir)
    assert result.git.git_common_dir == str(git_dir)
    assert result.git.is_linked_worktree is False


def test_brief_reports_git_linked_worktree_facts(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    worktree = tmp_path / "linked-worktree"
    subprocess.run(
        ["git", "worktree", "add", "--detach", str(worktree), "HEAD"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )

    result = brief(worktree)

    assert result.target_root == str(worktree)
    assert result.git.available is True
    assert result.git.worktree_root == str(worktree)
    assert result.git.git_dir is not None
    assert Path(result.git.git_dir).parent.name == "worktrees"
    assert result.git.git_common_dir == str(target / ".git")
    assert result.git.is_linked_worktree is True
    assert result.handoff_export.state == "no-active-work"


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
    assert "redaction=external" in rendered.content
    assert str(artifact.resolve()) in rendered.content


def test_artifact_list_returns_attached_records(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "list-artifacts")
    artifact = tmp_path / "pi-session.jsonl"
    artifact.write_text('{"event":"message"}\n')

    attached = attach_artifact(
        target,
        source_path=artifact,
        kind="pi-session-transcript",
        label="Pi session transcript",
        redaction="unknown",
    )

    records = artifact_records(target)

    assert records.work_id.endswith("list-artifacts")
    assert len(records.artifacts) == 1
    record = records.artifacts[0]
    assert record.seq == attached.seq
    assert record.kind == "pi-session-transcript"
    assert record.label == "Pi session transcript"
    assert record.sha256 == attached.sha256
    assert record.copied is True


def test_handoff_dir_export_includes_explicit_copied_artifacts(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-artifacts")
    add_note(target, kind="plan", text="Export attached artifacts.")
    artifact = tmp_path / "codex-review.md"
    artifact.write_text("# Codex review\nNo blockers.\n")
    attached = attach_artifact(
        target,
        source_path=artifact,
        kind="codex-review-summary",
        label="Codex review final message",
        redaction="external",
    )
    output = tmp_path / "handoff-export"

    exported = export_handoff_dir(target, output_path=output)
    metadata = json.loads((output / "meta.json").read_text())

    assert exported.path == str(output)
    attached_metadata = metadata["attached_artifacts"][0]
    export_path = attached_metadata["export_path"]
    assert attached_metadata["kind"] == "codex-review-summary"
    assert export_path in metadata["files"]
    copied = output / export_path
    assert copied.exists()
    assert copied.read_text() == artifact.read_text()
    assert metadata["file_hashes"][export_path] == attached.sha256
    assert "source_path" not in attached_metadata
    assert "artifact_path" not in attached_metadata
    assert str(artifact) not in (output / "README.md").read_text()
    assert attached.artifact_path not in (output / "README.md").read_text()
    assert ".harness-local/" not in (output / "README.md").read_text()
    assert export_path in (output / "README.md").read_text()


def test_artifact_attach_rejects_symlinked_artifacts_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "artifact-dir-symlink")
    artifact_dir = Path(work.work_dir) / "artifacts"
    shutil_target = tmp_path / "outside-artifacts"
    shutil_target.mkdir()
    artifact_dir.rmdir()
    artifact_dir.symlink_to(shutil_target, target_is_directory=True)
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")

    with pytest.raises(
        LocalWorkflowError, match="artifact directory must not be a symlink"
    ):
        attach_artifact(target, source_path=artifact, kind="codex-review")


def test_handoff_dir_export_rejects_tampered_artifact_kind_traversal(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "artifact-kind-traversal")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attach_artifact(target, source_path=artifact, kind="codex-review")
    events_path = Path(work.work_dir) / "events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text().splitlines()]
    for row in rows:
        if row["type"] == "artifact_attached":
            row["data"]["kind"] = "../../escape"
    events_path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    with pytest.raises(LocalWorkflowError, match="invalid artifact kind"):
        export_handoff_dir(target, output_path=tmp_path / "export")


def test_handoff_dir_export_rejects_tampered_artifact_source_outside_work(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "artifact-source-traversal")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attached = attach_artifact(target, source_path=artifact, kind="codex-review")
    external = tmp_path / "outside.md"
    external.write_text("review\n")
    events_path = Path(work.work_dir) / "events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text().splitlines()]
    for row in rows:
        if row["type"] == "artifact_attached":
            row["data"]["artifact_path"] = str(external)
            row["data"]["sha256"] = attached.sha256
    events_path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    with pytest.raises(LocalWorkflowError, match="not in this work's HK artifacts"):
        export_handoff_dir(target, output_path=tmp_path / "export")


def test_handoff_dir_export_check_rejects_symlinked_export_artifact(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "artifact-export-symlink")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attached = attach_artifact(target, source_path=artifact, kind="codex-review")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    metadata = json.loads((output / "meta.json").read_text())
    export_path = metadata["attached_artifacts"][0]["export_path"]
    exported_artifact = output / export_path
    exported_artifact.unlink()
    exported_artifact.symlink_to(Path(attached.artifact_path))

    with pytest.raises(LocalWorkflowError, match="symlinked files"):
        export_handoff_dir(target, output_path=output, check=True)


def test_handoff_dir_export_preserves_user_status_bullets(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-status-note")
    add_note(target, kind="plan", text="Status: important user context")
    output = tmp_path / "export"

    export_handoff_dir(target, output_path=output)

    assert "Status: important user context" in (output / "README.md").read_text()


def test_handoff_dir_export_check_rejects_unexpected_export_files(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-unexpected-files")
    add_note(target, kind="plan", text="Export unexpected file check.")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    (output / "extra.md").write_text("unexpected\n")

    with pytest.raises(LocalWorkflowError, match="unexpected files: extra.md"):
        export_handoff_dir(target, output_path=output, check=True)


def test_handoff_dir_export_check_rejects_invalid_utf8_generated_file(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-invalid-utf8")
    add_note(target, kind="plan", text="Export invalid UTF-8 check.")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    (output / "README.md").write_bytes(b"\xff\xfe")

    with pytest.raises(LocalWorkflowError, match="modified generated files"):
        export_handoff_dir(target, output_path=output, check=True)


def test_handoff_dir_export_check_rejects_modified_attached_artifact(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "artifact-export-modified")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attach_artifact(target, source_path=artifact, kind="codex-review")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    metadata = json.loads((output / "meta.json").read_text())
    export_path = metadata["attached_artifacts"][0]["export_path"]
    (output / export_path).write_text("tampered\n")

    with pytest.raises(LocalWorkflowError, match="modified attached artifacts"):
        export_handoff_dir(target, output_path=output, check=True)


def test_handoff_dir_export_check_rejects_missing_artifact_file_hash(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "artifact-export-missing-hash")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attach_artifact(target, source_path=artifact, kind="codex-review")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    meta_path = output / "meta.json"
    metadata = json.loads(meta_path.read_text())
    export_path = metadata["attached_artifacts"][0]["export_path"]
    (output / export_path).write_text("tampered\n")
    metadata["file_hashes"].pop(export_path)
    meta_path.write_text(json.dumps(metadata))

    with pytest.raises(LocalWorkflowError, match="stale attached artifact hashes"):
        export_handoff_dir(target, output_path=output, check=True)


def test_handoff_dir_export_check_rejects_unsafe_file_hash_metadata(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "artifact-export-unsafe-meta")
    artifact = tmp_path / "review.md"
    artifact.write_text("review\n")
    attach_artifact(target, source_path=artifact, kind="codex-review")
    output = tmp_path / "export"
    export_handoff_dir(target, output_path=output)
    meta_path = output / "meta.json"
    metadata = json.loads(meta_path.read_text())
    metadata["file_hashes"]["../outside.txt"] = "sha256:deadbeef"
    meta_path.write_text(json.dumps(metadata))

    with pytest.raises(LocalWorkflowError, match="unsafe file_hashes paths"):
        export_handoff_dir(target, output_path=output, check=True)


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


@pytest.mark.cli
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

    listed = _run_hk(
        "artifact",
        "list",
        "--target",
        str(target),
        "--json",
    )
    assert listed.returncode == 0, listed.stderr
    list_payload = json.loads(listed.stdout)
    assert list_payload["artifacts"][0]["kind"] == "agent-session"
    assert list_payload["artifacts"][0]["label"] == "Pi session transcript"


def test_handoff_dir_export_rejects_symlinked_output_parent(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-parent-symlink")
    add_note(target, kind="plan", text="Export safely.")
    outside = tmp_path / "outside-parent"
    outside.mkdir()
    hk_parent = target / ".ai" / "hk"
    hk_parent.parent.mkdir(parents=True)
    hk_parent.symlink_to(outside, target_is_directory=True)

    with pytest.raises(LocalWorkflowError, match="symlinked parent"):
        export_handoff_dir(target, output_path=hk_parent / "export-parent-symlink")
    with pytest.raises(LocalWorkflowError, match="symlinked parent"):
        export_handoff_dir(
            target, output_path=hk_parent / "export-parent-symlink", check=True
        )

    assert not (outside / "export-parent-symlink" / "README.md").exists()


def test_handoff_dir_export_does_not_follow_output_directory_symlink(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-dir-symlink")
    add_note(target, kind="plan", text="Export safely.")
    output = target / ".ai" / "hk" / "export-dir-symlink"
    outside = tmp_path / "outside-export"
    outside.mkdir()
    output.parent.mkdir(parents=True)
    output.symlink_to(outside, target_is_directory=True)

    export_handoff_dir(target, output_path=output)

    assert not output.is_symlink()
    assert not (outside / "README.md").exists()
    assert "HK export" in (output / "README.md").read_text()


def test_handoff_dir_export_does_not_follow_generated_file_symlink(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "export-symlink")
    add_note(target, kind="plan", text="Export safely.")
    output = target / ".ai" / "hk" / "export-symlink"
    export_handoff_dir(target, output_path=output)
    outside = tmp_path / "outside.md"
    outside.write_text("do not overwrite\n")
    (output / "README.md").unlink()
    (output / "README.md").symlink_to(outside)

    export_handoff_dir(target, output_path=output)

    assert outside.read_text() == "do not overwrite\n"
    assert not (output / "README.md").is_symlink()
    assert "HK export" in (output / "README.md").read_text()


def test_handoff_dir_export_hints_preserve_external_state_mode(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target, no_local_files=True)
    work = create_work(target, "external-export", no_local_files=True)
    add_note(
        target,
        kind="plan",
        text="Export external-state work.",
        no_local_files=True,
    )

    export_handoff_dir(target, no_local_files=True)
    output = target / ".ai" / "hk" / work.work_id
    readme = (output / "README.md").read_text()
    assert "--no-local-files --check" in readme
    status_result = brief(target, no_local_files=True).handoff_export
    assert status_result.commands is not None
    assert "--no-local-files" in status_result.commands["generate"]
    add_note(
        target,
        kind="learning",
        text="Stale external export.",
        no_local_files=True,
    )
    with pytest.raises(LocalWorkflowError, match="--no-local-files"):
        export_handoff_dir(target, check=True, no_local_files=True)


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
    export_handoff_dir(target, output_path=output)
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
    fresh_status = handoff_export_status(target, output_path=output)
    assert fresh_status.state == "fresh"
    assert fresh_status.path == str(output)
    assert fresh_status.readme_exists is True
    assert fresh_status.commands is not None
    assert "hk handoff" in fresh_status.commands["preview"]
    assert "hk export --format handoff-dir" in fresh_status.commands["generate"]

    (target / "src.py").write_text("print('new source change')\n")
    stale_status = handoff_export_status(target, output_path=output)
    assert stale_status.state == "stale"
    assert stale_status.fresh is False
    assert stale_status.readme_exists is True
    assert any(
        "stale metadata" in reason for reason in stale_status.stale_reasons or []
    )
    with pytest.raises(LocalWorkflowError, match="stale metadata: diff_hash"):
        export_handoff_dir(target, output_path=output, check=True)
    (target / "src.py").unlink()
    export_handoff_dir(target, output_path=output)

    metadata = json.loads((output / "meta.json").read_text())
    metadata["file_hashes"].pop("README.md")
    (output / "meta.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with pytest.raises(LocalWorkflowError, match="stale generated file hashes"):
        export_handoff_dir(target, output_path=output, check=True)
    export_handoff_dir(target, output_path=output)

    metadata = json.loads((output / "meta.json").read_text())
    metadata["file_hashes"]["README.md"] = "sha256:bad"
    (output / "meta.json").write_text(json.dumps(metadata, indent=2) + "\n")
    with pytest.raises(LocalWorkflowError, match="stale generated file hashes"):
        export_handoff_dir(target, output_path=output, check=True)
    export_handoff_dir(target, output_path=output)

    (output / "README.md").write_text("tampered\n")
    with pytest.raises(LocalWorkflowError, match="modified generated files"):
        export_handoff_dir(target, output_path=output, check=True)
    export_handoff_dir(target, output_path=output)

    (output / "README.md").write_text("tampered with matching recorded hash\n")
    forged_metadata = json.loads((output / "meta.json").read_text())
    forged_metadata["file_hashes"]["README.md"] = (
        "sha256:" + hashlib.sha256((output / "README.md").read_bytes()).hexdigest()
    )
    (output / "meta.json").write_text(json.dumps(forged_metadata, indent=2) + "\n")
    with pytest.raises(LocalWorkflowError, match="modified generated files"):
        export_handoff_dir(target, output_path=output, check=True)
    export_handoff_dir(target, output_path=output)

    add_note(target, kind="learning", text="Exports become stale after ledger changes.")
    with pytest.raises(LocalWorkflowError, match="stale metadata"):
        export_handoff_dir(target, output_path=output, check=True)


@pytest.mark.cli
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


@pytest.mark.cli
def test_cli_handoff_dir_export_check_json_reports_invalid_artifact_state(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "cli-invalid-artifact")
    add_note(target, kind="plan", text="Check invalid artifact JSON.")
    source = tmp_path / "artifact.log"
    source.write_text("original artifact\n")
    attached = attach_artifact(
        target,
        source_path=source,
        kind="codex-review-transcript",
        label="Codex review",
    )
    Path(attached.artifact_path).unlink()

    result = _run_hk(
        "export",
        "--format",
        "handoff-dir",
        "--target",
        str(target),
        "--check",
        "--json",
    )

    assert result.returncode == 1
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["state"] == "invalid"
    assert payload["fresh"] is False
    assert "attached copied artifact" in payload["message"]
    assert payload["stale_reasons"] == [payload["message"]]


def test_cli_handoff_dir_export_check_json_reports_missing_export(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk(
            "start",
            "cli-missing-export",
            "--target",
            str(target),
            "--plan",
            "Check missing export JSON.",
            "--json",
        ).returncode
        == 0
    )

    result = _run_hk(
        "export",
        "--format",
        "handoff-dir",
        "--target",
        str(target),
        "--check",
        "--json",
    )

    assert result.returncode == 1
    assert result.stderr == ""
    payload = json.loads(result.stdout)
    assert payload["state"] == "missing"
    assert payload["fresh"] is False
    assert payload["checked"] is True
    assert payload["path"] == str(target / ".ai" / "hk" / payload["work_id"])
    assert payload["readme_path"].endswith("/README.md")
    assert "metadata missing" in payload["stale_reasons"]
    assert "hk handoff" in payload["commands"]["preview"]
    assert "hk export --format handoff-dir" in payload["commands"]["generate"]


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


@pytest.mark.cli
def test_cli_evidence_bare_command_gives_list_hint() -> None:
    result = _run_hk("evidence", "--target", ".")

    assert result.returncode != 0
    assert "hk evidence list --target . --json" in result.stderr


@pytest.mark.cli
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


@pytest.mark.cli
def test_cli_review_help_warns_self_review_does_not_count() -> None:
    result = _run_hk("review", "add", "--help")

    assert result.returncode == 0
    assert (
        "Implementation-agent self-review does not satisfy readiness" in result.stdout
    )
    assert "independent AI/tool reviewer" in result.stdout
    assert "reviewer-fresh-context" in result.stdout


def test_review_remains_fresh_for_active_hk_export_changes(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "review-export-neutral")
    add_note(target, kind="plan", text="Review export-neutral behavior.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# reviewed\n")
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed source change.",
    )
    export_file = target / ".ai" / "hk" / Path(work.work_dir).name / "README.md"
    export_file.parent.mkdir(parents=True)
    export_file.write_text("# generated export refresh\n")

    result = ready(target)
    review_check = next(check for check in result.checks if check.id == "review")

    assert review_check.status == "pass"


def test_active_hk_export_does_not_make_ready_or_sync_stale(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "export-lifecycle-neutral")
    add_note(target, kind="plan", text="Keep active exports lifecycle neutral.")
    add_note(target, kind="decision", text="Generated exports are derived artifacts.")
    add_note(target, kind="spec-impact", text="updated")
    (target / "README.md").write_text("# lifecycle neutral export\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Synthetic validation before exporting.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed source change.",
    )
    sync_checkpoint(target)

    before_export = ready(target)
    exported = export_handoff_dir(target)
    checked = export_handoff_dir(target, check=True)
    sync_after_export = sync_checkpoint(target, check=True)
    after_export = ready(target)

    assert before_export.ready is True
    assert exported.path.endswith(f".ai/hk/{Path(work.work_dir).name}")
    assert checked.fresh is True
    assert sync_after_export.synced is True
    assert after_export.ready is True

    subprocess.run(
        ["git", "add", "README.md", ".ai/hk"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "commit active export"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    checked_after_commit = export_handoff_dir(target, check=True)

    assert checked_after_commit.fresh is True


def test_non_active_hk_export_changes_still_make_freshness_stale(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "other-export-is-real")
    add_note(target, kind="plan", text="Non-active exports are real changes.")
    add_note(target, kind="decision", text="Only active exports are neutral.")
    add_note(target, kind="spec-impact", text="not-needed")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Synthetic validation before unrelated export change.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed before unrelated export change.",
    )
    sync_checkpoint(target)

    other_export = target / ".ai" / "hk" / "other-work" / "README.md"
    other_export.parent.mkdir(parents=True)
    other_export.write_text("# other generated export\n")

    checked = sync_checkpoint(target, check=True)
    result = ready(target)
    validation_check = next(
        check for check in result.checks if check.id == "validation"
    )
    review_check = next(check for check in result.checks if check.id == "review")

    assert checked.synced is False
    assert "work changed after checkpoint" in checked.message
    assert validation_check.status == "fail"
    assert review_check.status == "fail"
    assert ".ai/hk/other-work/README.md" in validation_check.message
    assert ".ai/hk/other-work/README.md" in review_check.message


def test_legacy_sync_checkpoint_remains_fresh_after_active_export_neutrality_upgrade(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "legacy-sync-compat")
    active_export = target / ".ai" / "hk" / Path(work.work_dir).name / "README.md"
    active_export.parent.mkdir(parents=True)
    active_export.write_text("# generated active export\n")
    legacy_hash = git_diff_hash(target)
    events_path = Path(work.work_dir) / "events.jsonl"
    sync_event = {
        "schema_version": 1,
        "seq": 2,
        "type": "sync_checkpoint",
        "at": "2026-05-15T00:00:00+00:00",
        "data": {
            "git_sha": "legacy",
            "diff_hash": legacy_hash,
            "event_seq": 1,
            "evidence_count": 0,
            "note_count": 0,
        },
    }
    with events_path.open("a") as file:
        file.write(json.dumps(sync_event, sort_keys=True) + "\n")

    checked = sync_checkpoint(target, check=True)

    assert checked.synced is True


def test_review_reports_source_paths_changed_after_review(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "review-source-stale")
    add_note(target, kind="plan", text="Review source staleness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# reviewed\n")
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed first source change.",
    )
    (target / "README.md").write_text("# changed after review\n")

    result = ready(target)
    review_check = next(check for check in result.checks if check.id == "review")

    assert review_check.status == "fail"
    assert "README.md" in review_check.message
    assert "targeted follow-up" in review_check.message


def test_review_add_path_normalizes_dot_slash(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "review-dot-slash")
    (target / "README.md").write_text("# reviewed\n")

    review = add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed README follow-up.",
        reviewed_paths=("./README.md",),
    )

    assert review.reviewed_paths == ["README.md"]


def test_targeted_follow_up_reviews_cover_changed_paths(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "review-targeted-follow-up")
    add_note(target, kind="plan", text="Review targeted follow-up behavior.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# reviewed\n")
    (target / "tests").mkdir()
    (target / "tests" / "test_demo.py").write_text(
        "def test_demo():\n    assert True\n"
    )

    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed README follow-up.",
        reviewed_paths=("README.md",),
    )
    first = ready(target)
    first_review = next(check for check in first.checks if check.id == "review")
    assert first_review.status == "fail"
    assert "tests/test_demo.py" in first_review.message

    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Reviewed test follow-up.",
        reviewed_paths=("tests/test_demo.py",),
    )
    second = ready(target)
    second_review = next(check for check in second.checks if check.id == "review")
    assert second_review.status == "pass"


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
    work = create_work(target, "skip-sync")
    add_note(target, kind="plan", text="Implement the lifecycle facade.")
    add_note(target, kind="decision", text="Use validate as the primary evidence verb.")
    add_note(target, kind="spec-impact", text="No spec impact declared.")
    capture_command(target, ("python3", "-c", "print('ok')"), why="Smoke test.")
    add_review(
        target,
        backend="manual_external",
        reviewer="Alex",
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
    skip_event = json.loads(
        (Path(work.work_dir) / "events.jsonl").read_text().splitlines()[-1]
    )

    assert skip.check == "sync"
    assert skip.label == "agent-local-state"
    assert skip_event["data"]["implicit_excluded_paths"] == [
        f".ai/hk/{Path(work.work_dir).name}"
    ]
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


def test_sync_check_revalidates_excluded_untracked_file_content(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-file-content-change")
    scratch = target / ".pi" / "session.json"
    scratch.parent.mkdir()
    scratch.write_text("{}\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi/session.json",),
        reason="Only local agent state.",
    )

    scratch.write_text('{"changed": true}\n')
    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


def test_sync_check_revalidates_excluded_untracked_directory_new_file(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-dir-new-file")
    scratch_dir = target / ".pi"
    scratch_dir.mkdir()
    (scratch_dir / "session.json").write_text("{}\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent state.",
    )

    (scratch_dir / "later.json").write_text("{}\n")
    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


def test_sync_check_revalidates_excluded_untracked_nested_git_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "exclude-nested-git-dir")
    nested = target / ".pi" / "nested"
    nested.mkdir(parents=True)
    subprocess.run(["git", "init"], cwd=nested, check=True, capture_output=True)
    (nested / "state.txt").write_text("v1\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent state.",
    )

    (nested / "state.txt").write_text("v2\n")
    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


@pytest.mark.parametrize(
    "replacement_metadata",
    (
        [],
        [{"path": ".other", "state_hash": "sha256:missing"}],
    ),
)
def test_sync_check_fails_closed_when_exclude_metadata_is_incomplete_or_mismatched(
    tmp_path: Path, replacement_metadata: list[dict[str, str]]
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "exclude-bad-metadata")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent state.",
    )
    events_path = Path(work.work_dir) / "events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text().splitlines()]
    rows[-1]["data"]["excluded"] = replacement_metadata
    events_path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


def test_sync_check_fails_closed_when_exclude_metadata_is_missing(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    work = create_work(target, "exclude-missing-metadata")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}\n")
    sync_checkpoint(
        target,
        exclude_paths=(".pi",),
        reason="Only local agent state.",
    )
    events_path = Path(work.work_dir) / "events.jsonl"
    rows = [json.loads(line) for line in events_path.read_text().splitlines()]
    rows[-1]["data"].pop("excluded")
    events_path.write_text("".join(json.dumps(row) + "\n" for row in rows))

    checked = sync_checkpoint(target, check=True)

    assert checked.synced is False
    assert "excluded path changed" in checked.message


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


def test_ready_accepts_evidence_with_existing_agent_local_state_after_sync_skip(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "skip-sync-existing-agent-local")
    add_note(target, kind="plan", text="Exercise existing local state freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation includes unchanged agent-local state.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review includes unchanged agent-local state.",
    )
    sync_checkpoint(target)
    add_dangerous_skip(
        target,
        check="sync",
        label="agent-local-state",
        reason="Only existing .pi agent-local state is untracked.",
        mitigation="No source files changed after validation/review.",
    )

    result = ready(target)

    messages = {check.id: check.message for check in result.checks}
    assert result.ready is True
    assert messages["validation"] == "validation evidence with rationale recorded"
    assert messages["review"] == "external-enough review recorded"
    assert messages["sync"].startswith("sync dangerously skipped")


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
    review_actions = [
        action
        for action in result.next_actions
        if action.startswith("review required:")
    ]
    assert review_actions
    assert "do not skip just because" in review_actions[0]
    assert "fresh-context subagent" in review_actions[0]


def test_status_ignores_profile_suggestion_resolution_key_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from harness_toolkit.kit import local as local_module
    from harness_toolkit.kit.readiness.diagnostics import ReadyResult

    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "profile-suggestion-error")
    (target / "src").mkdir()
    (target / "src" / "changed.py").write_text("print('changed')\n")

    monkeypatch.setattr(
        local_module,
        "ready_for_work",
        lambda *args, **kwargs: ReadyResult(
            work_id="profile-suggestion-error",
            ready=False,
            status="not-ready",
            checks=[],
        ),
    )

    def raise_key_error(*args: object, **kwargs: object) -> object:
        raise KeyError("Unknown profile 'missing'")

    monkeypatch.setattr(local_module.ProfileContext, "resolve", raise_key_error)

    result = status(target)

    assert result.active_work.endswith("profile-suggestion-error")
    assert result.suggested_checks == []
    assert result.suggested_reviews == []


def test_status_prompts_exact_agent_local_sync_exclusion(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "agent-local-sync")
    add_note(target, kind="plan", text="Exercise local state guidance.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers current diff.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers current diff.",
    )
    sync_checkpoint(target)
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}\n")

    result = status(target)

    sync_actions = [
        action for action in result.next_actions if action.startswith("sync:")
    ]
    assert sync_actions
    assert "agent-local state is blocking readiness" in sync_actions[0]
    assert "hk sync --exclude .pi --reason agent-local-state" in sync_actions[0]


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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


def test_ready_accepts_fresh_validation_when_preexisting_local_state_is_excluded(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "preexisting-local-exclude")
    add_note(target, kind="plan", text="Exercise preexisting local excludes.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / ".pi").mkdir()
    (target / ".pi" / "session.json").write_text("{}\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers source diff while local state exists.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers source diff while local state exists.",
    )

    sync_checkpoint(target, exclude_paths=(".pi",), reason="Only local agent state.")
    result = ready(target)

    assert result.ready is True
    messages = {check.id: check.message for check in result.checks}
    assert messages["validation"] == "validation evidence with rationale recorded"
    assert messages["review"] == "external-enough review recorded"


def test_ready_accepts_validation_when_validated_diff_is_committed_unchanged(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "validated-then-committed")
    add_note(target, kind="plan", text="Exercise committed equivalent diff.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# validated change\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers the README change.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers the README change.",
    )
    subprocess.run(["git", "add", "README.md"], cwd=target, check=True, env=_git_env())
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "commit validated readme"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    sync_checkpoint(target)

    result = ready(target)

    assert result.ready is True
    messages = {check.id: check.message for check in result.checks}
    assert messages["validation"] == "validation evidence with rationale recorded"
    assert messages["review"] == "external-enough review recorded"


def test_ready_accepts_validation_when_new_untracked_file_is_committed_unchanged(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "validated-new-file")
    add_note(target, kind="plan", text="Exercise untracked to committed freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "NEW.md").write_text("# new\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers the new file.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers the new file.",
    )
    subprocess.run(["git", "add", "NEW.md"], cwd=target, check=True, env=_git_env())
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "commit new file"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    sync_checkpoint(target)

    result = ready(target)

    assert result.ready is True


def test_ready_rejects_stale_validation_after_committed_work_change(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "stale-after-commit")
    add_note(target, kind="plan", text="Exercise committed freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers initial committed state.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers initial committed state.",
    )
    sync_checkpoint(target)
    (target / "README.md").write_text("# committed change\n")
    subprocess.run(["git", "add", "README.md"], cwd=target, check=True, env=_git_env())
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "change readme"],
        cwd=target,
        check=True,
        capture_output=True,
        env=_git_env(),
    )
    sync_checkpoint(target)

    result = ready(target)

    assert result.ready is False
    messages = {check.id: check.message for check in result.checks}
    assert "validation evidence is stale" in messages["validation"]
    assert "does not cover current changed paths" in messages["review"]


def test_ready_rejects_stale_validation_and_review_after_diff_changes(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "stale-validation-review")
    add_note(target, kind="plan", text="Exercise freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# v1\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers v1.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers v1.",
    )

    (target / "README.md").write_text("# v2\n")
    sync_checkpoint(target)
    result = ready(target)

    assert result.ready is False
    messages = {check.id: check.message for check in result.checks}
    assert "validation evidence is stale" in messages["validation"]
    assert "README.md" in messages["validation"]
    assert "does not cover current changed paths" in messages["review"]
    assert "README.md" in messages["review"]


def test_capture_rejects_bare_env_assignment_with_actionable_hint(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "env-assignment")

    with pytest.raises(LocalWorkflowError) as exc_info:
        capture_command(
            target,
            ("PYTHONPATH=src", "pytest", "-q"),
            kind="test",
            why="Exercise env assignment guidance.",
        )

    message = str(exc_info.value)
    assert "environment assignments" in message
    assert "env PYTHONPATH=src" in message
    assert "--shell 'KEY=value command ...'" in message


def test_dangerous_sync_skip_does_not_hide_source_diff_from_freshness(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "sync-skip-source-change")
    add_note(target, kind="plan", text="Exercise sync skip source freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    (target / "README.md").write_text("# v1\n")
    capture_command(
        target,
        ("python3", "-c", "print('ok')"),
        kind="test",
        why="Validation covers v1.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers v1.",
    )
    sync_checkpoint(target)

    (target / "README.md").write_text("# v2\n")
    add_dangerous_skip(
        target,
        check="sync",
        label="claimed-local-only",
        reason="Pretend only local state changed.",
        mitigation="Freshness should still catch source changes.",
    )
    result = ready(target)

    assert result.ready is False
    messages = {check.id: check.message for check in result.checks}
    assert "validation evidence is stale" in messages["validation"]
    assert "does not cover current changed paths" in messages["review"]


def test_dangerous_validation_skip_goes_stale_after_diff_changes(
    tmp_path: Path,
) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    init_state(target)
    create_work(target, "stale-validation-skip")
    add_note(target, kind="plan", text="Exercise skip freshness.")
    add_note(target, kind="decision", text="No spec impact.")
    add_note(target, kind="spec-impact", text="not-needed")
    add_dangerous_skip(
        target,
        check="validation",
        label="not-run",
        reason="No validation available in fixture.",
        mitigation="This is a freshness test.",
    )
    add_review(
        target,
        backend="subagent",
        reviewer="reviewer-fresh-context",
        summary="Review covers current diff.",
    )

    (target / "README.md").write_text("# changed\n")
    sync_checkpoint(target)
    result = ready(target)

    assert result.ready is False
    messages = {check.id: check.message for check in result.checks}
    assert messages["validation"] == "missing validation evidence with --why"


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


@pytest.mark.cli
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


@pytest.mark.cli
def test_cli_plan_without_active_work_points_to_start(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)

    result = _run_hk("plan", "legacy-looking-slug", "--target", str(target))

    assert result.returncode != 0
    assert "No active work. Run `hk start demo-work --plan" in result.stderr
    assert "hk legacy" not in result.stderr


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
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


@pytest.mark.cli
def test_cli_capture_timeout_json_is_parseable(tmp_path: Path) -> None:
    target = tmp_path / "repo"
    _git_init(target)
    assert _run_hk("init", "--target", str(target), "--json").returncode == 0
    assert (
        _run_hk("work", "start", "capture-timeout", "--target", str(target)).returncode
        == 0
    )

    result = _run_hk(
        "capture",
        "--target",
        str(target),
        "--json",
        "--timeout-seconds",
        "1",
        "--",
        "python3",
        "-c",
        "import time; time.sleep(5)",
    )

    assert result.returncode == 124
    payload = json.loads(result.stdout)
    assert payload["timed_out"] is True
    assert payload["exit_code"] == 124


@pytest.mark.cli
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
