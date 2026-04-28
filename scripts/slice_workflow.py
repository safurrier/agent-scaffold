"""Prompt rendering and status helpers for the slice workflow tasks.

The public interface is the file-based mise tasks. This module is intentionally
stdlib-only so generated Go/Rust projects can render prompts without installing
the scaffold Python package or extra dependencies.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from scripts.lib import PROJECT_ROOT, log_error, log_ok, log_step
from scripts.plan_contract import (
    ArtifactEntry,
    PlanContext,
    current_plan_context,
    file_has_meaningful_content,
    missing_required_plan_files,
    parse_artifact_manifest,
    parse_meta_yaml,
    validation_has_commands,
)

WORKFLOW_SKILL_NAME = "slice-workflow"
PROMPTS_DIR_NAME = "prompts"
TASK_SNAPSHOT_NAME = "TASK.md"
TEMPLATE_VAR_RE = re.compile(r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}")

PHASE_TEMPLATE_FILES = {
    "planner": "planner.md",
    "implementer": "implementer.md",
    "reviewer": "reviewer.md",
}

PHASE_OUTPUT_FILES = {
    "planner": "planner.md",
    "implementer": "implementer.md",
    "reviewer": "reviewer.md",
}

VALID_PHASES = tuple(PHASE_TEMPLATE_FILES)


class SliceWorkflowError(RuntimeError):
    """Expected workflow error that should be shown without a traceback."""


@dataclass(frozen=True)
class RenderResult:
    phase: str
    plan_path: str
    prompt_path: str
    task_path: str
    printed: bool
    changed: bool


@dataclass(frozen=True)
class SliceStatus:
    plan_path: str
    slug: str
    branch: str
    status: str
    required_files_missing: list[str]
    prompts: dict[str, str]
    validation_has_commands: bool
    review_has_content: bool
    artifact_count: int


def _relative(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _load_plan(root: Path, plan_arg: str | None) -> PlanContext:
    if plan_arg:
        plan_path = Path(plan_arg)
        if not plan_path.is_absolute():
            plan_path = root / plan_path
        meta = parse_meta_yaml(plan_path / "META.yaml")
        if meta is None:
            raise SliceWorkflowError(
                f"Plan not found or missing META.yaml: {_relative(plan_path, root)}"
            )
        return PlanContext(path=plan_path, meta=meta)

    plan = current_plan_context(root)
    if plan is None:
        raise SliceWorkflowError(
            "No active plan found. Run `mise run plan -- <slug>` first, then retry."
        )
    return plan


def _workflow_skill_dir(root: Path) -> Path:
    candidates = [
        root / ".agent" / "skills" / WORKFLOW_SKILL_NAME,
        root / "templates" / ".agent" / "skills" / WORKFLOW_SKILL_NAME,
    ]
    for candidate in candidates:
        if candidate.is_dir():
            return candidate
    raise SliceWorkflowError(
        "slice-workflow skill not found. Expected .agent/skills/slice-workflow "
        "or templates/.agent/skills/slice-workflow."
    )


def _template_path(root: Path, phase: str) -> Path:
    if phase not in PHASE_TEMPLATE_FILES:
        raise SliceWorkflowError(
            f"Unknown slice workflow phase '{phase}'. Valid phases: "
            f"{', '.join(VALID_PHASES)}"
        )
    path = _workflow_skill_dir(root) / "templates" / PHASE_TEMPLATE_FILES[phase]
    if not path.exists():
        raise SliceWorkflowError(f"Prompt template missing: {_relative(path, root)}")
    return path


def _read_task_context(
    root: Path, task: str | None, task_text: str | None
) -> tuple[str, str]:
    if task and task_text:
        raise SliceWorkflowError("Use either --task or --task-text, not both.")
    if task:
        task_path = Path(task)
        if not task_path.is_absolute():
            task_path = root / task_path
        if not task_path.exists():
            raise SliceWorkflowError(
                f"Task file not found: {_relative(task_path, root)}"
            )
        return task_path.read_text().strip(), _relative(task_path, root)
    if task_text:
        return task_text.strip(), "(inline task text)"
    return "", ""


def _write_task_snapshot(plan: PlanContext, task_body: str, task_path: str) -> str:
    if not task_body:
        return ""

    target = plan.path / TASK_SNAPSHOT_NAME
    content = "\n".join(
        [
            f"# Task - {plan.meta.slug}",
            "",
            f"- Source: {task_path}",
            "",
            "## Task Text",
            "",
            task_body,
            "",
        ]
    )
    target.write_text(content)
    return str(target)


def _plan_summary(plan: PlanContext) -> str:
    parts: list[str] = []
    for filename in ("SPEC.md", "IMPLEMENTATION.md", "TODO.md", "DECISIONS.md"):
        path = plan.path / filename
        if path.exists() and file_has_meaningful_content(path):
            parts.append(f"## {filename}\n\n{path.read_text().strip()}")
    if not parts:
        return "No meaningful plan content has been written yet."
    return "\n\n---\n\n".join(parts)


def _render_template(source: str, values: dict[str, str]) -> str:
    missing: list[str] = []

    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in values:
            missing.append(key)
            return match.group(0)
        return values[key]

    rendered = TEMPLATE_VAR_RE.sub(replace, source)
    if missing:
        raise SliceWorkflowError(
            "Prompt template has unknown variable(s): "
            + ", ".join(sorted(set(missing)))
        )
    return rendered


def render_phase_prompt(
    *,
    root: Path = PROJECT_ROOT,
    phase: str,
    plan_arg: str | None = None,
    task: str | None = None,
    task_text: str | None = None,
    print_prompt: bool = False,
) -> RenderResult:
    plan = _load_plan(root, plan_arg)
    task_body, task_path = _read_task_context(root, task, task_text)
    if phase == "planner" and not task_body:
        raise SliceWorkflowError(
            "slice-plan requires --task <path> or --task-text <text>."
        )

    task_snapshot = _write_task_snapshot(plan, task_body, task_path)
    template = _template_path(root, phase).read_text()
    prompt_dir = plan.path / PROMPTS_DIR_NAME
    prompt_dir.mkdir(parents=True, exist_ok=True)
    prompt_path = prompt_dir / PHASE_OUTPUT_FILES[phase]

    values = {
        "phase": phase,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "repo_root": str(root),
        "plan_path": _relative(plan.path, root),
        "plan_slug": plan.meta.slug,
        "plan_status": plan.meta.status,
        "plan_branch": plan.meta.branch,
        "task_path": task_path or "(see active plan)",
        "task_text": task_body or "(see active plan)",
        "task_snapshot_path": _relative(Path(task_snapshot), root)
        if task_snapshot
        else "",
        "plan_summary": _plan_summary(plan),
    }
    rendered = _render_template(template, values)
    previous = prompt_path.read_text() if prompt_path.exists() else ""
    changed = previous != rendered
    prompt_path.write_text(rendered)

    if print_prompt:
        print(rendered)

    return RenderResult(
        phase=phase,
        plan_path=_relative(plan.path, root),
        prompt_path=_relative(prompt_path, root),
        task_path=task_path,
        printed=print_prompt,
        changed=changed,
    )


def _artifact_count(entries: list[ArtifactEntry]) -> int:
    return len(entries)


def inspect_status(
    root: Path = PROJECT_ROOT, plan_arg: str | None = None
) -> SliceStatus:
    plan = _load_plan(root, plan_arg)
    prompts: dict[str, str] = {}
    for phase, filename in PHASE_OUTPUT_FILES.items():
        path = plan.path / PROMPTS_DIR_NAME / filename
        if path.exists():
            prompts[phase] = _relative(path, root)

    missing = [
        _relative(plan.path / rel, root)
        for rel in missing_required_plan_files(plan.path)
    ]
    artifacts = parse_artifact_manifest(plan.path / "artifacts" / "manifest.yaml")
    return SliceStatus(
        plan_path=_relative(plan.path, root),
        slug=plan.meta.slug,
        branch=plan.meta.branch,
        status=plan.meta.status,
        required_files_missing=missing,
        prompts=prompts,
        validation_has_commands=validation_has_commands(plan.path / "VALIDATION.md"),
        review_has_content=file_has_meaningful_content(plan.path / "REVIEW.md"),
        artifact_count=_artifact_count(artifacts),
    )


def _print_render_result(result: RenderResult, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(asdict(result), indent=2, sort_keys=True))
        return
    log_ok(f"Rendered {result.phase} prompt: {result.prompt_path}")
    if result.task_path:
        print(f"  Task: {result.task_path}")
    print("  Next: paste that prompt into your current agent session.")


def _print_status(status: SliceStatus, *, json_output: bool) -> None:
    if json_output:
        print(json.dumps(asdict(status), indent=2, sort_keys=True))
        return
    log_ok(f"Active slice: {status.plan_path}")
    print(f"  Slug: {status.slug}")
    print(f"  Branch: {status.branch}")
    print(f"  Status: {status.status}")
    print(f"  Validation commands: {status.validation_has_commands}")
    print(f"  Review content: {status.review_has_content}")
    print(f"  Artifacts declared: {status.artifact_count}")
    if status.prompts:
        print("  Prompts:")
        for phase, path in sorted(status.prompts.items()):
            print(f"    {phase}: {path}")
    if status.required_files_missing:
        print("  Missing required files:", file=sys.stderr)
        for path in status.required_files_missing:
            print(f"    {path}", file=sys.stderr)


def main(phase: str) -> None:
    parser = argparse.ArgumentParser(
        description=f"Render or inspect the {phase} slice workflow phase."
    )
    parser.add_argument(
        "--plan", help="Plan directory to use. Defaults to active plan."
    )
    parser.add_argument(
        "--json", action="store_true", help="Emit machine-readable JSON."
    )

    if phase == "status":
        args = parser.parse_args()
        try:
            status = inspect_status(plan_arg=args.plan)
            _print_status(status, json_output=args.json)
        except SliceWorkflowError as exc:
            log_error(str(exc))
            sys.exit(1)
        return

    parser.add_argument("--task", help="Task file to include in the rendered prompt.")
    parser.add_argument(
        "--task-text", help="Inline task text to include in the prompt."
    )
    parser.add_argument(
        "--print",
        dest="print_prompt",
        action="store_true",
        help="Also print the rendered prompt to stdout.",
    )
    args = parser.parse_args()

    try:
        if args.json and args.print_prompt:
            raise SliceWorkflowError("Use either --json or --print, not both.")
        if not args.json:
            log_step(f"Rendering {phase} prompt")
        result = render_phase_prompt(
            phase=phase,
            plan_arg=args.plan,
            task=args.task,
            task_text=args.task_text,
            print_prompt=args.print_prompt,
        )
        _print_render_result(result, json_output=args.json)
    except SliceWorkflowError as exc:
        log_error(str(exc))
        sys.exit(1)
