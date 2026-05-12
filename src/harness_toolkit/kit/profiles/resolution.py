"""Target-to-profile resolution for Harness Kit user config."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_toolkit.kit.git.client import DEFAULT_GIT_CLIENT, GitWorktreeInfo
from harness_toolkit.kit.profiles.builtins import loaded_builtins
from harness_toolkit.kit.profiles.models import (
    HarnessConfig,
    LoadedProfile,
    ProfileResolution,
    TargetBinding,
)


@dataclass(frozen=True)
class _TargetMatch:
    binding: TargetBinding
    matched_path: Path
    projected_path: Path | None = None
    git_common_dir: Path | None = None


def _git_worktree_info(target: Path) -> GitWorktreeInfo | None:
    return DEFAULT_GIT_CLIENT.worktree_info(target)


def _direct_target_matches(
    resolved_target: Path, config: HarnessConfig
) -> list[_TargetMatch]:
    matches: list[_TargetMatch] = []
    for binding in config.targets:
        binding_path = Path(binding.path).resolve(strict=False)
        try:
            resolved_target.relative_to(binding_path)
        except ValueError:
            continue
        matches.append(_TargetMatch(binding=binding, matched_path=binding_path))
    return matches


def _worktree_target_matches(
    resolved_target: Path, config: HarnessConfig
) -> list[_TargetMatch]:
    target_info = _git_worktree_info(resolved_target)
    if target_info is None:
        return []

    matches: list[_TargetMatch] = []
    for binding in config.targets:
        binding_path = Path(binding.path).resolve(strict=False)
        binding_info = _git_worktree_info(binding_path)
        if binding_info is None:
            continue
        if binding_info.git_common_dir != target_info.git_common_dir:
            continue
        try:
            relative_binding_path = binding_path.relative_to(binding_info.repo_root)
        except ValueError:
            continue
        projected_path = (target_info.repo_root / relative_binding_path).resolve(
            strict=False
        )
        try:
            resolved_target.relative_to(projected_path)
        except ValueError:
            continue
        matches.append(
            _TargetMatch(
                binding=binding,
                matched_path=binding_path,
                projected_path=projected_path,
                git_common_dir=target_info.git_common_dir,
            )
        )
    return matches


def _select_longest_match(matches: list[_TargetMatch]) -> _TargetMatch:
    return max(
        matches,
        key=lambda match: len((match.projected_path or match.matched_path).parts),
    )


def resolve_profile(
    target: Path,
    *,
    catalog: dict[str, LoadedProfile] | None = None,
    config: HarnessConfig | None = None,
) -> ProfileResolution:
    resolved_catalog = catalog or loaded_builtins()
    resolved_target = target.resolve(strict=False)
    if config is None:
        profile = "generic"
        if profile not in resolved_catalog:
            valid = ", ".join(resolved_catalog)
            raise KeyError(f"Unknown profile '{profile}'. Valid profiles: {valid}")
        return ProfileResolution(
            profile=profile,
            source=resolved_catalog[profile].source,
            reason="no harness config target matched; using generic fallback",
            target=str(resolved_target),
            match_kind="generic-fallback",
        )

    direct_matches = _direct_target_matches(resolved_target, config)
    if direct_matches:
        selected = _select_longest_match(direct_matches)
        profile = selected.binding.profile
        reason = "target matched configured longest path prefix"
        matched_target = selected.binding.path
        matched_name = selected.binding.name
        worktree_target = None
        worktree_matched_target = None
        worktree_projected_target = None
        worktree_git_common_dir = None
        match_kind = "direct"
    else:
        worktree_matches = _worktree_target_matches(resolved_target, config)
        if worktree_matches:
            selected = _select_longest_match(worktree_matches)
            profile = selected.binding.profile
            reason = "target matched configured target through git worktree family"
            matched_target = selected.binding.path
            matched_name = selected.binding.name
            worktree_target = str(resolved_target)
            worktree_matched_target = selected.binding.path
            worktree_projected_target = (
                str(selected.projected_path) if selected.projected_path else None
            )
            worktree_git_common_dir = (
                str(selected.git_common_dir) if selected.git_common_dir else None
            )
            match_kind = "worktree"
        else:
            profile = config.default_profile
            reason = "no configured target matched; using config default_profile"
            matched_target = None
            matched_name = None
            worktree_target = None
            worktree_matched_target = None
            worktree_projected_target = None
            worktree_git_common_dir = None
            match_kind = "config-default"
    if profile not in resolved_catalog:
        valid = ", ".join(resolved_catalog)
        raise KeyError(f"Unknown profile '{profile}'. Valid profiles: {valid}")
    return ProfileResolution(
        profile=profile,
        source=resolved_catalog[profile].source,
        reason=reason,
        target=str(resolved_target),
        match_kind=match_kind,
        matched_target=matched_target,
        matched_name=matched_name,
        config_path=config.path,
        worktree_target=worktree_target,
        worktree_matched_target=worktree_matched_target,
        worktree_projected_target=worktree_projected_target,
        worktree_git_common_dir=worktree_git_common_dir,
    )
