"""Built-in and custom profile/check DSL for portable agent workflows.

Profiles describe named verification loops. They intentionally do not execute
those loops; agents should run the suggested commands directly so raw output stays
visible in the normal agent shell loop.
"""

from __future__ import annotations

import json
import os
import re
import shlex
import tomllib
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import cast

from pathspec import PathSpec

from harness_toolkit.kit.profiles.builtins import BUILTIN_PROFILES, loaded_builtins
from harness_toolkit.kit.profiles.models import (
    BUILTIN_PRESETS,
    VALID_RUN_FROM,
    CheckDefinition,
    HarnessConfig,
    LoadedProfile,
    ProfileCheckView,
    ProfileError,
    ProfileName,
    ProfileResolution,
    ProfileSuggestion,
    ReviewDefinition,
    RunFrom,
    TargetBinding,
    WorkflowProfile,
)
from harness_toolkit.kit.profiles.resolution import (
    resolve_profile as resolve_target_profile,
)
from harness_toolkit.names import KIT_COMMAND


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
        return checks_view(
            name,
            target,
            repo_root,
            catalog=self.profiles,
            changed_paths=changed_paths,
            enforce_required=enforce_required,
        )

    def resolve(self, target: Path) -> ProfileResolution:
        return resolve_profile(target, catalog=self.profiles, config=self.config)

    def template(self, name: str, *, target: Path, preset: str = "generic") -> str:
        return profile_template(name, target=target, preset=preset)


PROFILE_SELECTION_GUIDANCE = """Choose the closest available profile yourself unless user config explicitly resolves one; the CLI does not use heuristic auto-selection.

Match the profile to the target scope, not just the repository root. In monorepos,
pass `--target` as the module/package/crate directory that owns the work, then
inspect that module's files first and repo-level AGENTS.md/README guidance second.
Prefer profiles in this order:
1. exact target/module profile
2. repo-specific profile
3. stack/task-runner profile
4. generic fallback

Tell the user once which profile you chose and why, then use that profile
consistently for plan, checks, and readiness.

Examples:
- --target my_project/api and profile my-project-api exists -> my-project-api
- --target my_project/api and no module profile exists, but pyproject.toml exists -> python
- --target crates/tui and profile foreman-tui exists -> foreman-tui
- --target crates/tui and no module profile exists, but Cargo.toml exists -> rust
- Rust repo with mise task contract but no exact module profile -> rust-mise
- no close target/module match -> generic
"""


def profile_names(
    catalog: dict[str, LoadedProfile] | None = None,
) -> tuple[ProfileName, ...]:
    resolved_catalog = catalog or load_profile_catalog()[0]
    return tuple(resolved_catalog.keys())


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


def _normalize_config_path(value: str, *, base_dir: Path) -> Path:
    expanded = Path(os.path.expandvars(value)).expanduser()
    if not expanded.is_absolute():
        expanded = base_dir / expanded
    return expanded.resolve(strict=False)


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
                path=str(_normalize_config_path(raw_path, base_dir=base_dir)),
                profile=profile,
            )
        )
    return HarnessConfig(
        path=str(path),
        default_profile=default_profile,
        targets=tuple(targets),
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


def load_profile_file(path: Path) -> LoadedProfile:
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ProfileError(f"invalid profile TOML {path}: {e}") from e
    profile = parse_profile_data(data, source=str(path), base_dir=path.parent)
    return LoadedProfile(profile=profile, source="file", path=str(path))


def _required_str(data: dict[str, object], key: str, *, source: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ProfileError(f"profile {source} must define non-empty string '{key}'")
    return value


def _optional_str(data: dict[str, object], key: str, *, source: str) -> str:
    value = data.get(key, "")
    if value is None:
        return ""
    if not isinstance(value, str):
        raise ProfileError(f"profile {source} field '{key}' must be a string")
    return value


def _optional_str_tuple(
    data: dict[str, object], key: str, *, source: str
) -> tuple[str, ...]:
    value = data.get(key, [])
    if value is None:
        return ()
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        raise ProfileError(f"profile {source} field '{key}' must be a string array")
    return tuple(cast("list[str]", value))


def parse_profile_data(
    data: object, *, source: str, base_dir: Path | None = None
) -> WorkflowProfile:
    if not isinstance(data, dict):
        raise ProfileError(f"profile {source} must be a TOML table")
    data = cast("dict[str, object]", data)

    name = _required_str(data, "name", source=source)
    validate_profile_name(name)
    checks_data = data.get("checks")
    if not isinstance(checks_data, list) or not checks_data:
        raise ProfileError(
            f"profile {source} must define at least one [[checks]] entry"
        )

    checks: list[CheckDefinition] = []
    check_names: set[str] = set()
    for index, raw_check in enumerate(checks_data, start=1):
        if not isinstance(raw_check, dict):
            raise ProfileError(f"profile {source} check #{index} must be a TOML table")
        run_from = _required_str(raw_check, "run_from", source=source)
        if run_from not in VALID_RUN_FROM:
            valid = ", ".join(VALID_RUN_FROM)
            raise ProfileError(
                f"profile {source} check #{index} has invalid run_from '{run_from}'. Valid: {valid}"
            )
        typed_run_from = cast(RunFrom, run_from)
        agent_should_run_directly = raw_check.get("agent_should_run_directly", True)
        if not isinstance(agent_should_run_directly, bool):
            raise ProfileError(
                f"profile {source} check #{index} field 'agent_should_run_directly' must be boolean"
            )
        check_name = _required_str(raw_check, "name", source=source)
        validate_item_name(check_name, kind="check", source=source)
        if check_name in check_names:
            raise ProfileError(
                f"profile {source} has duplicate check name '{check_name}'"
            )
        check_names.add(check_name)
        checks.append(
            CheckDefinition(
                name=check_name,
                purpose=_required_str(raw_check, "purpose", source=source),
                command_template=_required_str(
                    raw_check, "command_template", source=source
                ),
                run_from=typed_run_from,
                required_inputs=_optional_str_tuple(
                    raw_check, "required_inputs", source=source
                ),
                notes=_optional_str_tuple(raw_check, "notes", source=source),
                agent_should_run_directly=agent_should_run_directly,
                applies_when=_optional_str_tuple(
                    raw_check, "applies_when", source=source
                ),
                required_when=_optional_str_tuple(
                    raw_check, "required_when", source=source
                ),
            )
        )

    reviews_data = data.get("reviews", [])
    if reviews_data is None:
        reviews_data = []
    if not isinstance(reviews_data, list):
        raise ProfileError(f"profile {source} field 'reviews' must be an array")
    reviews: list[ReviewDefinition] = []
    review_names: set[str] = set()
    for index, raw_review in enumerate(reviews_data, start=1):
        if not isinstance(raw_review, dict):
            raise ProfileError(f"profile {source} review #{index} must be a TOML table")
        raw_review = cast("dict[str, object]", raw_review)
        prompt_file_value = raw_review.get("prompt_file")
        prompt_file: str | None = None
        prompt_file_text = ""
        if prompt_file_value is not None:
            if not isinstance(prompt_file_value, str) or not prompt_file_value.strip():
                raise ProfileError(
                    f"profile {source} review #{index} field 'prompt_file' must be a string"
                )
            prompt_file = prompt_file_value
            if base_dir is not None:
                prompt_path = _normalize_config_path(prompt_file, base_dir=base_dir)
                try:
                    prompt_file_text = prompt_path.read_text()
                except OSError as e:
                    raise ProfileError(
                        f"profile {source} review #{index} could not read prompt_file {prompt_file}: {e}"
                    ) from e
        review_name = _required_str(raw_review, "name", source=source)
        validate_item_name(review_name, kind="review", source=source)
        if review_name in review_names:
            raise ProfileError(
                f"profile {source} has duplicate review name '{review_name}'"
            )
        review_names.add(review_name)
        reviews.append(
            ReviewDefinition(
                name=review_name,
                purpose=_required_str(raw_review, "purpose", source=source),
                backend=_required_str(raw_review, "backend", source=source),
                rubric=_required_str(raw_review, "rubric", source=source),
                dispatch_hint=_optional_str(raw_review, "dispatch_hint", source=source),
                prompt=_optional_str(raw_review, "prompt", source=source),
                prompt_file=prompt_file,
                prompt_file_text=prompt_file_text,
                applies_when=_optional_str_tuple(
                    raw_review, "applies_when", source=source
                ),
                required_when=_optional_str_tuple(
                    raw_review, "required_when", source=source
                ),
            )
        )

    return WorkflowProfile(
        name=name,
        title=_required_str(data, "title", source=source),
        summary=_required_str(data, "summary", source=source),
        target_hint=_required_str(data, "target_hint", source=source),
        instructions=_required_str(data, "instructions", source=source),
        checks=tuple(checks),
        reviews=tuple(reviews),
    )


def validate_profile_name(name: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ProfileError(
            "profile name must be lowercase and contain only letters, numbers, '.', '_', or '-'"
        )


def validate_item_name(name: str, *, kind: str, source: str) -> None:
    if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", name):
        raise ProfileError(
            f"profile {source} {kind} name must be lowercase and contain only letters, numbers, '.', '_', or '-'"
        )


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


def _without_prompt_file_text(value: object) -> object:
    if isinstance(value, dict):
        return {
            key: _without_prompt_file_text(item)
            for key, item in value.items()
            if key != "prompt_file_text"
        }
    if isinstance(value, list | tuple):
        return [_without_prompt_file_text(item) for item in value]
    return value


def profile_to_json(
    profile: WorkflowProfile, *, source: str = "built-in", path: str | None = None
) -> str:
    payload = cast("dict[str, object]", _without_prompt_file_text(asdict(profile)))
    payload["source"] = source
    if path is not None:
        payload["path"] = path
    return json.dumps(payload, indent=2, sort_keys=True)


def profiles_to_json(
    catalog: dict[str, LoadedProfile] | None = None,
    target: Path | None = None,
    repo_root: Path | None = None,
) -> str:
    resolved_catalog = catalog or load_profile_catalog()[0]
    rows = [
        {
            "name": loaded.profile.name,
            "title": loaded.profile.title,
            "summary": loaded.profile.summary,
            "target_hint": loaded.profile.target_hint,
            "source": loaded.source,
            **({"path": loaded.path} if loaded.path else {}),
        }
        for loaded in resolved_catalog.values()
    ]
    payload: dict[str, object] = {
        "profiles": rows,
        "selection_guidance": PROFILE_SELECTION_GUIDANCE,
    }
    if target is not None and repo_root is not None:
        payload.update({"target": str(target), "repo_root": str(repo_root)})
    return json.dumps(payload, indent=2, sort_keys=True)


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


def _matched_paths(
    patterns: tuple[str, ...], changed_paths: tuple[str, ...]
) -> tuple[str, ...]:
    clean_patterns = tuple(_normalize_pattern(pattern) for pattern in patterns)
    if not clean_patterns:
        return ()
    spec = PathSpec.from_lines("gitignore", clean_patterns)
    matches: list[str] = []
    for path in changed_paths:
        clean_path = _normalize_changed_path(path)
        if clean_path and spec.match_file(clean_path):
            matches.append(clean_path)
    return tuple(dict.fromkeys(matches))


def _check_suggestions(
    profile: WorkflowProfile, changed_paths: tuple[str, ...], *, enforce_required: bool
) -> tuple[ProfileSuggestion, ...]:
    suggestions: list[ProfileSuggestion] = []
    for check in profile.checks:
        record_command = (
            f"hk validate --check {shlex.quote(check.name)} "
            "--why '...' -- <native command>"
        )
        required_matches = _matched_paths(check.required_when, changed_paths)
        applies_matches = _matched_paths(check.applies_when, changed_paths)
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
) -> tuple[ProfileSuggestion, ...]:
    suggestions: list[ProfileSuggestion] = []
    for review in profile.reviews:
        prompt_command = (
            f"hk review prompt {shlex.quote(review.name)} "
            f"--target {shlex.quote(str(target))}"
        )
        record_command = f"hk review add --review {shlex.quote(review.name)} ..."
        required_matches = _matched_paths(review.required_when, changed_paths)
        applies_matches = _matched_paths(review.applies_when, changed_paths)
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
            profile, normalized_changed_paths, enforce_required=enforce_required
        ),
        suggested_reviews=_review_suggestions(
            profile,
            normalized_changed_paths,
            enforce_required=enforce_required,
            target=target,
        ),
    )


def checks_to_json(view: ProfileCheckView) -> str:
    return json.dumps(_without_prompt_file_text(asdict(view)), indent=2, sort_keys=True)


def resolution_to_json(resolution: ProfileResolution) -> str:
    return json.dumps(asdict(resolution), indent=2, sort_keys=True)


def resolve_profile(
    target: Path,
    *,
    catalog: dict[str, LoadedProfile] | None = None,
    config: HarnessConfig | None = None,
) -> ProfileResolution:
    return resolve_target_profile(target, catalog=catalog, config=config)


def _toml_string(value: str) -> str:
    return json.dumps(value)


def _toml_array(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(_toml_string(value) for value in values) + "]"


def _title_from_name(name: str) -> str:
    return name.replace("-", " ").replace("_", " ").title()


def profile_template(name: str, *, target: Path, preset: str = "generic") -> str:
    validate_profile_name(name)
    if preset not in BUILTIN_PRESETS:
        valid = ", ".join(BUILTIN_PRESETS)
        raise ProfileError(f"Unknown preset '{preset}'. Valid presets: {valid}")

    preset_profile = BUILTIN_PROFILES[preset]
    target_text = str(target)
    instructions = (
        f"Use this profile for work under {target_text}.\n\n"
        "TODO:\n"
        "- Confirm the fast validation gate for this target/module.\n"
        "- Confirm focused test command patterns.\n"
        "- Confirm when heavier validation is required.\n\n"
        "Run validation commands directly and record exact command/result evidence "
        "with hk validate --why before handoff."
    )

    checks = [
        check
        for check in preset_profile.checks
        if check.name not in {"handoff", "handoff-readiness"}
    ]
    if preset == "generic":
        checks = [
            CheckDefinition(
                name="fast-gate",
                purpose="TODO: Run the fastest validation gate appropriate before handoff.",
                command_template="TODO: e.g. mise run check",
                run_from="repo-root",
                notes=("Replace this TODO before relying on the profile.",),
            ),
            CheckDefinition(
                name="focused-tests",
                purpose="TODO: Run focused tests for the changed area.",
                command_template="TODO: e.g. uv run pytest <test_path_or_selector>",
                run_from="target",
                required_inputs=("test_path_or_selector",),
                notes=("Use the smallest test path that covers the change.",),
            ),
        ]
    checks.append(
        CheckDefinition(
            name="handoff-readiness",
            purpose="Checkpoint lifecycle freshness and check handoff readiness.",
            command_template=f"{KIT_COMMAND} sync --target <target> --json && {KIT_COMMAND} ready --target <target> --json",
            run_from="current-directory",
            notes=("This checks recorded evidence; it does not rerun validation.",),
        )
    )

    lines = [
        f"name = {_toml_string(name)}",
        f"title = {_toml_string(_title_from_name(name))}",
        f"summary = {_toml_string(f'TODO: Describe the validation contract for {target_text}.')}",
        f"target_hint = {_toml_string(f'Use --target {target_text}.')}",
        "",
        f"instructions = {_toml_string(instructions)}",
        "",
    ]
    for check in checks:
        lines.extend(
            [
                "[[checks]]",
                f"name = {_toml_string(check.name)}",
                f"purpose = {_toml_string(check.purpose)}",
                f"command_template = {_toml_string(check.command_template)}",
                f"run_from = {_toml_string(check.run_from)}",
            ]
        )
        if check.required_inputs:
            lines.append(f"required_inputs = {_toml_array(check.required_inputs)}")
        if check.notes:
            lines.append(f"notes = {_toml_array(check.notes)}")
        if not check.agent_should_run_directly:
            lines.append("agent_should_run_directly = false")
        lines.append("")
    return "\n".join(lines)
