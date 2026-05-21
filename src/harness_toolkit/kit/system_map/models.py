"""Data models for Harness Kit system maps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

FindingSeverity = Literal["error", "warning", "info"]
SystemMapStatus = Literal["valid", "invalid"]
SystemMapSourceKind = Literal["repo-local", "target-config"]
LabelResolutionStatus = Literal["skipped", "resolved", "unresolved"]


@dataclass(frozen=True)
class SystemMapFinding:
    code: str
    severity: FindingSeverity
    message: str
    field_path: str | None = None
    related_path: str | None = None
    check_label: str | None = None


@dataclass(frozen=True)
class SystemInfo:
    name: str
    summary: str


@dataclass(frozen=True)
class InvariantDefinition:
    id: str
    statement: str
    evidence: tuple[str, ...] = ()
    validation_checks: tuple[str, ...] = ()


@dataclass(frozen=True)
class ComponentDefinition:
    id: str
    title: str
    kind: str
    paths: tuple[str, ...]
    read_before_editing: tuple[str, ...] = ()
    validation_checks: tuple[str, ...] = ()
    invariants: tuple[InvariantDefinition, ...] = ()


@dataclass(frozen=True)
class RelationDefinition:
    from_component: str
    to_component: str
    kind: str
    rule: str


@dataclass(frozen=True)
class SystemMap:
    version: int
    system: SystemInfo
    components: tuple[ComponentDefinition, ...]
    relations: tuple[RelationDefinition, ...] = ()

    @property
    def invariant_count(self) -> int:
        return sum(len(component.invariants) for component in self.components)


@dataclass(frozen=True)
class SystemMapSource:
    path: str
    source: SystemMapSourceKind
    path_base: str = "repo-root"
    overrides: str | None = None


@dataclass(frozen=True)
class SystemMapLoadResult:
    path: str
    map: SystemMap | None
    findings: tuple[SystemMapFinding, ...]
    source: SystemMapSourceKind = "repo-local"
    path_base: str = "repo-root"
    overrides: str | None = None

    @property
    def ok(self) -> bool:
        return not any(finding.severity == "error" for finding in self.findings)


@dataclass(frozen=True)
class SystemMapSummary:
    path: str
    version: int | None
    status: SystemMapStatus
    components: int
    invariants: int
    warnings_count: int
    errors_count: int
    source: SystemMapSourceKind = "repo-local"
    path_base: str = "repo-root"
    overrides: str | None = None
    label_resolution: LabelResolutionStatus = "skipped"


@dataclass(frozen=True)
class RelevantCheckLabel:
    name: str
    source: str = "system_map"
    required_by_profile: bool | None = None


@dataclass(frozen=True)
class MatchedInvariant:
    id: str
    qualified_id: str
    statement: str
    relevant_check_labels: tuple[RelevantCheckLabel, ...] = ()


@dataclass(frozen=True)
class MatchedComponent:
    id: str
    title: str
    kind: str
    matched_paths: tuple[str, ...]
    read_before_editing: tuple[str, ...] = ()
    relevant_check_labels: tuple[RelevantCheckLabel, ...] = ()
    invariants: tuple[MatchedInvariant, ...] = ()


@dataclass(frozen=True)
class LabelResolution:
    status: LabelResolutionStatus
    profile: str | None = None
    unresolved_check_labels: tuple[str, ...] = ()


@dataclass(frozen=True)
class SystemContextView:
    advisory: bool
    source: str
    label_resolution: LabelResolution
    matched_components: tuple[MatchedComponent, ...]
    source_kind: SystemMapSourceKind = "repo-local"
    path_base: str = "repo-root"
    overrides: str | None = None
    invariant_policy: str = "must_preserve_unless_superseded"
    conflict_protocol: str = "stop_confirm_record_decision"
    warnings: tuple[SystemMapFinding, ...] = ()
