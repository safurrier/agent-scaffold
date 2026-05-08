"""Validation helpers for profile identifiers."""

from __future__ import annotations

import re

from harness_toolkit.kit.profiles.models import ProfileError


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
