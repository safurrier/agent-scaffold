"""Serialization helpers for system maps."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.system_map.models import (
    SystemMapLoadResult,
    SystemMapStatus,
    SystemMapSummary,
)


def _display_path(result: SystemMapLoadResult, repo_root: Path) -> str:
    if result.source == "target-config":
        return result.path
    try:
        return Path(result.path).resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return result.path


def summary_from_load_result(
    result: SystemMapLoadResult, *, repo_root: Path
) -> SystemMapSummary:
    errors = sum(1 for finding in result.findings if finding.severity == "error")
    warnings = sum(1 for finding in result.findings if finding.severity == "warning")
    status: SystemMapStatus = "invalid" if errors else "valid"
    return SystemMapSummary(
        path=_display_path(result, repo_root),
        version=result.map.version if result.map and result.ok else None,
        status=status,
        components=len(result.map.components) if result.map and result.ok else 0,
        invariants=result.map.invariant_count if result.map and result.ok else 0,
        warnings_count=warnings,
        errors_count=errors,
        source=result.source,
        path_base=result.path_base,
        overrides=result.overrides,
        label_resolution="skipped",
    )
