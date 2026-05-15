"""Editable profile TOML template generation."""

from __future__ import annotations

import json
from pathlib import Path

from harness_toolkit.kit.profiles.builtins import BUILTIN_PROFILES
from harness_toolkit.kit.profiles.models import (
    BUILTIN_PRESETS,
    CheckDefinition,
    ProfileError,
)
from harness_toolkit.kit.profiles.validation import validate_profile_name
from harness_toolkit.names import KIT_COMMAND


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
        "- Confirm when heavier validation is required.\n"
        "- Replace broad required_when patterns with explicit risk paths before relying on the profile.\n\n"
        "Run validation commands directly and record exact command/result evidence "
        "with hk validate --why before handoff. Do not chase final readiness after "
        "every edit: use focused checks while iterating, run broad final gates once "
        "implementation is stable, and after small review fixes prefer targeted "
        "validation/review for changed paths unless behavior or design changed."
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
                purpose="TODO: Run the final validation gate appropriate before handoff; not the repeated inner-loop check.",
                command_template="TODO: e.g. mise run check",
                run_from="repo-root",
                notes=(
                    "Replace this TODO before relying on the profile.",
                    "Use focused checks while iterating; run this once implementation is stable.",
                ),
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
