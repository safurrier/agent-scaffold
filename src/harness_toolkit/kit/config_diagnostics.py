"""Deterministic config diagnostics for Harness Kit."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

from harness_toolkit.kit.profiles import ProfileCatalog, ProfileError, ProfileName
from harness_toolkit.kit.profiles.config import default_config_path
from harness_toolkit.kit.profiles.models import ProfileCheckView, ProfileResolution
from harness_toolkit.kit.profiles.resolution import resolve_target_system_map
from harness_toolkit.kit.state.repo import git_root
from harness_toolkit.kit.system_map import load_system_map
from harness_toolkit.kit.system_map.serialization import summary_from_load_result
from harness_toolkit.kit.system_map.validation import check_label_findings

ConfigFindingSeverity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class ConfigFinding:
    code: str
    severity: ConfigFindingSeverity
    message: str
    path: str | None = None
    field_path: str | None = None
    related_path: str | None = None
    check_label: str | None = None


@dataclass(frozen=True)
class ConfigInspectResult:
    config_path: str
    config_exists: bool
    target: str
    repo_root: str
    profile_count: int
    resolution: ProfileResolution | None
    system_map: dict[str, object] | None
    findings: tuple[ConfigFinding, ...] = ()


@dataclass(frozen=True)
class ConfigValidateResult:
    target: str
    repo_root: str
    ok: bool
    findings: tuple[ConfigFinding, ...]
    inspect: ConfigInspectResult | None = None


@dataclass(frozen=True)
class ConfigExplainResult:
    target: str
    repo_root: str
    profile: ProfileName
    source_engine: str
    paths: tuple[str, ...]
    checks: tuple[dict[str, object], ...]
    reviews: tuple[dict[str, object], ...]
    system_context: dict[str, object] | None
    resolution: ProfileResolution | None = None
    findings: tuple[ConfigFinding, ...] = ()


@dataclass(frozen=True)
class ConfigAuditResult:
    target: str
    repo_root: str
    ok: bool
    findings: tuple[ConfigFinding, ...]
    inspect: ConfigInspectResult | None = None


def _finding_from_exception(exc: Exception) -> ConfigFinding:
    return ConfigFinding(
        code="profile-config-error",
        severity="error",
        message=str(exc),
    )


def _system_map_summary_dict(
    catalog: ProfileCatalog, target: Path, repo_root: Path
) -> dict[str, object] | None:
    configured_map = resolve_target_system_map(target, config=catalog.config)
    result = load_system_map(repo_root, configured_path=configured_map)
    if result is None:
        return None
    summary = asdict(summary_from_load_result(result, repo_root=repo_root))
    summary["findings"] = [asdict(finding) for finding in result.findings]
    return summary


def _resolve_target(target: Path) -> tuple[Path, Path]:
    resolved_target = target.resolve(strict=False)
    return resolved_target, git_root(resolved_target)


def inspect_config(
    target: Path, *, profiles_dir: Path | None = None
) -> ConfigInspectResult:
    resolved_target, repo_root = _resolve_target(target)
    findings: list[ConfigFinding] = []
    config_path = default_config_path()
    try:
        catalog = ProfileCatalog.load(profiles_dir)
        resolution = catalog.resolve(resolved_target)
        system_map = _system_map_summary_dict(catalog, resolved_target, repo_root)
    except (ProfileError, KeyError) as exc:
        findings.append(_finding_from_exception(exc))
        return ConfigInspectResult(
            config_path=str(config_path),
            config_exists=config_path.exists(),
            target=str(resolved_target),
            repo_root=str(repo_root),
            profile_count=0,
            resolution=None,
            system_map=None,
            findings=tuple(findings),
        )
    return ConfigInspectResult(
        config_path=str(config_path),
        config_exists=config_path.exists(),
        target=str(resolved_target),
        repo_root=str(repo_root),
        profile_count=len(catalog.profiles),
        resolution=resolution,
        system_map=system_map,
        findings=tuple(findings),
    )


def _config_reference_findings(catalog: ProfileCatalog) -> tuple[ConfigFinding, ...]:
    findings: list[ConfigFinding] = []
    config = catalog.config
    if config is None:
        return ()
    if config.default_profile not in catalog.profiles:
        findings.append(
            ConfigFinding(
                code="missing-default-profile",
                severity="error",
                message=f"default_profile references unknown profile: {config.default_profile}",
                field_path="default_profile",
            )
        )
    for profiles_dir in config.profiles_dirs:
        path = Path(profiles_dir)
        if not path.exists():
            findings.append(
                ConfigFinding(
                    code="missing-profiles-dir",
                    severity="error",
                    message=f"configured profiles directory does not exist: {path}",
                    path=str(path),
                    field_path="profiles_dirs",
                )
            )
        elif not path.is_dir():
            findings.append(
                ConfigFinding(
                    code="profiles-path-not-directory",
                    severity="error",
                    message=f"configured profiles path is not a directory: {path}",
                    path=str(path),
                    field_path="profiles_dirs",
                )
            )
    for target in config.targets:
        target_path = Path(target.path)
        if not target_path.exists():
            findings.append(
                ConfigFinding(
                    code="missing-target-path",
                    severity="error",
                    message=f"configured target path does not exist: {target.path}",
                    path=target.path,
                    field_path=f"targets.{target.name}.path",
                )
            )
        if target.profile not in catalog.profiles:
            findings.append(
                ConfigFinding(
                    code="missing-target-profile",
                    severity="error",
                    message=f"target {target.name} references unknown profile: {target.profile}",
                    field_path=f"targets.{target.name}.profile",
                )
            )
        if target.system_map is not None and not Path(target.system_map).exists():
            findings.append(
                ConfigFinding(
                    code="missing-target-system-map",
                    severity="error",
                    message=f"target {target.name} references missing system map: {target.system_map}",
                    path=target.system_map,
                    field_path=f"targets.{target.name}.system_map",
                )
            )
    return tuple(findings)


def _system_map_findings(
    catalog: ProfileCatalog,
    target: Path,
    repo_root: Path,
    *,
    profile: ProfileName | None = None,
    strict_labels: bool = False,
) -> tuple[ConfigFinding, ...]:
    findings: list[ConfigFinding] = []
    selected_profile = profile or catalog.resolve(target).profile
    configured_map = resolve_target_system_map(target, config=catalog.config)
    result = load_system_map(repo_root, configured_path=configured_map)
    if result is None:
        return ()
    for finding in result.findings:
        findings.append(
            ConfigFinding(
                code=finding.code,
                severity=finding.severity,
                message=finding.message,
                path=result.path,
                field_path=finding.field_path,
                related_path=finding.related_path,
                check_label=finding.check_label,
            )
        )
    if result.map is None:
        return tuple(findings)
    known_labels: set[str] | None = None
    loaded = catalog.profiles.get(selected_profile)
    if loaded is not None:
        known_labels = {check.name for check in loaded.profile.checks}
    for finding in check_label_findings(
        result.map,
        known_check_labels=known_labels,
        strict_profile=strict_labels,
    ):
        findings.append(
            ConfigFinding(
                code=finding.code,
                severity=finding.severity,
                message=finding.message,
                path=result.path,
                field_path=finding.field_path,
                related_path=finding.related_path,
                check_label=finding.check_label,
            )
        )
    return tuple(findings)


def validate_config(
    target: Path,
    *,
    profile: ProfileName | None = None,
    profiles_dir: Path | None = None,
    strict_labels: bool = False,
) -> ConfigValidateResult:
    resolved_target, repo_root = _resolve_target(target)
    findings: list[ConfigFinding] = []
    try:
        catalog = ProfileCatalog.load(profiles_dir)
        inspect = inspect_config(resolved_target, profiles_dir=profiles_dir)
        if profile is not None and profile not in catalog.profiles:
            findings.append(
                ConfigFinding(
                    code="unknown-profile",
                    severity="error",
                    message=f"unknown profile: {profile}",
                    field_path="profile",
                )
            )
        findings.extend(_config_reference_findings(catalog))
        findings.extend(
            _system_map_findings(
                catalog,
                resolved_target,
                repo_root,
                profile=profile,
                strict_labels=strict_labels,
            )
        )
    except (ProfileError, KeyError) as exc:
        findings.append(_finding_from_exception(exc))
        inspect = None
    ok = not any(finding.severity == "error" for finding in findings)
    return ConfigValidateResult(
        target=str(resolved_target),
        repo_root=str(repo_root),
        ok=ok,
        findings=tuple(findings),
        inspect=inspect,
    )


def _repo_relative_path(path: str, *, repo_root: Path) -> str:
    candidate = Path(path).expanduser()
    if candidate.is_absolute():
        try:
            return (
                candidate.resolve(strict=False)
                .relative_to(repo_root.resolve(strict=False))
                .as_posix()
            )
        except ValueError:
            return candidate.as_posix()
    clean = path.strip().replace("\\", "/")
    while clean.startswith("./"):
        clean = clean[2:]
    return clean.strip("/")


def explain_config(
    target: Path,
    *,
    profile: ProfileName | None = None,
    profiles_dir: Path | None = None,
    changed_paths: tuple[str, ...] = (),
) -> ConfigExplainResult:
    resolved_target, repo_root = _resolve_target(target)
    findings: list[ConfigFinding] = []
    catalog = ProfileCatalog.load(profiles_dir)
    resolution = catalog.resolve(resolved_target)
    selected_profile = profile or resolution.profile
    normalized_paths = tuple(
        dict.fromkeys(
            _repo_relative_path(path, repo_root=repo_root)
            for path in changed_paths
            if path.strip()
        )
    )
    view: ProfileCheckView = catalog.checks_view(
        selected_profile,
        target=resolved_target,
        repo_root=repo_root,
        changed_paths=normalized_paths,
        enforce_required=profile is None and profiles_dir is None,
    )
    return ConfigExplainResult(
        target=str(resolved_target),
        repo_root=str(repo_root),
        profile=view.profile,
        source_engine="profile-checks-view",
        paths=view.changed_paths,
        checks=tuple(asdict(item) for item in view.suggested_checks),
        reviews=tuple(asdict(item) for item in view.suggested_reviews),
        system_context=asdict(view.system_context) if view.system_context else None,
        resolution=resolution,
        findings=tuple(findings),
    )


def audit_config(
    target: Path,
    *,
    profile: ProfileName | None = None,
    profiles_dir: Path | None = None,
) -> ConfigAuditResult:
    validation = validate_config(
        target,
        profile=profile,
        profiles_dir=profiles_dir,
        strict_labels=False,
    )
    findings = list(validation.findings)
    inspect = validation.inspect
    if (
        inspect is not None
        and inspect.system_map
        and inspect.system_map.get("overrides")
    ):
        findings.append(
            ConfigFinding(
                code="system-map-overrides-repo-local",
                severity="info",
                message=(
                    "target-level system map overrides repo-local "
                    f"{inspect.system_map['overrides']}"
                ),
                path=str(inspect.system_map.get("path")),
            )
        )
    return ConfigAuditResult(
        target=validation.target,
        repo_root=validation.repo_root,
        ok=not any(finding.severity == "error" for finding in findings),
        findings=tuple(findings),
        inspect=inspect,
    )
