"""Profile catalog loading and lookup helpers."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.kit.profiles.builtins import loaded_builtins
from harness_toolkit.kit.profiles.config import (
    default_config_path,
    load_config_profiles,
    load_harness_config,
)
from harness_toolkit.kit.profiles.models import (
    HarnessConfig,
    LoadedProfile,
    ProfileError,
    ProfileName,
    WorkflowProfile,
)
from harness_toolkit.kit.profiles.parser import load_profile_file


def load_profile_catalog(
    profiles_dir: Path | None = None,
) -> tuple[dict[str, LoadedProfile], HarnessConfig | None]:
    catalog = loaded_builtins()
    config = load_harness_config(default_config_path())
    if config is not None:
        catalog.update(load_config_profiles(Path(config.path)))

    if profiles_dir is not None:
        if not profiles_dir.exists():
            raise ProfileError(f"profiles directory does not exist: {profiles_dir}")
        if not profiles_dir.is_dir():
            raise ProfileError(f"profiles path is not a directory: {profiles_dir}")

        for path in sorted(profiles_dir.glob("*.toml")):
            loaded = load_profile_file(path)
            catalog[loaded.profile.name] = loaded
    return catalog, config


def profile_names(
    catalog: dict[str, LoadedProfile] | None = None,
) -> tuple[ProfileName, ...]:
    resolved_catalog = catalog or load_profile_catalog()[0]
    return tuple(resolved_catalog.keys())


def get_loaded_profile(
    name: str, catalog: dict[str, LoadedProfile] | None = None
) -> LoadedProfile:
    resolved_catalog = catalog or load_profile_catalog()[0]
    if name not in resolved_catalog:
        valid = ", ".join(resolved_catalog)
        raise KeyError(f"Unknown profile '{name}'. Valid profiles: {valid}")
    return resolved_catalog[name]


def get_profile(
    name: str, catalog: dict[str, LoadedProfile] | None = None
) -> WorkflowProfile:
    return get_loaded_profile(name, catalog).profile
