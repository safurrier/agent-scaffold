"""TOML parsing for Harness Kit workflow profiles."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import cast

from harness_toolkit.kit.profiles.models import (
    VALID_RUN_FROM,
    CheckDefinition,
    LoadedProfile,
    ProfileError,
    ReviewDefinition,
    RunFrom,
    WorkflowProfile,
)
from harness_toolkit.kit.profiles.validation import (
    validate_item_name,
    validate_profile_name,
)


def normalize_config_path(value: str, *, base_dir: Path) -> Path:
    expanded = Path(os.path.expandvars(value)).expanduser()
    if not expanded.is_absolute():
        expanded = base_dir / expanded
    return expanded.resolve(strict=False)


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
                prompt_path = normalize_config_path(prompt_file, base_dir=base_dir)
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


def load_profile_file(path: Path) -> LoadedProfile:
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        raise ProfileError(f"invalid profile TOML {path}: {e}") from e
    profile = parse_profile_data(data, source=str(path), base_dir=path.parent)
    return LoadedProfile(profile=profile, source="file", path=str(path))
