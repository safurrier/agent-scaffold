"""Validation helpers for system maps."""

from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec

from harness_toolkit.kit.system_map.models import SystemMap, SystemMapFinding


def is_glob(ref: str) -> bool:
    return any(ch in ref for ch in "*?[")


def path_exists_or_glob(repo_root: Path, ref: str) -> bool:
    if ref.startswith(("http://", "https://")):
        return True
    path = Path(ref)
    if path.is_absolute():
        return path.exists()
    if is_glob(ref):
        spec = PathSpec.from_lines("gitignore", [ref.replace("\\", "/")])
        return any(
            spec.match_file(candidate.as_posix())
            for candidate in _repo_files(repo_root)
        )
    return (repo_root / path).exists()


def _repo_files(repo_root: Path) -> tuple[Path, ...]:
    ignored = {
        ".git",
        ".venv",
        ".harness-local",
        "target",
        "node_modules",
        "__pycache__",
    }
    files: list[Path] = []
    for candidate in repo_root.rglob("*"):
        try:
            rel = candidate.relative_to(repo_root)
        except ValueError:
            continue
        if any(part in ignored for part in rel.parts):
            continue
        files.append(rel)
    return tuple(files)


def referenced_check_labels(system_map: SystemMap) -> tuple[str, ...]:
    labels: list[str] = []
    for component in system_map.components:
        labels.extend(component.validation_checks)
        for invariant in component.invariants:
            labels.extend(invariant.validation_checks)
    return tuple(dict.fromkeys(labels))


def check_label_findings(
    system_map: SystemMap,
    *,
    known_check_labels: set[str] | None,
    strict_profile: bool = False,
) -> tuple[SystemMapFinding, ...]:
    if known_check_labels is None:
        return ()
    findings: list[SystemMapFinding] = []
    for label in referenced_check_labels(system_map):
        if label not in known_check_labels:
            findings.append(
                SystemMapFinding(
                    code="unresolved-check-label",
                    severity="error" if strict_profile else "warning",
                    message=f"validation check label does not exist in profile: {label}",
                    check_label=label,
                )
            )
    return tuple(findings)
