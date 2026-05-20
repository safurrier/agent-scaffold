from __future__ import annotations

from harness_toolkit.kit.system_map.models import (
    ComponentDefinition,
    InvariantDefinition,
    SystemInfo,
    SystemMap,
)


def test_system_map_counts_nested_invariants() -> None:
    system_map = SystemMap(
        version=1,
        system=SystemInfo(name="demo", summary="Demo."),
        components=(
            ComponentDefinition(
                id="core",
                title="Core",
                kind="module",
                paths=("src/**",),
                invariants=(
                    InvariantDefinition(id="one", statement="One."),
                    InvariantDefinition(id="two", statement="Two."),
                ),
            ),
        ),
    )

    assert system_map.invariant_count == 2
