"""Shared helpers for plan/spec/evidence/review contract checks.

These helpers intentionally avoid external dependencies so they can ship into
generated repos alongside the existing file-based mise tasks.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path

PROJECT_ROOT = Path(os.environ.get("MISE_PROJECT_ROOT", "."))
CHECKLIST_PREFIX = re.compile(r"^\[[ xX]\]\s+")
COMMAND_PATTERN = re.compile(
    r"\bmise\s+(?:-[\w-]+\s+)*run\b|\bcargo (?:fmt|check|test|clippy|run|build)\b|"
    r"\buv run\b|\bgo test\b|\bpytest\b|\bdocker\b"
)

PLAN_REQUIRED_FILES = (
    Path("META.yaml"),
    Path("TODO.md"),
    Path("LEARNING_LOG.md"),
    Path("VALIDATION.md"),
    Path("REVIEW.md"),
    Path("DECISIONS.md"),
    Path("artifacts") / "manifest.yaml",
)
PLAN_ACTIVE_STATUSES = {"planned", "in-progress"}
ALLOWED_META_STATUSES = {"planned", "in-progress", "complete", "abandoned"}
ALLOWED_CONTRACT_CHANGES = {"implementation_only", "docs_only", "contract_changed"}
ALLOWED_DECISION_RECORDS = {"none", "ledger", "adr"}
ALLOWED_REVIEW_MODES = {"external_required"}
PLACEHOLDER_VALUES = {
    "",
    "-",
    "todo",
    "tbd",
    "pending",
    "pending review",
    "pending review.",
    "pending sync",
    "pending sync.",
    "pending implementation",
    "fill me in",
    "replace this placeholder with the actual slice tasks",
    "add artifact paths to artifacts/manifest.yaml as they are produced",
}
NON_SLICE_BOOTSTRAP_PATHS = {
    "uv.lock",
    "go.sum",
    "Cargo.lock",
    "test-results",
    "test-results/",
}


@dataclass
class PlanMeta:
    slug: str = ""
    branch: str = ""
    created: str = ""
    pr: str = ""
    status: str = ""
    source: str = ""
    contract_change: str = ""
    decision_record: str = ""
    review_mode: str = ""
    review_backend: str = ""
    review_rubrics: list[str] = field(default_factory=list)
    evidence_required: list[str] = field(default_factory=list)
    continues_from: str = ""
    supersedes: str = ""


@dataclass
class PlanContext:
    path: Path
    meta: PlanMeta


@dataclass
class MarkdownSection:
    heading: str
    level: int
    content: str


@dataclass
class ArtifactEntry:
    type: str = ""
    path: str = ""
    note: str = ""


class PlanContractError(RuntimeError):
    """Expected plan-contract failure that should be shown without a traceback."""


def strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + 5 :]


def parse_meta_yaml(path: Path) -> PlanMeta | None:
    if not path.exists():
        return None

    meta = PlanMeta()
    list_fields = {"review_rubrics", "evidence_required"}
    current_list_key: str | None = None

    for raw_line in path.read_text().splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if current_list_key and raw_line.startswith("  - "):
            getattr(meta, current_list_key).append(raw_line[4:].strip())
            continue

        if not raw_line.startswith(" "):
            current_list_key = None
            match = re.match(r"^([a-z_]+):\s*(.*)$", line)
            if not match:
                continue
            key, value = match.group(1), match.group(2).strip()
            if key in list_fields:
                current_list_key = key
                setattr(meta, key, [])
            elif hasattr(meta, key):
                setattr(meta, key, value)

    return meta


def validate_meta_yaml(meta: PlanMeta) -> list[str]:
    errors: list[str] = []

    if not meta.slug:
        errors.append("missing 'slug' field")
    if not meta.created:
        errors.append("missing 'created' field")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", meta.created):
        errors.append(f"created '{meta.created}' is not YYYY-MM-DD format")

    if not meta.status:
        errors.append("missing 'status' field")
    elif meta.status not in ALLOWED_META_STATUSES:
        errors.append(
            f"status '{meta.status}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_META_STATUSES))}"
        )

    if not meta.contract_change:
        errors.append("missing 'contract_change' field")
    elif meta.contract_change not in ALLOWED_CONTRACT_CHANGES:
        errors.append(
            f"contract_change '{meta.contract_change}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_CONTRACT_CHANGES))}"
        )

    if not meta.decision_record:
        errors.append("missing 'decision_record' field")
    elif meta.decision_record not in ALLOWED_DECISION_RECORDS:
        errors.append(
            f"decision_record '{meta.decision_record}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_DECISION_RECORDS))}"
        )

    if not meta.review_mode:
        errors.append("missing 'review_mode' field")
    elif meta.review_mode not in ALLOWED_REVIEW_MODES:
        errors.append(
            f"review_mode '{meta.review_mode}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_REVIEW_MODES))}"
        )

    if not meta.review_rubrics:
        errors.append("missing or empty 'review_rubrics' field")
    if not meta.evidence_required:
        errors.append("missing or empty 'evidence_required' field")

    return errors


def list_plan_contexts(root: Path = PROJECT_ROOT) -> list[PlanContext]:
    plans_root = root / ".ai" / "plans"
    if not plans_root.exists():
        return []
    contexts: list[PlanContext] = []
    for path in sorted(plans_root.iterdir()):
        if not path.is_dir() or not re.match(r"^\d{4}-\d{2}-\d{2}-\d{6}-", path.name):
            continue
        meta = parse_meta_yaml(path / "META.yaml")
        if meta is None:
            continue
        contexts.append(PlanContext(path=path, meta=meta))
    return contexts


def current_plan_context(root: Path = PROJECT_ROOT) -> PlanContext | None:
    contexts = list_plan_contexts(root)
    in_progress = [ctx for ctx in contexts if ctx.meta.status == "in-progress"]
    if len(in_progress) == 1:
        return in_progress[0]
    planned = [ctx for ctx in contexts if ctx.meta.status == "planned"]
    if planned:
        return planned[-1]
    return None


def in_progress_plan_contexts(root: Path = PROJECT_ROOT) -> list[PlanContext]:
    return [ctx for ctx in list_plan_contexts(root) if ctx.meta.status == "in-progress"]


def missing_required_plan_files(plan_dir: Path) -> list[Path]:
    return [rel for rel in PLAN_REQUIRED_FILES if not (plan_dir / rel).exists()]


def git_current_branch(root: Path = PROJECT_ROOT) -> str:
    git_bin = shutil.which("git")
    if git_bin is None:
        return ""
    result = subprocess.run(  # noqa: S603
        [git_bin, "symbolic-ref", "--quiet", "--short", "HEAD"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def git_changed_paths(root: Path = PROJECT_ROOT) -> list[str]:
    git_bin = shutil.which("git")
    if git_bin is None:
        raise PlanContractError(
            "git executable not found; cannot inspect changed paths."
        )
    result = subprocess.run(  # noqa: S603
        [git_bin, "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise PlanContractError(
            f"git status failed; cannot inspect changed paths: {message}"
        )

    paths: list[str] = []
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        entry = line[3:].strip()
        if " -> " in entry:
            entry = entry.split(" -> ", 1)[1]
        paths.append(entry)
    return paths


def strip_plan_local_changes(paths: list[str], plan_dir: Path | None) -> list[str]:
    def _is_ignored(path: str) -> bool:
        if path in NON_SLICE_BOOTSTRAP_PATHS:
            return True
        if (
            "__pycache__/" in path
            or path.endswith("/__pycache__")
            or path.endswith(".pyc")
        ):
            return True
        return False

    if plan_dir is None:
        return [path for path in paths if not _is_ignored(path)]
    prefix = str(plan_dir.relative_to(PROJECT_ROOT))
    return [
        path
        for path in paths
        if not _is_ignored(path)
        and path != prefix
        and not path.startswith(f"{prefix}/")
    ]


def parse_sections(path: Path) -> list[MarkdownSection]:
    text = strip_frontmatter(path.read_text()) if path.exists() else ""
    sections: list[MarkdownSection] = []
    matches = list(re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE))
    if not matches:
        return sections

    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections.append(
            MarkdownSection(
                heading=match.group(2).strip(),
                level=len(match.group(1)),
                content=text[start:end].strip(),
            )
        )
    return sections


def find_section(path: Path, heading: str, *, level: int = 2) -> MarkdownSection | None:
    target = heading.lower()
    for section in parse_sections(path):
        if section.level == level and section.heading.lower() == target:
            return section
    return None


def normalize_value(value: str) -> str:
    return value.strip().strip("`").strip()


def strip_checklist_prefix(value: str) -> str:
    return CHECKLIST_PREFIX.sub("", value, count=1).strip()


def checklist_has_meaningful_items(path: Path) -> bool:
    if not path.exists():
        return False

    for raw_line in strip_frontmatter(path.read_text()).splitlines():
        stripped = raw_line.strip()
        match = re.match(r"^- \[[ xX]\]\s+(.+)$", stripped)
        if not match:
            continue
        item = normalize_value(match.group(1))
        if not is_placeholder_value(item):
            return True
    return False


def is_placeholder_value(value: str) -> bool:
    normalized = normalize_value(value).lower()
    return normalized in PLACEHOLDER_VALUES


def file_has_meaningful_content(path: Path) -> bool:
    if not path.exists():
        return False

    for raw_line in strip_frontmatter(path.read_text()).splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#") or stripped.startswith("<!--"):
            continue
        if stripped.startswith("- "):
            bullet = normalize_value(stripped[2:])
            if is_placeholder_value(bullet) or is_placeholder_value(
                strip_checklist_prefix(bullet)
            ):
                continue
            return True
        if not is_placeholder_value(stripped):
            return True
    return False


def section_bullets(path: Path, heading: str) -> list[str]:
    section = find_section(path, heading)
    if section is None:
        return []
    bullets: list[str] = []
    for line in section.content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            bullets.append(normalize_value(stripped[2:]))
    return bullets


def section_has_meaningful_bullets(path: Path, heading: str) -> bool:
    return any(
        not is_placeholder_value(value) for value in section_bullets(path, heading)
    )


def keyed_bullets(path: Path, heading: str) -> dict[str, str]:
    section = find_section(path, heading)
    if section is None:
        return {}
    values: dict[str, str] = {}
    for line in section.content.splitlines():
        stripped = line.strip()
        match = re.match(r"^-\s+([^:]+):\s*(.+)$", stripped)
        if match:
            values[match.group(1).strip().lower()] = normalize_value(match.group(2))
    return values


def extract_paths_from_bullets(path: Path, heading: str) -> list[str]:
    values = section_bullets(path, heading)
    extracted: list[str] = []
    for value in values:
        inline = re.findall(r"`([^`]+)`", value)
        if inline:
            extracted.extend(inline)
            continue
        candidate = re.split(r"\s+[—-]\s+", value, maxsplit=1)[0].strip()
        if candidate:
            extracted.append(candidate)
    return extracted


def parse_artifact_manifest(path: Path) -> list[ArtifactEntry]:
    if not path.exists():
        return []

    entries: list[ArtifactEntry] = []
    current: dict[str, str] | None = None
    in_artifacts = False

    for raw_line in path.read_text().splitlines():
        if not raw_line.strip() or raw_line.strip().startswith("#"):
            continue
        if raw_line.strip() == "artifacts:":
            in_artifacts = True
            continue
        if not in_artifacts:
            continue

        if raw_line.startswith("  - "):
            if current is not None:
                entries.append(
                    ArtifactEntry(
                        type=current.get("type", ""),
                        path=current.get("path", ""),
                        note=current.get("note", ""),
                    )
                )
            current = {}
            key_value = raw_line[4:].strip()
            if ":" in key_value:
                key, value = key_value.split(":", 1)
                current[key.strip()] = value.strip()
            continue

        if current is not None and raw_line.startswith("    ") and ":" in raw_line:
            key, value = raw_line.strip().split(":", 1)
            current[key.strip()] = value.strip()

    if current is not None:
        entries.append(
            ArtifactEntry(
                type=current.get("type", ""),
                path=current.get("path", ""),
                note=current.get("note", ""),
            )
        )

    return entries


def validation_has_commands(path: Path) -> bool:
    if not path.exists():
        return False
    text = strip_frontmatter(path.read_text())

    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        inline = re.findall(r"`([^`]+)`", stripped)
        if any(COMMAND_PATTERN.search(candidate) for candidate in inline):
            return True

    for block in re.findall(r"```[a-zA-Z0-9_-]*\n(.*?)```", text, flags=re.DOTALL):
        for raw_line in block.splitlines():
            stripped = raw_line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("$ "):
                stripped = stripped[2:].strip()
            if COMMAND_PATTERN.search(stripped):
                return True
    return False


def plan_reference_present(path: Path, plan_id: str, slug: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text()
    return plan_id in text or slug in text or f".ai/plans/{plan_id}" in text


def resolve_plan_artifact_path(plan_dir: Path, artifact_path: str) -> Path | None:
    candidate = (plan_dir / artifact_path).resolve()
    plan_root = plan_dir.resolve()
    if candidate == plan_root or plan_root in candidate.parents:
        return candidate
    return None


def resolve_repo_path(root: Path, raw_path: str) -> Path | None:
    candidate = (root / raw_path).resolve()
    repo_root = root.resolve()
    if candidate == repo_root or repo_root in candidate.parents:
        return candidate
    return None


def ledger_path(root: Path = PROJECT_ROOT) -> Path:
    generated = root / "docs" / "explanation" / "decision-ledger.md"
    legacy = root / "docs" / "decision-ledger.md"

    if generated.exists():
        return generated
    if legacy.exists():
        return legacy
    return generated


def adr_dir(root: Path = PROJECT_ROOT) -> Path:
    generated = root / "docs" / "explanation" / "decisions"
    legacy = root / "docs" / "decisions"

    if generated.exists():
        return generated
    if legacy.exists():
        return legacy
    return generated
