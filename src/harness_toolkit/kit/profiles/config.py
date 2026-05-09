"""User-level Harness Kit profile config loading."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path

from harness_toolkit.kit.profiles.models import (
    HarnessConfig,
    LoadedProfile,
    ProfileError,
    TargetBinding,
)
from harness_toolkit.kit.profiles.parser import (
    _required_str,
    normalize_config_path,
    parse_profile_data,
)
from harness_toolkit.kit.profiles.validation import validate_profile_name


def default_config_path() -> Path:
    explicit = os.environ.get("HARNESS_KIT_CONFIG")
    if explicit:
        return Path(os.path.expandvars(explicit)).expanduser()
    xdg_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_home:
        return (
            Path(os.path.expandvars(xdg_home)).expanduser()
            / "harness-toolkit"
            / "harness.toml"
        )
    return Path.home() / ".config" / "harness-toolkit" / "harness.toml"


def _config_profile_dirs(data: dict[str, object], *, path: Path) -> tuple[str, ...]:
    raw_dirs: list[str] = []
    profiles_dir = data.get("profiles_dir")
    if profiles_dir is not None:
        if not isinstance(profiles_dir, str) or not profiles_dir.strip():
            raise ProfileError(
                f"harness config {path} profiles_dir must be a non-empty string"
            )
        raw_dirs.append(profiles_dir)

    profiles_dirs = data.get("profiles_dirs")
    if profiles_dirs is not None:
        if not isinstance(profiles_dirs, list):
            raise ProfileError(
                f"harness config {path} profiles_dirs must be an array of non-empty strings"
            )
        for item in profiles_dirs:
            if not isinstance(item, str) or not item.strip():
                raise ProfileError(
                    f"harness config {path} profiles_dirs must be an array of non-empty strings"
                )
            raw_dirs.append(item)

    normalized: list[str] = []
    seen: set[str] = set()
    for raw_dir in raw_dirs:
        resolved = str(normalize_config_path(raw_dir, base_dir=path.parent))
        if resolved not in seen:
            normalized.append(resolved)
            seen.add(resolved)
    return tuple(normalized)


def load_harness_config(path: Path) -> HarnessConfig | None:
    explicit = os.environ.get("HARNESS_KIT_CONFIG")
    if not path.exists():
        if explicit:
            raise ProfileError(f"harness config does not exist: {path}")
        return None
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ProfileError(f"invalid harness config TOML {path}: {e}") from e
    if not isinstance(data, dict):
        raise ProfileError(f"harness config {path} must be a TOML table")
    version = data.get("version", 1)
    if version != 1:
        raise ProfileError(f"harness config {path} has unsupported version: {version}")
    default_profile = data.get("default_profile", "generic")
    if not isinstance(default_profile, str) or not default_profile.strip():
        raise ProfileError(f"harness config {path} default_profile must be a string")
    validate_profile_name(default_profile)
    profiles_dirs = _config_profile_dirs(data, path=path)
    targets_data = data.get("targets", [])
    if not isinstance(targets_data, list):
        raise ProfileError(f"harness config {path} targets must be an array")
    targets: list[TargetBinding] = []
    base_dir = path.parent
    for index, target in enumerate(targets_data, start=1):
        if not isinstance(target, dict):
            raise ProfileError(f"harness config {path} target #{index} must be a table")
        name = _required_str(target, "name", source=f"{path} target #{index}")
        raw_path = _required_str(target, "path", source=f"{path} target #{index}")
        profile = _required_str(target, "profile", source=f"{path} target #{index}")
        validate_profile_name(profile)
        targets.append(
            TargetBinding(
                name=name,
                path=str(normalize_config_path(raw_path, base_dir=base_dir)),
                profile=profile,
            )
        )
    return HarnessConfig(
        path=str(path),
        default_profile=default_profile,
        targets=tuple(targets),
        profiles_dirs=profiles_dirs,
    )


def load_config_profiles(config_path: Path) -> dict[str, LoadedProfile]:
    try:
        data = tomllib.loads(config_path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ProfileError(f"invalid harness config TOML {config_path}: {e}") from e
    profiles_data = data.get("profiles", {})
    if profiles_data is None:
        return {}
    if not isinstance(profiles_data, dict):
        raise ProfileError(f"harness config {config_path} profiles must be a table")
    loaded: dict[str, LoadedProfile] = {}
    for name, raw_profile in profiles_data.items():
        validate_profile_name(name)
        if not isinstance(raw_profile, dict):
            raise ProfileError(f"profile {name} in {config_path} must be a table")
        profile_data = dict(raw_profile)
        profile_data["name"] = name
        profile = parse_profile_data(
            profile_data,
            source=f"{config_path} profiles.{name}",
            base_dir=config_path.parent,
        )
        loaded[name] = LoadedProfile(
            profile=profile,
            source="user-config",
            path=str(config_path),
        )
    return loaded
