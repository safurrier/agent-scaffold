"""Harness Kit system-map loading and matching."""

from __future__ import annotations

from harness_toolkit.kit.system_map.matching import system_context_for_changed_paths
from harness_toolkit.kit.system_map.models import (
    ComponentDefinition,
    InvariantDefinition,
    LabelResolution,
    MatchedComponent,
    MatchedInvariant,
    RelationDefinition,
    RelevantCheckLabel,
    SystemContextView,
    SystemInfo,
    SystemMap,
    SystemMapFinding,
    SystemMapLoadResult,
    SystemMapSource,
    SystemMapSummary,
)
from harness_toolkit.kit.system_map.parser import parse_system_map_file
from harness_toolkit.kit.system_map.resolution import (
    find_repo_local_system_map,
    load_system_map,
    load_system_map_source,
    resolve_system_map_source,
)
from harness_toolkit.kit.system_map.serialization import summary_from_load_result
from harness_toolkit.kit.system_map.validation import (
    check_label_findings,
    referenced_check_labels,
)

__all__ = [
    "ComponentDefinition",
    "InvariantDefinition",
    "LabelResolution",
    "MatchedComponent",
    "MatchedInvariant",
    "RelevantCheckLabel",
    "RelationDefinition",
    "SystemContextView",
    "SystemInfo",
    "SystemMap",
    "SystemMapFinding",
    "SystemMapLoadResult",
    "SystemMapSource",
    "SystemMapSummary",
    "check_label_findings",
    "find_repo_local_system_map",
    "load_system_map",
    "load_system_map_source",
    "parse_system_map_file",
    "referenced_check_labels",
    "resolve_system_map_source",
    "summary_from_load_result",
    "system_context_for_changed_paths",
]
