"""Changed-path applicability rules for profile checks and reviews."""

from __future__ import annotations

import shlex
from pathlib import Path

from pathspec import PathSpec

from harness_toolkit.kit.profiles.loading import get_profile
from harness_toolkit.kit.profiles.models import (
    LoadedProfile,
    ProfileCheckView,
    ProfileSuggestion,
    WorkflowProfile,
)


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


def _matches_pattern(path: str, pattern: str) -> bool:
    clean_path = _normalize_changed_path(path)
    clean_pattern = _normalize_pattern(pattern)
    if not clean_path or not clean_pattern:
        return False
    spec = PathSpec.from_lines("gitignore", [clean_pattern])
    return bool(spec.match_file(clean_path))


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
    target: Path | None = None,
    repo_root: Path | None = None,
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


def _check_suggestions(
    profile: WorkflowProfile,
    changed_paths: tuple[str, ...],
    *,
    enforce_required: bool,
    target: Path,
    repo_root: Path,
) -> tuple[ProfileSuggestion, ...]:
    suggestions: list[ProfileSuggestion] = []
    for check in profile.checks:
        record_command = (
            f"hk validate --check {shlex.quote(check.name)} "
            "--why '...' -- <native command>"
        )
        required_matches = _matched_paths(
            check.required_when, changed_paths, target=target, repo_root=repo_root
        )
        applies_matches = _matched_paths(
            check.applies_when, changed_paths, target=target, repo_root=repo_root
        )
        if required_matches:
            suggestions.append(
                ProfileSuggestion(
                    name=check.name,
                    purpose=check.purpose,
                    required=True,
                    matched_by="required_when",
                    matched_paths=required_matches,
                    enforced=enforce_required,
                    record_command=record_command,
                )
            )
        elif applies_matches:
            suggestions.append(
                ProfileSuggestion(
                    name=check.name,
                    purpose=check.purpose,
                    required=False,
                    matched_by="applies_when",
                    matched_paths=applies_matches,
                    record_command=record_command,
                )
            )
    return tuple(suggestions)


def _review_suggestions(
    profile: WorkflowProfile,
    changed_paths: tuple[str, ...],
    *,
    enforce_required: bool,
    target: Path,
    repo_root: Path,
) -> tuple[ProfileSuggestion, ...]:
    suggestions: list[ProfileSuggestion] = []
    for review in profile.reviews:
        prompt_command = (
            f"hk review prompt {shlex.quote(review.name)} "
            f"--target {shlex.quote(str(target))}"
        )
        record_command = f"hk review add --review {shlex.quote(review.name)} ..."
        required_matches = _matched_paths(
            review.required_when, changed_paths, target=target, repo_root=repo_root
        )
        applies_matches = _matched_paths(
            review.applies_when, changed_paths, target=target, repo_root=repo_root
        )
        if required_matches:
            suggestions.append(
                ProfileSuggestion(
                    name=review.name,
                    purpose=review.purpose,
                    required=True,
                    matched_by="required_when",
                    matched_paths=required_matches,
                    enforced=enforce_required,
                    record_command=record_command,
                    prompt_command=prompt_command,
                )
            )
        elif applies_matches:
            suggestions.append(
                ProfileSuggestion(
                    name=review.name,
                    purpose=review.purpose,
                    required=False,
                    matched_by="applies_when",
                    matched_paths=applies_matches,
                    record_command=record_command,
                    prompt_command=prompt_command,
                )
            )
    return tuple(suggestions)


def checks_view(
    profile_name: str,
    target: Path,
    repo_root: Path,
    catalog: dict[str, LoadedProfile] | None = None,
    changed_paths: tuple[str, ...] = (),
    enforce_required: bool = True,
) -> ProfileCheckView:
    profile = get_profile(profile_name, catalog)
    normalized_changed_paths = tuple(
        dict.fromkeys(_normalize_changed_path(path) for path in changed_paths if path)
    )
    return ProfileCheckView(
        profile=profile.name,
        target=str(target),
        repo_root=str(repo_root),
        checks=profile.checks,
        reviews=profile.reviews,
        reminder=(
            "Run validation commands directly in the agent shell loop, then record "
            "the exact command/result with `hk validate --why ... -- <command>`. "
            "Dispatch profile review guidance yourself and record accepted reviews "
            "with `hk review add ...`; HK does not run checks or reviews. "
            "When changed-path suggestions name a check or review, use the shown "
            "`hk validate --check NAME` or `hk review add --review NAME` form."
        ),
        changed_paths=normalized_changed_paths,
        suggested_checks=_check_suggestions(
            profile,
            normalized_changed_paths,
            enforce_required=enforce_required,
            target=target,
            repo_root=repo_root,
        ),
        suggested_reviews=_review_suggestions(
            profile,
            normalized_changed_paths,
            enforce_required=enforce_required,
            target=target,
            repo_root=repo_root,
        ),
    )
