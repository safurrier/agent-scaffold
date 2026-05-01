from __future__ import annotations

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
