"""Parser and structural validator for .harness/system.toml."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any, cast

from harness_toolkit.kit.system_map.models import (
    ComponentDefinition,
    InvariantDefinition,
    RelationDefinition,
    SystemInfo,
    SystemMap,
    SystemMapFinding,
    SystemMapLoadResult,
)

ID_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
COMMANDISH_RE = re.compile(
    r"\b(cargo|pytest|uv|npm|pnpm|yarn|go test|mise|make|python)\b"
)
MAX_SUMMARY = 180
MAX_STATEMENT = 220
MAX_RULE = 220
KNOWN_TOP_LEVEL = {"version", "system", "components", "relations"}
KNOWN_SYSTEM = {"name", "summary"}
KNOWN_COMPONENT = {
    "id",
    "title",
    "kind",
    "paths",
    "read_before_editing",
    "validation_checks",
    "invariants",
}
KNOWN_INVARIANT = {"id", "statement", "evidence", "validation_checks"}
KNOWN_RELATION = {"from", "to", "kind", "rule"}


def _finding(
    code: str,
    severity: str,
    message: str,
    field_path: str | None = None,
    related_path: str | None = None,
    check_label: str | None = None,
) -> SystemMapFinding:
    return SystemMapFinding(
        code=code,
        severity=cast("Any", severity),
        message=message,
        field_path=field_path,
        related_path=related_path,
        check_label=check_label,
    )


def _unknown_findings(
    findings: list[SystemMapFinding],
    table: dict[str, Any],
    allowed: set[str],
    field_path: str,
) -> None:
    for key in sorted(set(table) - allowed):
        findings.append(
            _finding(
                "unknown-field",
                "warning",
                f"unknown field '{key}' at {field_path or 'root'}",
                f"{field_path}.{key}" if field_path else key,
            )
        )


def _string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _string_tuple(value: Any) -> tuple[str, ...] | None:
    if not isinstance(value, list):
        return None
    items: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            return None
        items.append(item.strip())
    return tuple(items)


def _validate_path_refs(
    repo_root: Path,
    refs: tuple[str, ...],
    *,
    field_path: str,
    code: str,
    findings: list[SystemMapFinding],
) -> None:
    from harness_toolkit.kit.system_map.validation import path_exists_or_glob

    for index, ref in enumerate(refs):
        if not path_exists_or_glob(repo_root, ref):
            findings.append(
                _finding(
                    code,
                    "error",
                    f"referenced path/glob does not exist: {ref}",
                    f"{field_path}[{index}]",
                    ref,
                )
            )


def parse_system_map_file(path: Path, *, repo_root: Path) -> SystemMapLoadResult:
    findings: list[SystemMapFinding] = []
    if not path.exists():
        findings.append(
            _finding("missing-system-map", "error", f"system map not found: {path}")
        )
        return SystemMapLoadResult(path=str(path), map=None, findings=tuple(findings))
    try:
        data = tomllib.loads(path.read_text())
    except tomllib.TOMLDecodeError as e:
        findings.append(_finding("invalid-toml", "error", f"invalid TOML: {e}"))
        return SystemMapLoadResult(path=str(path), map=None, findings=tuple(findings))
    if not isinstance(data, dict):
        findings.append(
            _finding("invalid-root", "error", "root TOML value must be a table")
        )
        return SystemMapLoadResult(path=str(path), map=None, findings=tuple(findings))

    _unknown_findings(findings, data, KNOWN_TOP_LEVEL, "")

    version = data.get("version")
    if version != 1:
        findings.append(
            _finding("invalid-version", "error", "version = 1 is required", "version")
        )
        version = 1 if isinstance(version, int) else 0

    raw_system = data.get("system")
    system = SystemInfo(name="", summary="")
    if not isinstance(raw_system, dict):
        findings.append(
            _finding("missing-system", "error", "[system] table is required", "system")
        )
    else:
        _unknown_findings(findings, raw_system, KNOWN_SYSTEM, "system")
        name = _string(raw_system.get("name"))
        summary = _string(raw_system.get("summary"))
        if name is None:
            findings.append(
                _finding(
                    "missing-system-field",
                    "error",
                    "[system].name is required",
                    "system.name",
                )
            )
            name = ""
        if summary is None:
            findings.append(
                _finding(
                    "missing-system-field",
                    "error",
                    "[system].summary is required",
                    "system.summary",
                )
            )
            summary = ""
        elif len(summary) > MAX_SUMMARY:
            findings.append(
                _finding(
                    "long-summary",
                    "warning",
                    f"system.summary should be <= {MAX_SUMMARY} chars",
                    "system.summary",
                )
            )
        system = SystemInfo(name=name, summary=summary)

    raw_components = data.get("components")
    if not isinstance(raw_components, list) or not raw_components:
        findings.append(
            _finding(
                "missing-components",
                "error",
                "at least one [[components]] table is required",
                "components",
            )
        )
        raw_components = []

    components: list[ComponentDefinition] = []
    component_ids: set[str] = set()
    for component_index, raw_component in enumerate(raw_components):
        cpath = f"components[{component_index}]"
        if not isinstance(raw_component, dict):
            findings.append(
                _finding(
                    "invalid-component", "error", "component must be a table", cpath
                )
            )
            continue
        _unknown_findings(findings, raw_component, KNOWN_COMPONENT, cpath)
        cid = _string(raw_component.get("id")) or ""
        if not ID_RE.match(cid):
            findings.append(
                _finding(
                    "invalid-component-id",
                    "error",
                    "component id must be kebab-case",
                    f"{cpath}.id",
                )
            )
        elif cid in component_ids:
            findings.append(
                _finding(
                    "duplicate-component-id",
                    "error",
                    f"duplicate component id '{cid}'",
                    f"{cpath}.id",
                )
            )
        component_ids.add(cid)

        title = _string(raw_component.get("title")) or ""
        kind = _string(raw_component.get("kind")) or ""
        for key, value in (("title", title), ("kind", kind)):
            if not value:
                findings.append(
                    _finding(
                        "missing-component-field",
                        "error",
                        f"component {cid or component_index} missing {key}",
                        f"{cpath}.{key}",
                    )
                )

        paths = _string_tuple(raw_component.get("paths"))
        if not paths:
            findings.append(
                _finding(
                    "invalid-paths",
                    "error",
                    f"component {cid or component_index} paths must be a non-empty string array",
                    f"{cpath}.paths",
                )
            )
            paths = ()
        _validate_path_refs(
            repo_root,
            paths,
            field_path=f"{cpath}.paths",
            code="missing-path",
            findings=findings,
        )

        read_before = _string_tuple(raw_component.get("read_before_editing", []))
        if read_before is None:
            findings.append(
                _finding(
                    "invalid-string-list",
                    "error",
                    f"component {cid} read_before_editing must be a string array",
                    f"{cpath}.read_before_editing",
                )
            )
            read_before = ()
        _validate_path_refs(
            repo_root,
            read_before,
            field_path=f"{cpath}.read_before_editing",
            code="missing-read-before",
            findings=findings,
        )

        checks = _string_tuple(raw_component.get("validation_checks", []))
        if checks is None:
            findings.append(
                _finding(
                    "invalid-string-list",
                    "error",
                    f"component {cid} validation_checks must be a string array",
                    f"{cpath}.validation_checks",
                )
            )
            checks = ()
        for label in checks:
            if COMMANDISH_RE.search(label):
                findings.append(
                    _finding(
                        "command-in-check-label",
                        "error",
                        "validation_checks must contain labels, not commands",
                        f"{cpath}.validation_checks",
                        check_label=label,
                    )
                )

        raw_invariants = raw_component.get("invariants", [])
        if raw_invariants is None:
            raw_invariants = []
        if not isinstance(raw_invariants, list):
            findings.append(
                _finding(
                    "invalid-invariants",
                    "error",
                    f"component {cid} invariants must be an array",
                    f"{cpath}.invariants",
                )
            )
            raw_invariants = []
        invariants: list[InvariantDefinition] = []
        invariant_ids: set[str] = set()
        for invariant_index, raw_invariant in enumerate(raw_invariants):
            ipath = f"{cpath}.invariants[{invariant_index}]"
            if not isinstance(raw_invariant, dict):
                findings.append(
                    _finding(
                        "invalid-invariant", "error", "invariant must be a table", ipath
                    )
                )
                continue
            _unknown_findings(findings, raw_invariant, KNOWN_INVARIANT, ipath)
            iid = _string(raw_invariant.get("id")) or ""
            if not ID_RE.match(iid):
                findings.append(
                    _finding(
                        "invalid-invariant-id",
                        "error",
                        "invariant id must be kebab-case",
                        f"{ipath}.id",
                    )
                )
            elif iid in invariant_ids:
                findings.append(
                    _finding(
                        "duplicate-invariant-id",
                        "error",
                        f"duplicate invariant id '{iid}' within component '{cid}'",
                        f"{ipath}.id",
                    )
                )
            invariant_ids.add(iid)
            statement = _string(raw_invariant.get("statement")) or ""
            if not statement:
                findings.append(
                    _finding(
                        "missing-invariant-statement",
                        "error",
                        "invariant statement is required",
                        f"{ipath}.statement",
                    )
                )
            elif len(statement) > MAX_STATEMENT:
                findings.append(
                    _finding(
                        "long-invariant-statement",
                        "warning",
                        f"invariant statement should be <= {MAX_STATEMENT} chars",
                        f"{ipath}.statement",
                    )
                )
            evidence = _string_tuple(raw_invariant.get("evidence", []))
            if evidence is None:
                findings.append(
                    _finding(
                        "invalid-string-list",
                        "error",
                        "invariant evidence must be a string array",
                        f"{ipath}.evidence",
                    )
                )
                evidence = ()
            _validate_path_refs(
                repo_root,
                evidence,
                field_path=f"{ipath}.evidence",
                code="missing-evidence",
                findings=findings,
            )
            invariant_checks = _string_tuple(raw_invariant.get("validation_checks", []))
            if invariant_checks is None:
                findings.append(
                    _finding(
                        "invalid-string-list",
                        "error",
                        "invariant validation_checks must be a string array",
                        f"{ipath}.validation_checks",
                    )
                )
                invariant_checks = ()
            for label in invariant_checks:
                if COMMANDISH_RE.search(label):
                    findings.append(
                        _finding(
                            "command-in-check-label",
                            "error",
                            "validation_checks must contain labels, not commands",
                            f"{ipath}.validation_checks",
                            check_label=label,
                        )
                    )
            invariants.append(
                InvariantDefinition(
                    id=iid,
                    statement=statement,
                    evidence=evidence,
                    validation_checks=invariant_checks,
                )
            )
        components.append(
            ComponentDefinition(
                id=cid,
                title=title,
                kind=kind,
                paths=paths,
                read_before_editing=read_before,
                validation_checks=checks,
                invariants=tuple(invariants),
            )
        )

    raw_relations = data.get("relations", [])
    if raw_relations is None:
        raw_relations = []
    if not isinstance(raw_relations, list):
        findings.append(
            _finding(
                "invalid-relations", "error", "relations must be an array", "relations"
            )
        )
        raw_relations = []
    relations: list[RelationDefinition] = []
    for relation_index, raw_relation in enumerate(raw_relations):
        rpath = f"relations[{relation_index}]"
        if not isinstance(raw_relation, dict):
            findings.append(
                _finding("invalid-relation", "error", "relation must be a table", rpath)
            )
            continue
        _unknown_findings(findings, raw_relation, KNOWN_RELATION, rpath)
        from_component = _string(raw_relation.get("from")) or ""
        to_component = _string(raw_relation.get("to")) or ""
        kind = _string(raw_relation.get("kind")) or ""
        rule = _string(raw_relation.get("rule")) or ""
        for key, value in (
            ("from", from_component),
            ("to", to_component),
            ("kind", kind),
            ("rule", rule),
        ):
            if not value:
                findings.append(
                    _finding(
                        "missing-relation-field",
                        "error",
                        f"relation {key} is required",
                        f"{rpath}.{key}",
                    )
                )
        for key, endpoint in (("from", from_component), ("to", to_component)):
            if endpoint and endpoint not in component_ids:
                findings.append(
                    _finding(
                        "unknown-relation-endpoint",
                        "error",
                        f"relation {key} references unknown component '{endpoint}'",
                        f"{rpath}.{key}",
                    )
                )
        if len(rule) > MAX_RULE:
            findings.append(
                _finding(
                    "long-relation-rule",
                    "warning",
                    f"relation rule should be <= {MAX_RULE} chars",
                    f"{rpath}.rule",
                )
            )
        relations.append(
            RelationDefinition(
                from_component=from_component,
                to_component=to_component,
                kind=kind,
                rule=rule,
            )
        )

    system_map = SystemMap(
        version=cast(int, version) if isinstance(version, int) else 0,
        system=system,
        components=tuple(components),
        relations=tuple(relations),
    )
    return SystemMapLoadResult(path=str(path), map=system_map, findings=tuple(findings))
