"""Project configuration dataclass and validation utilities."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# Canonical scaffold root — src/harness_toolkit/scaffold/ is three levels below the repo root.
SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def validate_name(name: str) -> str:
    """Validate project name: lowercase, hyphens, digits, no leading digit."""
    if not re.match(r"^[a-z][a-z0-9-]*$", name):
        raise ValueError(
            f"Invalid project name '{name}': must be lowercase letters, digits, "
            "and hyphens, starting with a letter."
        )
    return name


def validate_module_name(name: str) -> str:
    """Validate apps module name as a safe single path component."""
    try:
        return validate_name(name)
    except ValueError as e:
        raise ValueError(
            f"Invalid module name '{name}': must be lowercase letters, digits, "
            "and hyphens, starting with a letter."
        ) from e


def to_module_name(name: str) -> str:
    """Convert project name to Python module name (hyphens → underscores)."""
    return name.replace("-", "_")


SUPPORTED_STACKS = ("python", "go", "rust")
PLANNED_STACKS = ("web",)
SUPPORTED_SHAPES = ("single", "apps")


@dataclass
class Config:
    name: str
    description: str
    shape: str  # "single" | "apps"
    stack: str  # "python" | "go" | "rust"
    modules: list[str] = field(default_factory=list)
    author_name: str = ""
    author_email: str = ""
    go_module: str = ""
    install_hooks: bool = True
    keep_examples: bool = True
