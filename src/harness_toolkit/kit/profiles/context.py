"""Target-specific profile context for Harness Kit lifecycle operations."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from harness_toolkit.kit.profiles import ProfileCatalog, ProfileError
from harness_toolkit.kit.profiles.models import (
    ProfileCheckView,
    ReviewDefinition,
    WorkflowProfile,
)


@dataclass(frozen=True)
class ProfileContext:
    target: Path
    profile: WorkflowProfile
    view: ProfileCheckView | None = None

    @classmethod
    def resolve(
        cls,
        target: Path,
        *,
        repo_root: Path | None = None,
        changed_paths: tuple[str, ...] = (),
    ) -> ProfileContext:
        catalog = ProfileCatalog.load()
        profile_name = catalog.resolve(target).profile
        profile = catalog.get(profile_name)
        view = None
        if repo_root is not None:
            view = catalog.checks_view(
                profile_name,
                target=target,
                repo_root=repo_root,
                changed_paths=changed_paths,
            )
        return cls(target=target, profile=profile, view=view)

    def validate_check_name(self, check_name: str) -> None:
        if check_name not in {check.name for check in self.profile.checks}:
            valid = ", ".join(check.name for check in self.profile.checks) or "none"
            raise ProfileError(
                f"unknown profile check '{check_name}'. Valid checks: {valid}"
            )

    def review_named(self, review_name: str) -> ReviewDefinition:
        review = next(
            (review for review in self.profile.reviews if review.name == review_name),
            None,
        )
        if review is None:
            valid = ", ".join(review.name for review in self.profile.reviews) or "none"
            raise ProfileError(
                f"unknown profile review '{review_name}'. Valid reviews: {valid}"
            )
        return review
