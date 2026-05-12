"""Profile data models for Harness Kit guidance."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ProfileName = str
ProfileSource = Literal["built-in", "file", "user-config"]
RunFrom = Literal["target", "repo-root", "current-directory", "external-ui"]
VALID_RUN_FROM: tuple[RunFrom, ...] = (
    "target",
    "repo-root",
    "current-directory",
    "external-ui",
)
BUILTIN_PRESETS = ("generic", "python", "go", "rust", "rust-mise")


@dataclass(frozen=True)
class CheckDefinition:
    name: str
    purpose: str
    command_template: str
    run_from: RunFrom
    required_inputs: tuple[str, ...] = ()
    notes: tuple[str, ...] = ()
    agent_should_run_directly: bool = True
    applies_when: tuple[str, ...] = ()
    required_when: tuple[str, ...] = ()


@dataclass(frozen=True)
class ReviewDefinition:
    name: str
    purpose: str
    backend: str
    rubric: str
    dispatch_hint: str = ""
    prompt: str = ""
    prompt_file: str | None = None
    prompt_file_text: str = ""
    applies_when: tuple[str, ...] = ()
    required_when: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProfileSuggestion:
    name: str
    purpose: str
    required: bool
    matched_by: str
    matched_paths: tuple[str, ...]
    matched_patterns: tuple[str, ...] = ()
    enforced: bool = False
    record_command: str = ""
    prompt_command: str = ""


@dataclass(frozen=True)
class WorkflowProfile:
    name: ProfileName
    title: str
    summary: str
    target_hint: str
    instructions: str
    checks: tuple[CheckDefinition, ...]
    reviews: tuple[ReviewDefinition, ...] = ()


@dataclass(frozen=True)
class LoadedProfile:
    profile: WorkflowProfile
    source: ProfileSource
    path: str | None = None


@dataclass(frozen=True)
class TargetBinding:
    name: str
    path: str
    profile: ProfileName


@dataclass(frozen=True)
class HarnessConfig:
    path: str
    default_profile: ProfileName
    targets: tuple[TargetBinding, ...]
    profiles_dirs: tuple[str, ...] = ()


@dataclass(frozen=True)
class ProfileResolution:
    profile: ProfileName
    source: str
    reason: str
    target: str
    match_kind: str
    matched_target: str | None = None
    matched_name: str | None = None
    config_path: str | None = None
    worktree_target: str | None = None
    worktree_matched_target: str | None = None
    worktree_projected_target: str | None = None
    worktree_git_common_dir: str | None = None


@dataclass(frozen=True)
class ProfileCheckView:
    profile: ProfileName
    target: str
    repo_root: str
    checks: tuple[CheckDefinition, ...]
    reviews: tuple[ReviewDefinition, ...]
    reminder: str
    changed_paths: tuple[str, ...] = ()
    suggested_checks: tuple[ProfileSuggestion, ...] = ()
    suggested_reviews: tuple[ProfileSuggestion, ...] = ()


class ProfileError(ValueError):
    """Raised when profile loading or validation fails."""
