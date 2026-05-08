"""Target-to-profile resolution for Harness Kit user config."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.profiles.builtins import loaded_builtins
from harness_toolkit.kit.profiles.models import (
    HarnessConfig,
    LoadedProfile,
    ProfileResolution,
    TargetBinding,
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
        )

    matches: list[TargetBinding] = []
    for binding in config.targets:
        binding_path = Path(binding.path).resolve(strict=False)
        try:
            resolved_target.relative_to(binding_path)
        except ValueError:
            continue
        matches.append(binding)
    if matches:
        selected = max(matches, key=lambda binding: len(Path(binding.path).parts))
        profile = selected.profile
        reason = "target matched configured longest path prefix"
        matched_target = selected.path
        matched_name = selected.name
    else:
        profile = config.default_profile
        reason = "no configured target matched; using config default_profile"
        matched_target = None
        matched_name = None
    if profile not in resolved_catalog:
        valid = ", ".join(resolved_catalog)
        raise KeyError(f"Unknown profile '{profile}'. Valid profiles: {valid}")
    return ProfileResolution(
        profile=profile,
        source=resolved_catalog[profile].source,
        reason=reason,
        target=str(resolved_target),
        matched_target=matched_target,
        matched_name=matched_name,
        config_path=config.path,
    )
