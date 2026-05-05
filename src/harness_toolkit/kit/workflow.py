"""Portable agent workflow overlay for existing repositories.

This module is intentionally separate from scaffold init. It lets a user attach
Harness Kit's slice planning workflow to an arbitrary target repository without
committing scaffold files into that repository.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from harness_toolkit.scaffold.config import SCAFFOLD_ROOT

SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
PLAN_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-")
ROOT_SCOPE = "root"
WORKFLOW_DIRNAME = "harness-kit"
LOCAL_OVERLAY_DIR = ".ai-local"
EXCLUDE_MARKER_START = "# harness-kit portable workflow"
EXCLUDE_MARKER_END = "# /harness-kit portable workflow"
PLAN_REQUIRED_FILES = (
    Path("META.yaml"),
    Path("TODO.md"),
    Path("LEARNING_LOG.md"),
    Path("VALIDATION.md"),
    Path("REVIEW.md"),
    Path("DECISIONS.md"),
    Path("artifacts") / "manifest.yaml",
)
PLACEHOLDER_VALUES = {
    "",
    "todo",
    "tbd",
    "pending",
    "pending sync.",
    "pending review.",
    "replace this placeholder with the actual slice tasks",
    "add artifact paths to `artifacts/manifest.yaml` as they are produced",
    "backend: pending",
    "core-quality",
    "mode: external",
    "reviewer: pending",
}
COMMAND_PATTERN = re.compile(
    r"\bmise\s+(?:-[\w-]+\s+)*run\b|\buv run\b|\bpytest\b|\bgo test\b|"
    r"\bcargo (?:fmt|check|test|clippy|run|build)\b|\bdocker\b|\bgit\s+status\b"
)


# Public facade for portable workflow state. If this grows new state backends or
# validation modes, split internals into store/plan/check modules while keeping
# this facade stable.
class WorkflowError(RuntimeError):
    """Expected portable workflow failure shown without a traceback."""


@dataclass(frozen=True)
class WorkflowState:
    target_root: Path
    target_scope: Path
    state_dir: Path
    mode: str
    scope: str
    repo_key: str


@dataclass(frozen=True)
class AttachResult:
    target_root: str
    target_scope: str
    state_dir: str
    mode: str
    scope: str
    ignored_by_local_git: bool


@dataclass(frozen=True)
class PlanResult:
    slug: str
    plan_dir: str
    state_dir: str


@dataclass(frozen=True)
class WorkflowStatus:
    target_root: str
    target_scope: str
    state_dir: str
    mode: str
    scope: str
    active_plan: str
    active_slug: str
    active_status: str
    missing_files: list[str]
    validation_has_commands: bool
    review_has_content: bool


@dataclass(frozen=True)
class SyncResult:
    plan_dir: str
    checks: list[str]


def git_root(path: Path) -> Path:
    if not path.exists():
        raise WorkflowError(f"target does not exist: {path}")
    if not path.is_dir():
        raise WorkflowError(f"target is not a directory: {path}")
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return path.resolve()
    return Path(result.stdout.strip()).resolve()


def git_branch(path: Path) -> str:
    result = subprocess.run(
        ["git", "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def git_remote(path: Path) -> str:
    result = subprocess.run(
        ["git", "config", "--get", "remote.origin.url"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def default_workflow_home() -> Path:
    configured = os.environ.get("HARNESS_KIT_WORKFLOW_HOME") or os.environ.get(
        "AGENT_SCAFFOLD_WORKFLOW_HOME"
    )
    if configured:
        return Path(configured).expanduser().resolve()
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "harness-toolkit" / "workflows"


def repo_key(target_root: Path) -> str:
    identity = git_remote(target_root) or str(target_root.resolve())
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
    safe_name = re.sub(
        r"[^a-zA-Z0-9_.-]+", "-", Path(identity).stem or target_root.name
    )
    return f"{safe_name}-{digest}"


def scope_key(target_root: Path, target_scope: Path) -> str:
    try:
        relative = target_scope.resolve().relative_to(target_root.resolve())
    except ValueError:
        return ROOT_SCOPE
    if str(relative) == ".":
        return ROOT_SCOPE
    raw = str(relative).strip().strip("/")
    if not raw:
        return ROOT_SCOPE
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw)


def resolve_state(
    target: Path,
    *,
    mode: str,
    state_root: Path | None,
) -> WorkflowState:
    target_scope = target.resolve()
    target_root = git_root(target_scope)
    scope = scope_key(target_root, target_scope)
    key = repo_key(target_root)
    if mode == "external":
        base = (
            state_root.expanduser().resolve() if state_root else default_workflow_home()
        )
        state_dir = base / key / scope
    elif mode == "overlay":
        state_dir = target_root / LOCAL_OVERLAY_DIR / WORKFLOW_DIRNAME / scope
    else:
        raise WorkflowError("mode must be 'external' or 'overlay'")
    return WorkflowState(
        target_root=target_root,
        target_scope=target_scope,
        state_dir=state_dir.resolve(),
        mode=mode,
        scope=scope,
        repo_key=key,
    )


def write_metadata(state: WorkflowState) -> None:
    metadata = {
        "target_root": str(state.target_root),
        "target_scope": str(state.target_scope),
        "state_dir": str(state.state_dir),
        "mode": state.mode,
        "scope": state.scope,
        "repo_key": state.repo_key,
        "created_or_updated": datetime.now().isoformat(timespec="seconds"),
    }
    (state.state_dir / "workflow.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )


def copy_workflow_templates(state: WorkflowState) -> None:
    plans_src = SCAFFOLD_ROOT / "templates" / ".ai" / "plans"
    skills_src = SCAFFOLD_ROOT / "templates" / ".agent" / "skills" / "slice-workflow"
    plans_dst = state.state_dir / ".ai" / "plans"
    skill_dst = state.state_dir / ".agent" / "skills" / "slice-workflow"
    if not plans_src.is_dir():
        raise WorkflowError(f"Plan templates not found: {plans_src}")
    if not skills_src.is_dir():
        raise WorkflowError(f"slice-workflow skill template not found: {skills_src}")
    shutil.copytree(plans_src, plans_dst, dirs_exist_ok=True)
    shutil.copytree(
        skills_src,
        skill_dst,
        ignore=shutil.ignore_patterns("cli", ".venv", "__pycache__"),
        dirs_exist_ok=True,
    )


def git_exclude_file(path: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return None
    raw_path = Path(result.stdout.strip())
    if raw_path.is_absolute():
        return raw_path
    return path / raw_path


def add_overlay_exclude(state: WorkflowState) -> bool:
    exclude = git_exclude_file(state.target_root)
    if exclude is None:
        return False
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text() if exclude.exists() else ""
    pattern = f"/{LOCAL_OVERLAY_DIR}/{WORKFLOW_DIRNAME}/"
    block = f"{EXCLUDE_MARKER_START}\n{pattern}\n{EXCLUDE_MARKER_END}\n"
    if pattern in existing:
        return True
    separator = "" if not existing or existing.endswith("\n") else "\n"
    exclude.write_text(existing + separator + block)
    return True


def preview_attach(
    target: Path,
    *,
    mode: str,
    state_root: Path | None = None,
) -> AttachResult:
    state = resolve_state(target, mode=mode, state_root=state_root)
    return AttachResult(
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        state_dir=str(state.state_dir),
        mode=state.mode,
        scope=state.scope,
        ignored_by_local_git=mode == "overlay"
        and git_exclude_file(state.target_root) is not None,
    )


def attach_workflow(
    target: Path,
    *,
    mode: str,
    state_root: Path | None = None,
) -> AttachResult:
    state = resolve_state(target, mode=mode, state_root=state_root)
    state.state_dir.mkdir(parents=True, exist_ok=True)
    copy_workflow_templates(state)
    write_metadata(state)
    ignored = add_overlay_exclude(state) if mode == "overlay" else False
    return AttachResult(
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        state_dir=str(state.state_dir),
        mode=state.mode,
        scope=state.scope,
        ignored_by_local_git=ignored,
    )


def ensure_attached(
    target: Path,
    *,
    mode: str,
    state_root: Path | None = None,
) -> WorkflowState:
    state = resolve_state(target, mode=mode, state_root=state_root)
    if not (state.state_dir / ".ai" / "plans" / "_templates").is_dir():
        attach_workflow(target, mode=mode, state_root=state_root)
    return state


def validate_slug(raw_slug: str) -> str:
    slug = raw_slug.strip()
    if not SLUG_RE.fullmatch(slug):
        raise WorkflowError(
            "Invalid slug: use lowercase letters, digits, and single hyphens"
        )
    return slug


def plan_templates_dir(state: WorkflowState) -> Path:
    templates = state.state_dir / ".ai" / "plans" / "_templates"
    missing = [
        str(path) for path in PLAN_REQUIRED_FILES if not (templates / path).exists()
    ]
    if missing:
        raise WorkflowError("Plan templates are incomplete: " + ", ".join(missing))
    return templates


def existing_plan(state: WorkflowState, slug: str) -> Path | None:
    plans_root = state.state_dir / ".ai" / "plans"
    if not plans_root.is_dir():
        return None
    for path in sorted(plans_root.iterdir()):
        if not path.is_dir() or not PLAN_DIR_RE.match(path.name):
            continue
        plan_slug = PLAN_DIR_RE.sub("", path.name, count=1)
        if plan_slug == slug:
            return path
    return None


def create_plan(
    target: Path,
    slug_arg: str,
    *,
    mode: str,
    state_root: Path | None = None,
) -> PlanResult:
    slug = validate_slug(slug_arg)
    state = ensure_attached(target, mode=mode, state_root=state_root)
    duplicate = existing_plan(state, slug)
    if duplicate is not None:
        raise WorkflowError(f"A plan for '{slug}' already exists: {duplicate}")
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    plan_dir = state.state_dir / ".ai" / "plans" / f"{timestamp}-{slug}"
    templates = plan_templates_dir(state)
    branch = git_branch(state.target_root)
    created = datetime.now().strftime("%Y-%m-%d")
    for src in sorted(templates.rglob("*")):
        if src.is_dir():
            continue
        dst = plan_dir / src.relative_to(templates)
        dst.parent.mkdir(parents=True, exist_ok=True)
        content = src.read_text()
        content = content.replace("{{slug}}", slug)
        content = content.replace("{{branch}}", branch)
        content = content.replace("{{created}}", created)
        dst.write_text(content)
    return PlanResult(slug=slug, plan_dir=str(plan_dir), state_dir=str(state.state_dir))


def parse_meta(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text().splitlines():
        if not raw_line or raw_line.startswith(" ") or raw_line.startswith("#"):
            continue
        if ":" not in raw_line:
            continue
        key, value = raw_line.split(":", 1)
        values[key.strip()] = value.strip()
    return values


def list_plans(state: WorkflowState) -> list[Path]:
    plans_root = state.state_dir / ".ai" / "plans"
    if not plans_root.is_dir():
        return []
    return [
        path
        for path in sorted(plans_root.iterdir())
        if path.is_dir() and PLAN_DIR_RE.match(path.name)
    ]


def active_plan(state: WorkflowState) -> Path | None:
    plans = list_plans(state)
    in_progress = [
        path
        for path in plans
        if parse_meta(path / "META.yaml").get("status") == "in-progress"
    ]
    if in_progress:
        return in_progress[-1]
    planned = [
        path
        for path in plans
        if parse_meta(path / "META.yaml").get("status") == "planned"
    ]
    if planned:
        return planned[-1]
    return plans[-1] if plans else None


def lines_without_frontmatter(text: str) -> list[str]:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for index, line in enumerate(lines[1:], start=1):
            if line.strip() == "---":
                return lines[index + 1 :]
    return lines


def is_meaningful_text(path: Path) -> bool:
    if not path.exists():
        return False
    for raw_line in lines_without_frontmatter(path.read_text()):
        line = raw_line.strip().lower()
        if not line or line.startswith("#") or line in PLACEHOLDER_VALUES:
            continue
        if line.startswith("-") and any(
            value and value in line for value in PLACEHOLDER_VALUES
        ):
            continue
        return True
    return False


def validation_has_commands(path: Path) -> bool:
    if not path.exists():
        return False
    in_fence = False
    for raw_line in lines_without_frontmatter(path.read_text()):
        line = raw_line.strip()
        if line.startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence and COMMAND_PATTERN.search(line):
            return True
        if line.startswith(("- `", "* `")) and COMMAND_PATTERN.search(line):
            return True
    return False


def workflow_status(
    target: Path,
    *,
    mode: str,
    state_root: Path | None = None,
) -> WorkflowStatus:
    state = ensure_attached(target, mode=mode, state_root=state_root)
    plan = active_plan(state)
    if plan is None:
        return WorkflowStatus(
            target_root=str(state.target_root),
            target_scope=str(state.target_scope),
            state_dir=str(state.state_dir),
            mode=state.mode,
            scope=state.scope,
            active_plan="",
            active_slug="",
            active_status="",
            missing_files=[],
            validation_has_commands=False,
            review_has_content=False,
        )
    meta = parse_meta(plan / "META.yaml")
    missing = [str(path) for path in PLAN_REQUIRED_FILES if not (plan / path).exists()]
    return WorkflowStatus(
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        state_dir=str(state.state_dir),
        mode=state.mode,
        scope=state.scope,
        active_plan=str(plan),
        active_slug=meta.get("slug", ""),
        active_status=meta.get("status", ""),
        missing_files=missing,
        validation_has_commands=validation_has_commands(plan / "VALIDATION.md"),
        review_has_content=is_meaningful_text(plan / "REVIEW.md"),
    )


def sync_check(
    target: Path,
    *,
    mode: str,
    state_root: Path | None = None,
) -> SyncResult:
    state = ensure_attached(target, mode=mode, state_root=state_root)
    plan = active_plan(state)
    if plan is None:
        raise WorkflowError(
            "No legacy plan found. Run `hk legacy plan <slug> --target <repo>` first."
        )
    missing = [str(path) for path in PLAN_REQUIRED_FILES if not (plan / path).exists()]
    if missing:
        raise WorkflowError(
            "Active plan is missing required files: " + ", ".join(missing)
        )
    meta = parse_meta(plan / "META.yaml")
    if not meta.get("slug") or not meta.get("created") or not meta.get("status"):
        raise WorkflowError("META.yaml must include slug, created, and status")
    if not is_meaningful_text(plan / "TODO.md"):
        raise WorkflowError("TODO.md must contain meaningful checklist items")
    if not is_meaningful_text(plan / "DECISIONS.md"):
        raise WorkflowError("DECISIONS.md must contain a meaningful change summary")
    if not validation_has_commands(plan / "VALIDATION.md"):
        raise WorkflowError("VALIDATION.md must contain real validation commands")
    review_required = meta.get("review_mode") == "external_required"
    review_ready = is_meaningful_text(plan / "REVIEW.md")
    if review_required and not review_ready:
        raise WorkflowError("REVIEW.md must contain external review notes")
    checks = ["plan", "decisions", "validation"]
    if review_ready:
        checks.append("review")
    return SyncResult(plan_dir=str(plan), checks=checks)


def to_jsonable(value: AttachResult | PlanResult | WorkflowStatus | SyncResult) -> str:
    return json.dumps(asdict(value), indent=2, sort_keys=True)
