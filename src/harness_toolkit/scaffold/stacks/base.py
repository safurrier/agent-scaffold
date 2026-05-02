"""Stack Protocol — structural interface for stack implementations."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from harness_toolkit.scaffold.config import Config


class Stack(Protocol):
    def init_single(self, root: Path, config: Config) -> dict[str, str]:
        """Lay out single-project files; return extra Jinja2 context vars."""
        ...

    def init_module(
        self, mod_dir: Path, config: Config, mod_name: str
    ) -> dict[str, str]:
        """Lay out one apps-workspace module; return extra context vars."""
        ...

    def remove_examples(self, root: Path, config: Config) -> None:
        """Remove example source files from a single-project layout."""
        ...

    def remove_module_examples(self, mod_dir: Path) -> None:
        """Remove example source files from one apps-workspace module."""
        ...

    def tools_toml(self) -> str:
        """Return the [tools] section content for .mise.toml."""
        ...

    def adr_notes(self) -> str:
        """Return stack description for the 0001-stack-choice.md ADR."""
        ...

    def stack_notes(self) -> str:
        """Return stack tooling summary for AGENTS.md."""
        ...
