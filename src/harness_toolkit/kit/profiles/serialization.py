"""JSON serialization for profile discovery views."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import cast

from harness_toolkit.kit.profiles.guidance import PROFILE_SELECTION_GUIDANCE
from harness_toolkit.kit.profiles.models import (
    LoadedProfile,
    ProfileCheckView,
    ProfileResolution,
    WorkflowProfile,
)


def _without_loaded_instruction_text(value: object) -> object:
    if isinstance(value, dict):
        data = cast("dict[str, object]", value)
        omit_file_text = data.get("type") == "file" and bool(data.get("path"))
        return {
            key: _without_loaded_instruction_text(item)
            for key, item in data.items()
            if not (omit_file_text and key == "text")
        }
    if isinstance(value, list | tuple):
        return [_without_loaded_instruction_text(item) for item in value]
    return value


def profile_to_json(
    profile: WorkflowProfile, *, source: str = "built-in", path: str | None = None
) -> str:
    payload = cast(
        "dict[str, object]", _without_loaded_instruction_text(asdict(profile))
    )
    payload["source"] = source
    if path is not None:
        payload["path"] = path
    return json.dumps(payload, indent=2, sort_keys=True)


def profiles_to_json(
    catalog: dict[str, LoadedProfile] | None = None,
    target: Path | None = None,
    repo_root: Path | None = None,
) -> str:
    if not catalog:
        from harness_toolkit.kit.profiles.loading import load_profile_catalog

        resolved_catalog = load_profile_catalog()[0]
    else:
        resolved_catalog = catalog
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


def checks_to_json(view: ProfileCheckView) -> str:
    return json.dumps(
        _without_loaded_instruction_text(asdict(view)), indent=2, sort_keys=True
    )


def resolution_to_json(resolution: ProfileResolution) -> str:
    return json.dumps(asdict(resolution), indent=2, sort_keys=True)
