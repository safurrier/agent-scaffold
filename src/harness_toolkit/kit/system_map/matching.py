"""Changed-path matching for system maps."""

from __future__ import annotations

from pathlib import Path

from pathspec import PathSpec

from harness_toolkit.kit.system_map.models import (
    LabelResolution,
    MatchedComponent,
    MatchedInvariant,
    RelevantCheckLabel,
    SystemContextView,
    SystemMap,
)
from harness_toolkit.kit.system_map.validation import check_label_findings


def _normalize_changed_path(path: str) -> str:
    clean = path.strip().replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean.strip("/")


def _normalize_pattern(pattern: str) -> str:
    clean = pattern.strip().replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean.rstrip("/") if clean != "/" else clean


def _target_prefix(target: Path | None, repo_root: Path | None) -> str:
    if target is None or repo_root is None:
        return ""
    try:
        relative = target.resolve(strict=False).relative_to(
            repo_root.resolve(strict=False)
        )
    except ValueError:
        return ""
    return _normalize_changed_path(relative.as_posix())


def _candidate_paths(clean_path: str, *, target_prefix: str = "") -> tuple[str, ...]:
    candidates = [clean_path]
    if target_prefix:
        if clean_path == target_prefix:
            target_relative = ""
        elif clean_path.startswith(f"{target_prefix}/"):
            target_relative = clean_path[len(target_prefix) + 1 :]
        else:
            target_relative = ""
        if target_relative:
            candidates.append(target_relative)
    return tuple(dict.fromkeys(candidates))


def _pattern_matches_candidates(pattern: str, candidates: tuple[str, ...]) -> bool:
    if not pattern:
        return False
    spec = PathSpec.from_lines("gitignore", [pattern])
    return any(spec.match_file(candidate) for candidate in candidates)


def _matched_paths(
    patterns: tuple[str, ...],
    changed_paths: tuple[str, ...],
    *,
    target: Path,
    repo_root: Path,
) -> tuple[str, ...]:
    clean_patterns = tuple(_normalize_pattern(pattern) for pattern in patterns)
    if not clean_patterns:
        return ()
    target_prefix = _target_prefix(target, repo_root)
    matches: list[str] = []
    for path in changed_paths:
        clean_path = _normalize_changed_path(path)
        if not clean_path:
            continue
        candidates = _candidate_paths(clean_path, target_prefix=target_prefix)
        included = False
        for pattern in clean_patterns:
            if pattern.startswith("!"):
                if _pattern_matches_candidates(pattern[1:], candidates):
                    included = False
            elif _pattern_matches_candidates(pattern, candidates):
                included = True
        if included:
            matches.append(clean_path)
    return tuple(dict.fromkeys(matches))


def _labels(
    names: tuple[str, ...], *, known: set[str] | None, required: set[str]
) -> tuple[RelevantCheckLabel, ...]:
    rows: list[RelevantCheckLabel] = []
    for name in names:
        required_by_profile: bool | None
        if known is None or name not in known:
            required_by_profile = None
        else:
            required_by_profile = name in required
        rows.append(
            RelevantCheckLabel(name=name, required_by_profile=required_by_profile)
        )
    return tuple(rows)


def system_context_for_changed_paths(
    system_map: SystemMap,
    *,
    source: str,
    changed_paths: tuple[str, ...],
    target: Path,
    repo_root: Path,
    profile_name: str | None = None,
    known_check_labels: set[str] | None = None,
    required_check_labels: set[str] | None = None,
) -> SystemContextView:
    required = required_check_labels or set()
    label_findings = check_label_findings(
        system_map, known_check_labels=known_check_labels, strict_profile=False
    )
    unresolved = tuple(
        sorted(
            finding.check_label
            for finding in label_findings
            if finding.check_label and finding.code == "unresolved-check-label"
        )
    )
    if known_check_labels is None:
        label_resolution = LabelResolution(status="skipped")
    elif unresolved:
        label_resolution = LabelResolution(
            status="unresolved",
            profile=profile_name,
            unresolved_check_labels=unresolved,
        )
    else:
        label_resolution = LabelResolution(status="resolved", profile=profile_name)

    matched_components: list[MatchedComponent] = []
    for component in system_map.components:
        matched_paths = _matched_paths(
            component.paths, changed_paths, target=target, repo_root=repo_root
        )
        if not matched_paths:
            continue
        matched_invariants = tuple(
            MatchedInvariant(
                id=invariant.id,
                qualified_id=f"{component.id}.{invariant.id}",
                statement=invariant.statement,
                relevant_check_labels=_labels(
                    invariant.validation_checks,
                    known=known_check_labels,
                    required=required,
                ),
            )
            for invariant in component.invariants
        )
        matched_components.append(
            MatchedComponent(
                id=component.id,
                title=component.title,
                kind=component.kind,
                matched_paths=matched_paths,
                read_before_editing=component.read_before_editing,
                relevant_check_labels=_labels(
                    component.validation_checks,
                    known=known_check_labels,
                    required=required,
                ),
                invariants=matched_invariants,
            )
        )

    return SystemContextView(
        advisory=True,
        source=source,
        label_resolution=label_resolution,
        matched_components=tuple(matched_components),
        warnings=tuple(f for f in label_findings if f.severity == "warning"),
    )
