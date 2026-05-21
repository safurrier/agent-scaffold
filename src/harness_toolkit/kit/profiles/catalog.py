"""Profile catalog facade used by CLI and lifecycle code."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_toolkit.kit.profiles.applicability import checks_view
from harness_toolkit.kit.profiles.loading import (
    get_loaded_profile,
    load_profile_catalog,
)
from harness_toolkit.kit.profiles.models import (
    HarnessConfig,
    LoadedProfile,
    ProfileCheckView,
    ProfileName,
    ProfileResolution,
    WorkflowProfile,
)
from harness_toolkit.kit.profiles.resolution import (
    resolve_profile,
    resolve_target_system_map,
)
from harness_toolkit.kit.profiles.serialization import profile_to_json, profiles_to_json
from harness_toolkit.kit.profiles.templates import profile_template


@dataclass(frozen=True)
class ProfileCatalog:
    """Loaded profile catalog with lookup, views, and template generation."""

    profiles: dict[str, LoadedProfile]
    config: HarnessConfig | None = None

    @classmethod
    def load(cls, profiles_dir: Path | None = None) -> ProfileCatalog:
        profiles, config = load_profile_catalog(profiles_dir)
        return cls(profiles, config)

    def names(self) -> tuple[ProfileName, ...]:
        return tuple(self.profiles)

    def loaded(self, name: str) -> LoadedProfile:
        return get_loaded_profile(name, self.profiles)

    def get(self, name: str) -> WorkflowProfile:
        return self.loaded(name).profile

    def list_json(
        self, *, target: Path | None = None, repo_root: Path | None = None
    ) -> str:
        return profiles_to_json(self.profiles, target=target, repo_root=repo_root)

    def profile_json(self, name: str) -> str:
        loaded = self.loaded(name)
        return profile_to_json(loaded.profile, source=loaded.source, path=loaded.path)

    def checks_view(
        self,
        name: str,
        *,
        target: Path,
        repo_root: Path,
        changed_paths: tuple[str, ...] = (),
        enforce_required: bool = True,
    ) -> ProfileCheckView:
        system_map_path = resolve_target_system_map(target, config=self.config)
        return checks_view(
            name,
            target,
            repo_root,
            catalog=self.profiles,
            changed_paths=changed_paths,
            enforce_required=enforce_required,
            system_map_path=system_map_path,
        )

    def resolve(self, target: Path) -> ProfileResolution:
        return resolve_profile(target, catalog=self.profiles, config=self.config)

    def template(self, name: str, *, target: Path, preset: str = "generic") -> str:
        return profile_template(name, target=target, preset=preset)
