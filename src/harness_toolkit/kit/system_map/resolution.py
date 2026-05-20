"""Resolve the active system-map source for a target repo."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.system_map.models import SystemMapLoadResult, SystemMapSource
from harness_toolkit.kit.system_map.parser import parse_system_map_file

REPO_LOCAL_SYSTEM_MAP = ".harness/system.toml"


def find_repo_local_system_map(repo_root: Path) -> Path | None:
    """Return the v1 repo-local system map path when present."""

    path = repo_root / REPO_LOCAL_SYSTEM_MAP
    return path if path.exists() else None


def resolve_system_map_source(
    repo_root: Path, *, configured_path: str | Path | None = None
) -> SystemMapSource | None:
    """Resolve the one active system-map source for a target.

    Target-level config intentionally wins over repo-local maps. This supports
    personal/user overlays for shared repos while preserving repo-local maps as
    the fallback shared source of truth.
    """

    repo_local = find_repo_local_system_map(repo_root)
    if configured_path is not None and str(configured_path).strip():
        configured = Path(configured_path).expanduser().resolve(strict=False)
        return SystemMapSource(
            path=str(configured),
            source="target-config",
            overrides=REPO_LOCAL_SYSTEM_MAP if repo_local is not None else None,
        )
    if repo_local is not None:
        return SystemMapSource(path=str(repo_local), source="repo-local")
    return None


def load_system_map_source(
    source: SystemMapSource, *, repo_root: Path
) -> SystemMapLoadResult:
    """Parse a resolved system-map source using repo-root-relative semantics."""

    result = parse_system_map_file(Path(source.path), repo_root=repo_root)
    return SystemMapLoadResult(
        path=result.path,
        map=result.map,
        findings=result.findings,
        source=source.source,
        path_base=source.path_base,
        overrides=source.overrides,
    )


def load_system_map(
    repo_root: Path, *, configured_path: str | Path | None = None
) -> SystemMapLoadResult | None:
    """Resolve and parse the active system map for ``repo_root`` if present."""

    source = resolve_system_map_source(repo_root, configured_path=configured_path)
    if source is None:
        return None
    return load_system_map_source(source, repo_root=repo_root)
