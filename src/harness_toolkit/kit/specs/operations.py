"""Optional local/committed SPEC operations."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from harness_toolkit.kit.specs.models import SpecOutline, SpecResult


class SpecState(Protocol):
    target_scope: Path
    target_root: Path
    state_dir: Path


class SpecWorkflowError(RuntimeError):
    """Expected spec operation failure."""


def find_specs_for_state(state: SpecState) -> list[str]:
    specs: list[str] = []
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    local = state.state_dir / "spec" / "SPEC.md"
    if committed.exists():
        specs.append(str(committed))
    elif root_committed.exists():
        specs.append(str(root_committed))
    if local.exists():
        specs.append(str(local) + " (local draft)")
    return specs


def init_spec_for_state(state: SpecState) -> SpecResult:
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    if committed.exists():
        return SpecResult(spec_path=str(committed), source="committed", created=False)
    if root_committed.exists():
        return SpecResult(
            spec_path=str(root_committed), source="committed", created=False
        )

    spec_path = state.state_dir / "spec" / "SPEC.md"
    created = not spec_path.exists()
    if created:
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(
            "# Local Project Specification\n\n"
            "Status: local draft\n\n"
            "## Summary\n\nTODO\n\n"
            "## Invariants\n\nTODO\n\n"
            "## Validation Contract\n\nTODO\n"
        )
    return SpecResult(spec_path=str(spec_path), source="local", created=created)


def spec_status_for_state(state: SpecState) -> SpecResult:
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    local = state.state_dir / "spec" / "SPEC.md"
    if committed.exists():
        return SpecResult(spec_path=str(committed), source="committed")
    if root_committed.exists():
        return SpecResult(spec_path=str(root_committed), source="committed")
    if local.exists():
        return SpecResult(spec_path=str(local), source="local")
    raise SpecWorkflowError("No SPEC found. Run `hk spec init --local` first.")


def spec_outline_for_state(state: SpecState) -> SpecOutline:
    current = spec_status_for_state(state)
    path = Path(current.spec_path)
    headings = [
        line.strip() for line in path.read_text().splitlines() if line.startswith("#")
    ]
    return SpecOutline(
        spec_path=current.spec_path, source=current.source, headings=headings
    )


def spec_promote_dry_run_for_state(state: SpecState) -> str:
    current = spec_status_for_state(state)
    if current.source == "committed":
        return f"Committed SPEC already exists: {current.spec_path}\n"
    target_path = state.target_scope / "SPEC.md"
    content = Path(current.spec_path).read_text()
    return f"Would write local spec to {target_path}\n\n--- SPEC.md ---\n{content}"
