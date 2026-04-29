from __future__ import annotations

from pathlib import Path

import pytest

from scripts.slice_workflow import (
    SliceWorkflowError,
    inspect_status,
    render_phase_prompt,
)


def _write_plan(root: Path) -> Path:
    plan = root / ".ai" / "plans" / "2026-04-28-120000-demo"
    (plan / "artifacts").mkdir(parents=True)
    (plan / "META.yaml").write_text(
        "\n".join(
            [
                "slug: demo",
                "branch: feat/demo",
                "created: 2026-04-28",
                "pr:",
                "status: in-progress",
                "source: unit test",
                "contract_change: implementation_only",
                "decision_record: none",
                "review_mode: external_required",
                "review_backend:",
                "review_rubrics:",
                "  - core-quality",
                "evidence_required:",
                "  - commands",
                "  - report",
                "continues_from:",
                "supersedes:",
                "",
            ]
        )
    )
    (plan / "SPEC.md").write_text("# Specification\n\nImplement a demo slice.\n")
    (plan / "IMPLEMENTATION.md").write_text("# Implementation\n\n1. Render prompts.\n")
    (plan / "TODO.md").write_text("# TODO\n\n- [ ] Render the planner prompt\n")
    (plan / "DECISIONS.md").write_text(
        "# Decisions\n\n- Keep prompts provider-neutral.\n"
    )
    (plan / "LEARNING_LOG.md").write_text("# Learning Log\n\n- Started.\n")
    (plan / "VALIDATION.md").write_text(
        "# Validation\n\n```bash\nmise run check\n```\n"
    )
    (plan / "REVIEW.md").write_text("# Review\n\n- Pending external review.\n")
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


def test_render_phase_prompt_writes_prompt_and_task_snapshot(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path)
    task = tmp_path / "task.md"
    task.write_text("Add a dry-run flag.\n")
    _write_skill_template(
        tmp_path,
        "planner",
        "Plan {{plan_slug}} from {{task_path}}\n\n{{task_text}}\n\n{{plan_summary}}\n",
    )

    result = render_phase_prompt(root=tmp_path, phase="planner", task=str(task))

    assert result.changed is True
    assert result.prompt_path == ".ai/plans/2026-04-28-120000-demo/prompts/planner.md"
    prompt = (plan / "prompts" / "planner.md").read_text()
    assert "Add a dry-run flag." in prompt
    assert "Render the planner prompt" in prompt
    assert "Task - demo" in (plan / "TASK.md").read_text()


def test_render_phase_prompt_is_idempotent_when_content_is_unchanged(
    tmp_path: Path,
) -> None:
    _write_plan(tmp_path)
    task = tmp_path / "task.md"
    task.write_text("Add a dry-run flag.\n")
    _write_skill_template(tmp_path, "planner", "Plan {{plan_slug}}: {{task_text}}\n")

    first = render_phase_prompt(root=tmp_path, phase="planner", task=str(task))
    second = render_phase_prompt(root=tmp_path, phase="planner", task=str(task))

    assert first.changed is True
    assert second.changed is False


def test_slice_plan_requires_task_context(tmp_path: Path) -> None:
    _write_plan(tmp_path)
    _write_skill_template(tmp_path, "planner", "Plan {{plan_slug}}\n")

    with pytest.raises(SliceWorkflowError, match="slice-plan requires"):
        render_phase_prompt(root=tmp_path, phase="planner")


def test_unknown_template_variable_fails_fast(tmp_path: Path) -> None:
    task = tmp_path / "task.md"
    task.write_text("Do the work.\n")
    _write_plan(tmp_path)
    _write_skill_template(tmp_path, "planner", "Hello {{missing_value}}\n")

    with pytest.raises(SliceWorkflowError, match="unknown variable"):
        render_phase_prompt(root=tmp_path, phase="planner", task=str(task))


def test_inspect_status_reports_prompts_and_validation(tmp_path: Path) -> None:
    plan = _write_plan(tmp_path)
    (plan / "prompts").mkdir()
    (plan / "prompts" / "planner.md").write_text("prompt\n")

    status = inspect_status(root=tmp_path)

    assert status.slug == "demo"
    assert status.validation_has_commands is True
    assert status.prompts == {
        "planner": ".ai/plans/2026-04-28-120000-demo/prompts/planner.md"
    }
