"""Typed closeout diagnostics for ``hk status``.

Readiness policy stays binary. This module builds agent-facing freshness facts that
explain why validation or review evidence is fresh or stale for current paths.
"""

from __future__ import annotations

import shlex
from dataclasses import dataclass

from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.readiness.policy import (
    RequiredProfileItem,
    accepted_review_events,
    dangerous_skip_for_label,
)


@dataclass(frozen=True)
class PathDecisionHint:
    source_risk: str
    accidental: str
    local_only: str


@dataclass(frozen=True)
class EvidenceFreshnessItem:
    kind: str
    label: str
    total: int
    accepted_or_passing: int
    latest_status: str
    latest_at: str
    fresh: bool
    covered_paths: list[str]
    uncovered_paths: list[str]
    scope: str = "generic"
    required: bool = False
    readiness_blocker: bool = False
    next_action: str = ""
    path_decision_hint: PathDecisionHint | None = None


@dataclass(frozen=True)
class ExportFreshnessNote:
    fresh_neutral_paths: list[str]
    check_command: str
    message: str


def _fresh_diff_hash(diff_hash: str, current_diff_hashes: tuple[str, ...]) -> bool:
    return not current_diff_hashes or diff_hash in {
        item for item in current_diff_hashes if item
    }


def _path_hash_payload(value: object) -> dict[str, str] | None:
    if not isinstance(value, dict):
        return None
    if not all(
        isinstance(item_key, str) and isinstance(item_value, str)
        for item_key, item_value in value.items()
    ):
        return None
    return {str(item_key): str(item_value) for item_key, item_value in value.items()}


def _hash_covered_paths(
    records: list[dict[str, str]],
    paths: tuple[str, ...],
    current_hashes: dict[str, str],
) -> tuple[list[str], list[str]]:
    covered: list[str] = []
    uncovered: list[str] = []
    for path in paths:
        current_hash = current_hashes.get(path, "")
        if current_hash and any(record.get(path) == current_hash for record in records):
            covered.append(path)
        else:
            uncovered.append(path)
    return covered, uncovered


def _path_flags(paths: list[str]) -> str:
    return " ".join(f"--path {shlex.quote(path)}" for path in paths)


def _sync_exclude_flags(paths: list[str]) -> str:
    return " ".join(f"--exclude {shlex.quote(path)}" for path in paths)


def _path_decision_hint(
    *, kind: str, paths: list[str], check_name: str = "", review_name: str = ""
) -> PathDecisionHint | None:
    if not paths:
        return None
    if kind == "validation" and check_name:
        source_risk = (
            f"validate source-risk paths and record with `hk validate --check {check_name} "
            "--why '...' -- <native command>`"
        )
    elif kind == "validation":
        source_risk = (
            "validate source-risk paths and record with `hk validate --why '...' "
            "-- <native command>`"
        )
    elif review_name:
        source_risk = (
            f"record targeted review for source-risk paths with `hk review add --review {review_name} "
            + _path_flags(paths)
            + " --backend subagent --reviewer reviewer-fresh-context --summary '...'`"
        )
    else:
        source_risk = (
            "record targeted review for source-risk paths with `hk review add "
            + _path_flags(paths)
            + " --backend subagent --reviewer reviewer-fresh-context --summary '...'`"
        )
    return PathDecisionHint(
        source_risk=source_risk,
        accidental="remove accidental tool output paths, then rerun `hk status`",
        local_only="for only the paths you judge local-only, record an explicit exclusion with `hk sync --exclude PATH --reason 'local-only tool output'`",
    )


def build_evidence_freshness_items(
    *,
    work_id: str,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    current_paths: tuple[str, ...],
    current_path_hashes: dict[str, str],
    current_diff_hashes: tuple[str, ...],
    required_checks: tuple[RequiredProfileItem, ...],
    required_reviews: tuple[RequiredProfileItem, ...],
) -> list[EvidenceFreshnessItem]:
    items: list[EvidenceFreshnessItem] = []
    passing_with_why = [
        record for record in evidence if record.why and record.status == "pass"
    ]
    all_with_why = [record for record in evidence if record.why]
    exact_validation_fresh = any(
        _fresh_diff_hash(record.diff_hash, current_diff_hashes)
        for record in passing_with_why
    )
    validation_hash_records = [
        record.changed_path_hashes
        for record in passing_with_why
        if isinstance(record.changed_path_hashes, dict)
    ]
    validation_covered, validation_uncovered = _hash_covered_paths(
        validation_hash_records, current_paths, current_path_hashes
    )
    validation_fresh = bool(passing_with_why) and (
        exact_validation_fresh or not validation_uncovered
    )
    latest_validation = max((record.ended_at for record in all_with_why), default="")
    if all_with_why or current_paths:
        items.append(
            EvidenceFreshnessItem(
                kind="validation",
                label="general",
                total=len(all_with_why),
                accepted_or_passing=len(passing_with_why),
                latest_status=all_with_why[-1].status if all_with_why else "missing",
                latest_at=latest_validation,
                fresh=validation_fresh,
                covered_paths=list(
                    current_paths if exact_validation_fresh else validation_covered
                ),
                uncovered_paths=[] if exact_validation_fresh else validation_uncovered,
                scope="generic",
                required=False,
                readiness_blocker=False,
                next_action="hk validate --why '...' -- <native command>"
                if not validation_fresh
                else "",
                path_decision_hint=_path_decision_hint(
                    kind="validation", paths=validation_uncovered
                ),
            )
        )

    for item in required_checks:
        named_records = [
            record for record in evidence if record.check_name == item.name
        ]
        named_passing = [record for record in named_records if record.status == "pass"]
        exact_fresh = any(
            _fresh_diff_hash(record.diff_hash, current_diff_hashes)
            for record in named_passing
        )
        hash_records = [
            record.changed_path_hashes
            for record in named_passing
            if isinstance(record.changed_path_hashes, dict)
        ]
        item_paths = tuple(
            path
            for path in item.matched_paths
            if not path.startswith(f".ai/hk/{work_id}/")
        )
        covered, uncovered = _hash_covered_paths(
            hash_records, item_paths, current_path_hashes
        )
        matching_skips = dangerous_skip_for_label(
            events, "validation", item.name, current_diff_hashes=current_diff_hashes
        )
        fresh = bool(matching_skips) or (
            bool(named_passing) and (exact_fresh or not uncovered)
        )
        items.append(
            EvidenceFreshnessItem(
                kind="validation",
                label=item.name,
                total=len(named_records),
                accepted_or_passing=len(named_passing),
                latest_status="skipped"
                if matching_skips
                else named_records[-1].status
                if named_records
                else "missing",
                latest_at=max(
                    (record.ended_at for record in named_records), default=""
                ),
                fresh=fresh,
                covered_paths=list(
                    item_paths if exact_fresh or matching_skips else covered
                ),
                uncovered_paths=[] if exact_fresh or matching_skips else uncovered,
                scope="profile",
                required=True,
                readiness_blocker=not fresh,
                next_action=f"hk validate --check {item.name} --why '...' -- <native command>"
                if not fresh
                else "",
                path_decision_hint=_path_decision_hint(
                    kind="validation", paths=uncovered, check_name=item.name
                ),
            )
        )

    accepted_reviews = accepted_review_events(events, require_current_hash=False)
    typed_review_hash_records = [
        hashes
        for review in accepted_reviews
        if (hashes := _path_hash_payload(review.get("changed_path_hashes"))) is not None
    ]
    exact_review_fresh = any(
        _fresh_diff_hash(str(review.get("diff_hash") or ""), current_diff_hashes)
        for review in accepted_reviews
    )
    review_covered, review_uncovered = _hash_covered_paths(
        typed_review_hash_records, current_paths, current_path_hashes
    )
    review_fresh = bool(accepted_reviews) and (
        exact_review_fresh or not review_uncovered
    )
    review_events = [event for event in events if event.type == "review_added"]
    if review_events or current_paths:
        items.append(
            EvidenceFreshnessItem(
                kind="review",
                label="general",
                total=len(review_events),
                accepted_or_passing=len(accepted_reviews),
                latest_status=str(
                    review_events[-1].data.get("disposition") or "missing"
                )
                if review_events
                else "missing",
                latest_at=review_events[-1].at if review_events else "",
                fresh=review_fresh,
                covered_paths=list(
                    current_paths if exact_review_fresh else review_covered
                ),
                uncovered_paths=[] if exact_review_fresh else review_uncovered,
                scope="generic",
                required=False,
                readiness_blocker=False,
                next_action="hk review add "
                + _path_flags(review_uncovered)
                + " --backend subagent --reviewer reviewer-fresh-context --summary '...'"
                if accepted_reviews and review_uncovered
                else "hk review prompt"
                if not review_fresh
                else "",
                path_decision_hint=_path_decision_hint(
                    kind="review", paths=review_uncovered
                ),
            )
        )

    for item in required_reviews:
        named_reviews = [
            review
            for review in accepted_reviews
            if str(review.get("review_name") or "") == item.name
        ]
        named_review_events = [
            event
            for event in review_events
            if str(event.data.get("review_name") or "") == item.name
        ]
        exact_fresh = any(
            _fresh_diff_hash(str(review.get("diff_hash") or ""), current_diff_hashes)
            for review in named_reviews
        )
        hash_records = [
            hashes
            for review in named_reviews
            if (hashes := _path_hash_payload(review.get("changed_path_hashes")))
            is not None
        ]
        item_paths = tuple(
            path
            for path in item.matched_paths
            if not path.startswith(f".ai/hk/{work_id}/")
        )
        covered, uncovered = _hash_covered_paths(
            hash_records, item_paths, current_path_hashes
        )
        matching_skips = dangerous_skip_for_label(
            events, "review", item.name, current_diff_hashes=current_diff_hashes
        )
        fresh = bool(matching_skips) or (
            bool(named_reviews) and (exact_fresh or not uncovered)
        )
        items.append(
            EvidenceFreshnessItem(
                kind="review",
                label=item.name,
                total=len(named_review_events),
                accepted_or_passing=len(named_reviews),
                latest_status="skipped"
                if matching_skips
                else str(named_review_events[-1].data.get("disposition") or "missing")
                if named_review_events
                else "missing",
                latest_at=named_review_events[-1].at if named_review_events else "",
                fresh=fresh,
                covered_paths=list(
                    item_paths if exact_fresh or matching_skips else covered
                ),
                uncovered_paths=[] if exact_fresh or matching_skips else uncovered,
                scope="profile",
                required=True,
                readiness_blocker=not fresh,
                next_action=f"hk review prompt {item.name}; hk review add --review {item.name} "
                + _path_flags(uncovered)
                + " --backend subagent --reviewer reviewer-fresh-context --summary '...'"
                if not fresh
                else "",
                path_decision_hint=_path_decision_hint(
                    kind="review", paths=uncovered, review_name=item.name
                ),
            )
        )
    return items


def build_export_freshness_note(
    *, work_id: str, target_root: str, all_changed_paths: tuple[str, ...]
) -> ExportFreshnessNote | None:
    active_prefix = f".ai/hk/{work_id}"
    active_paths = [
        path
        for path in all_changed_paths
        if path == active_prefix or path.startswith(f"{active_prefix}/")
    ]
    if not active_paths:
        return None
    return ExportFreshnessNote(
        fresh_neutral_paths=active_paths,
        check_command="hk export --format handoff-dir --output "
        + shlex.quote(f"{target_root}/{active_prefix}")
        + " --check --target "
        + shlex.quote(target_root),
        message="active HK export paths are ignored by validation/review freshness; validate the generated export separately with the export check command",
    )
