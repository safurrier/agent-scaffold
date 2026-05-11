from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SKILL_CLI_SRC = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / ".agent"
    / "skills"
    / "slice-workflow"
    / "cli"
    / "src"
)
sys.path.insert(0, str(SKILL_CLI_SRC))

from slice_workflow_cli.cli import main  # noqa: E402

pytestmark = pytest.mark.cli


def _write_plan(root: Path, *, status: str = "complete") -> Path:
    plan = root / ".ai" / "plans" / "2026-04-30-120000-cli-demo"
    (plan / "artifacts").mkdir(parents=True)
    (plan / "META.yaml").write_text(
        "\n".join(
            [
                "slug: cli-demo",
                "branch: feat/cli-demo",
                "created: 2026-04-30",
                "pr:",
                f"status: {status}",
                "source: unit test",
                "contract_change: implementation_only",
                "decision_record: none",
                "review_mode: external_required",
                "review_backend: manual_external",
                "review_rubrics:",
                "  - core-quality",
                "evidence_required:",
                "  - commands",
                "continues_from:",
                "supersedes:",
                "",
            ]
        )
    )
    (plan / "SPEC.md").write_text("# Specification\n\nImplement CLI tests.\n")
    (plan / "IMPLEMENTATION.md").write_text(
        "# Implementation\n\n- Cover CLI dispatch.\n"
    )
    (plan / "TODO.md").write_text("# TODO\n\n- [x] Add CLI coverage\n")
    (plan / "DECISIONS.md").write_text(
        "\n".join(
            [
                "# Decisions",
                "",
                "## What Changed",
                "",
                "- Added CLI seam tests.",
                "",
                "## Why",
                "",
                "- The skill CLI is now an execution boundary.",
                "",
            ]
        )
    )
    (plan / "LEARNING_LOG.md").write_text("# Learning Log\n\n- Added CLI tests.\n")
    (plan / "VALIDATION.md").write_text(
        "# Validation\n\n```bash\nmise run check\n```\n"
    )
    (plan / "REVIEW.md").write_text(
        "\n".join(
            [
                "# Review",
                "",
                "## Review Context",
                "",
                "- Mode: external",
                "- Backend: manual_external",
                "- Reviewer: unit-test-reviewer",
                "",
                "## Rubrics",
                "",
                "- core-quality",
                "",
                "## Findings",
                "",
                "- No blocking findings.",
                "",
                "## Disposition",
                "",
                "- PASS.",
                "",
            ]
        )
    )
    (plan / "artifacts" / "manifest.yaml").write_text("artifacts:\n")
    return plan


def _git_commit_all(root: Path) -> None:
    subprocess.run(["git", "add", "."], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "commit", "--no-verify", "-m", "test"],
        cwd=root,
        check=True,
        capture_output=True,
        env=os.environ.copy()
        | {
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
        },
    )


def _git_init_and_commit(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, capture_output=True)
    subprocess.run(
        ["git", "checkout", "-b", "feat/test"],
        cwd=root,
        check=True,
        capture_output=True,
    )
    _git_commit_all(root)


def _write_skill_template(root: Path, phase: str, content: str) -> None:
    template = (
        root
        / "templates"
        / ".agent"
        / "skills"
        / "slice-workflow"
        / "templates"
        / f"{phase}.md"
    )
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(content)


def _run_cli(argv: list[str]) -> int:
    with pytest.raises(SystemExit) as exc_info:
        main(argv)
    code = exc_info.value.code
    assert isinstance(code, int)
    return code


def test_module_entrypoint_help_exits_successfully() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SKILL_CLI_SRC)

    result = subprocess.run(
        [sys.executable, "-m", "slice_workflow_cli", "--help"],
        capture_output=True,
        check=False,
        env=env,
        text=True,
    )

    assert result.returncode == 0
    assert "slice-workflow" in result.stdout
    assert "sync-check" in result.stdout


def test_status_json_uses_explicit_repo_root(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _write_plan(tmp_path, status="in-progress")

    code = _run_cli(["--repo", str(tmp_path), "status", "--json"])

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["slug"] == "cli-demo"
    assert output["plan_path"] == str(plan.relative_to(tmp_path))
    assert output["validation_has_commands"] is True


def test_render_json_writes_prompt_and_task_snapshot(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _write_plan(tmp_path, status="in-progress")
    _write_skill_template(
        tmp_path,
        "planner",
        "Plan {{plan_slug}}\n\nTask: {{task_text}}\n",
    )

    code = _run_cli(
        [
            "--repo",
            str(tmp_path),
            "render",
            "planner",
            "--task-text",
            "Add CLI test coverage.",
            "--json",
        ]
    )

    assert code == 0
    output = json.loads(capsys.readouterr().out)
    assert output["changed"] is True
    assert output["prompt_path"] == str(
        plan.relative_to(tmp_path) / "prompts/planner.md"
    )
    assert "Add CLI test coverage." in (plan / "TASK.md").read_text()
    assert "Add CLI test coverage." in (plan / "prompts" / "planner.md").read_text()


def test_render_missing_planner_task_returns_error(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_plan(tmp_path, status="in-progress")
    _write_skill_template(tmp_path, "planner", "Plan {{plan_slug}}\n")

    code = _run_cli(["--repo", str(tmp_path), "render", "planner"])

    captured = capsys.readouterr()
    assert code == 1
    assert "error:" in captured.err
    assert captured.out == ""


def _write_hk_export(root: Path, work_id: str = "2026-05-09-120000-demo") -> Path:
    export = root / ".ai" / "hk" / work_id
    (export / "artifacts").mkdir(parents=True)
    for filename in (
        "README.md",
        "artifacts/README.md",
    ):
        (export / filename).write_text(f"# {filename}\n")
    file_hashes = {}
    for path in export.rglob("*.md"):
        file_hashes[path.relative_to(export).as_posix()] = (
            "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
        )
    (export / "meta.json").write_text(
        json.dumps(
            {
                "schema_version": 1,
                "generated_by": "hk export --format handoff-dir",
                "work_id": work_id,
                "git_sha": "abc123",
                "diff_hash": "sha256:" + "0" * 64,
                "event_count": 1,
                "event_seq": 1,
                "evidence_count": 0,
                "output_path": f".ai/hk/{work_id}",
                "files": ["README.md", "meta.json", "artifacts/README.md"],
                "file_hashes": file_hashes,
            }
        )
    )
    return export


def test_sync_check_validates_hk_exports_when_present(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    _write_hk_export(tmp_path)
    _git_init_and_commit(tmp_path)

    code = _run_cli(["--repo", str(tmp_path), "sync-check"])

    assert code == 0
    assert "HK export ready" in capsys.readouterr().out


def test_sync_check_validates_changed_hk_exports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "checkout", "-b", "feat/test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "README.md").write_text("# demo\n")
    _git_commit_all(tmp_path)
    _write_hk_export(tmp_path)
    subprocess.run(
        ["git", "add", ".ai/hk"], cwd=tmp_path, check=True, capture_output=True
    )

    code = _run_cli(
        ["--repo", str(tmp_path), "sync-check", "--changed-hk-exports", "HEAD"]
    )

    assert code == 0
    assert "HK export ready" in capsys.readouterr().out


def test_sync_check_requires_changed_hk_export_for_meaningful_changes(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "checkout", "-b", "feat/test"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / "README.md").write_text("# demo\n")
    _git_commit_all(tmp_path)
    (tmp_path / "src.py").write_text("print('change')\n")
    subprocess.run(
        ["git", "add", "src.py"], cwd=tmp_path, check=True, capture_output=True
    )

    code = _run_cli(
        ["--repo", str(tmp_path), "sync-check", "--changed-hk-exports", "HEAD"]
    )

    assert code == 1
    captured = capsys.readouterr()
    assert "no changed HK export" in captured.err
    assert "src.py" in captured.err


def test_sync_check_rejects_obsolete_hk_export_files(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = _write_hk_export(tmp_path)
    (export / "VALIDATION.md").write_text("old shape\n")
    _git_init_and_commit(tmp_path)

    code = _run_cli(["--repo", str(tmp_path), "sync-check"])

    assert code == 1
    captured = capsys.readouterr()
    assert "obsolete generated files" in captured.err
    assert "VALIDATION.md" in captured.err


def test_sync_check_rejects_metadata_with_wrong_hk_export_files_list(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = _write_hk_export(tmp_path)
    metadata = json.loads((export / "meta.json").read_text())
    metadata["files"] = ["README.md", "meta.json", "VALIDATION.md"]
    (export / "meta.json").write_text(json.dumps(metadata))
    _git_init_and_commit(tmp_path)

    code = _run_cli(["--repo", str(tmp_path), "sync-check"])

    assert code == 1
    assert "files list does not match compact package shape" in capsys.readouterr().err


def test_sync_check_rejects_incomplete_hk_exports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = _write_hk_export(tmp_path)
    (export / "README.md").unlink()
    _git_init_and_commit(tmp_path)

    code = _run_cli(["--repo", str(tmp_path), "sync-check"])

    assert code == 1
    assert "HK export is missing required files" in capsys.readouterr().err


def test_sync_check_reports_corrupt_hk_export_metadata_with_repair_hint(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    export = _write_hk_export(tmp_path)
    metadata = json.loads((export / "meta.json").read_text())
    metadata["event_count"] = "abc"
    (export / "meta.json").write_text(json.dumps(metadata))
    _git_init_and_commit(tmp_path)

    code = _run_cli(["--repo", str(tmp_path), "sync-check"])

    assert code == 1
    captured = capsys.readouterr()
    assert "event_count must be an integer" in captured.err
    assert "hk export --format handoff-dir" in captured.err


def test_sync_check_plan_dir_runs_all_contract_checks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    plan = _write_plan(tmp_path)

    code = _run_cli(
        [
            "--repo",
            str(tmp_path),
            "sync-check",
            "--plan-dir",
            str(plan.relative_to(tmp_path)),
        ]
    )

    assert code == 0
    assert "Sync-check passed" in capsys.readouterr().out
