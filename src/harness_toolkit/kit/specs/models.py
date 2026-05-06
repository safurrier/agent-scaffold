"""Spec result models for optional HK2 spec support."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SpecResult:
    spec_path: str
    source: str
    created: bool = False


@dataclass(frozen=True)
class SpecOutline:
    spec_path: str
    source: str
    headings: list[str]
