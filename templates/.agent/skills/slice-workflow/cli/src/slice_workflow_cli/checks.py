"""Contract check command logic for slice workflow."""

from __future__ import annotations

from pathlib import Path

from .contract import (
    PlanContext,
    PlanContractError,
    adr_dir,
    changed_plan_contexts,
    checklist_has_meaningful_items,
    extract_paths_from_bullets,
    file_has_meaningful_content,
    git_changed_paths,
    git_current_branch,
    git_diff_paths,
    git_path_is_ignored,
    git_path_is_tracked,
    in_progress_plan_contexts,
    is_placeholder_value,
    keyed_bullets,
    ledger_path,
    missing_required_plan_files,
    parse_artifact_manifest,
    plan_reference_present,
    resolve_plan_artifact_path,
    resolve_repo_path,
    section_bullets,
    section_has_meaningful_bullets,
    selected_plan_context,
    strip_changed_plan_paths,
    strip_plan_local_changes,
    validate_meta_yaml,
    validation_has_commands,
)
from .output import log_ok, log_step

CONTRACT_TASKS = ("plan-check", "spec-check", "evidence-check", "review-check")


class ContractCheckError(RuntimeError):
    """Expected contract check failure."""


def _selected(root: Path, plan_dir: str | None) -> tuple[PlanContext | None, bool]:
    args = ["--plan-dir", plan_dir] if plan_dir else []
    try:
        return selected_plan_context(root, args)
    except PlanContractError as e:
        raise ContractCheckError(str(e)) from e


def check_plan(root: Path, plan_dir: str | None = None) -> int:
    log_step("Checking plan contract")
    current, explicit_plan = _selected(root, plan_dir)

    meaningful_changes: list[str] = []
    if not explicit_plan:
        in_progress = in_progress_plan_contexts(root)
        if len(in_progress) > 1:
            lines = "\n".join(
                f"  - {ctx.path.relative_to(root)}" for ctx in in_progress
            )
            raise ContractCheckError(
                "Multiple plans are marked in-progress. Keep exactly one active slice."
                f"\n{lines}"
            )

        try:
            changed_paths = git_changed_paths(root)
        except PlanContractError as e:
            raise ContractCheckError(str(e)) from e
        meaningful_changes = strip_plan_local_changes(
            changed_paths, current.path if current else None, root
        )

    if current is None:
        if meaningful_changes:
            lines = "\n".join(f"  - {path}" for path in meaningful_changes)
            raise ContractCheckError(
                "Meaningful changes exist, but no active plan was found.\n" + lines
            )
        log_ok("No active plan and no meaningful changes")
        return 0

    missing = missing_required_plan_files(current.path)
    if missing:
        lines = "\n".join(f"  - {rel}" for rel in missing)
        raise ContractCheckError("Active plan is missing required files:\n" + lines)

    errors = validate_meta_yaml(current.meta)
    if errors:
        lines = "\n".join(f"  - {error}" for error in errors)
        raise ContractCheckError("META.yaml is incomplete:\n" + lines)

    branch = git_current_branch(root)
    if branch and current.meta.branch and current.meta.branch != branch:
        raise ContractCheckError(
            f"Plan branch '{current.meta.branch}' does not match current branch '{branch}'."
        )

    if not checklist_has_meaningful_items(current.path / "TODO.md"):
        raise ContractCheckError(
            "TODO.md must contain at least one meaningful checklist item."
        )

    if (
        not explicit_plan
        and meaningful_changes
        and current.meta.status != "in-progress"
    ):
        raise ContractCheckError(
            "Meaningful changes require the active plan status to be 'in-progress'."
        )

    if current.meta.status in {
        "in-progress",
        "complete",
    } and not file_has_meaningful_content(current.path / "LEARNING_LOG.md"):
        raise ContractCheckError(
            "LEARNING_LOG.md should record at least one in-progress note once work starts."
        )

    log_ok(f"Plan contract ready: {current.path.relative_to(root)}")
    return 0


def check_spec(root: Path, plan_dir: str | None = None) -> int:
    log_step("Checking spec and decision contract")
    current, _explicit_plan = _selected(root, plan_dir)
    if current is None:
        log_ok("No active plan to spec-check")
        return 0

    decisions_file = current.path / "DECISIONS.md"
    if not file_has_meaningful_content(decisions_file):
        raise ContractCheckError(
            "DECISIONS.md needs a real change summary before handoff."
        )

    for heading in ("What Changed", "Why"):
        if not section_has_meaningful_bullets(decisions_file, heading):
            raise ContractCheckError(
                f"DECISIONS.md is missing a meaningful '{heading}' section."
            )

    if current.meta.contract_change in {"docs_only", "contract_changed"}:
        reflected_paths = extract_paths_from_bullets(decisions_file, "Where Reflected")
        if not reflected_paths:
            raise ContractCheckError(
                "Docs or contract changes must list durable reflected paths in DECISIONS.md."
            )
        for raw_path in reflected_paths:
            target = resolve_repo_path(root, raw_path)
            if target is None:
                raise ContractCheckError(
                    f"Reflected path escapes the repository: {raw_path}"
                )
            if not target.exists():
                raise ContractCheckError(f"Reflected path does not exist: {raw_path}")

    if current.meta.decision_record == "ledger":
        active_ledger = ledger_path(root)
        if not active_ledger.exists():
            raise ContractCheckError("Decision ledger is missing.")
        if not plan_reference_present(
            active_ledger, current.path.name, current.meta.slug
        ):
            raise ContractCheckError(
                "Decision ledger must contain an entry referencing the active plan before sync-check passes."
            )

    if current.meta.decision_record == "adr":
        decisions_dir = adr_dir(root)
        adr_files = sorted(decisions_dir.glob("*.md")) if decisions_dir.exists() else []
        if not adr_files:
            raise ContractCheckError(
                "decision_record=adr requires an ADR under docs/explanation/decisions/."
            )
        if not any(
            plan_reference_present(path, current.path.name, current.meta.slug)
            for path in adr_files
        ):
            raise ContractCheckError(
                "No ADR references the active plan. Add or update an ADR before handoff."
            )

    log_ok(f"Spec contract ready: {current.path.relative_to(root)}")
    return 0


def check_evidence(root: Path, plan_dir: str | None = None) -> int:
    log_step("Checking evidence contract")
    current, _explicit_plan = _selected(root, plan_dir)
    if current is None:
        log_ok("No active plan to evidence-check")
        return 0

    validation_path = current.path / "VALIDATION.md"
    if not validation_has_commands(validation_path):
        raise ContractCheckError(
            "VALIDATION.md must contain real commands or captured verification output."
        )

    manifest_path = current.path / "artifacts" / "manifest.yaml"
    artifacts = parse_artifact_manifest(manifest_path)

    for artifact in artifacts:
        if not artifact.type:
            raise ContractCheckError(
                f"Artifact entry in {manifest_path.relative_to(root)} is missing a type."
            )
        if not artifact.path:
            raise ContractCheckError(
                f"Artifact entry in {manifest_path.relative_to(root)} is missing a path."
            )
        target = resolve_plan_artifact_path(current.path, artifact.path)
        if target is None:
            raise ContractCheckError(
                f"Artifact path escapes the active plan directory: {artifact.path}"
            )
        if not target.exists():
            raise ContractCheckError(
                f"Artifact path does not exist: {target.relative_to(root)}"
            )
        try:
            ignored = git_path_is_ignored(root, target)
            tracked = git_path_is_tracked(root, target)
        except PlanContractError as e:
            raise ContractCheckError(str(e)) from e
        if ignored:
            raise ContractCheckError(
                "Artifact path is ignored by git and will not survive CI checkout: "
                f"{target.relative_to(root)}"
            )
        if not tracked:
            raise ContractCheckError(
                "Artifact path is not tracked or staged for commit: "
                f"{target.relative_to(root)}"
            )

    for evidence_type in current.meta.evidence_required:
        if evidence_type == "commands":
            continue
        if not any(artifact.type == evidence_type for artifact in artifacts):
            raise ContractCheckError(
                f"Missing declared evidence type '{evidence_type}' in artifacts/manifest.yaml."
            )

    log_ok(f"Evidence contract ready: {current.path.relative_to(root)}")
    return 0


def check_review(root: Path, plan_dir: str | None = None) -> int:
    log_step("Checking review contract")
    current, _explicit_plan = _selected(root, plan_dir)
    if current is None:
        log_ok("No active plan to review-check")
        return 0

    review_path = current.path / "REVIEW.md"
    if not file_has_meaningful_content(review_path):
        raise ContractCheckError(
            "REVIEW.md must contain a completed review, not only placeholders."
        )

    context = keyed_bullets(review_path, "Review Context")
    mode = context.get("mode", "")
    backend = context.get("backend", "") or current.meta.review_backend
    reviewer = context.get("reviewer", "")

    if current.meta.review_mode == "external_required" and mode != "external":
        raise ContractCheckError(
            "REVIEW.md must record Mode: external when external review is required."
        )
    if not reviewer or is_placeholder_value(reviewer):
        raise ContractCheckError(
            "REVIEW.md must record the reviewer identity or external review context."
        )
    if not current.meta.review_backend or is_placeholder_value(
        current.meta.review_backend
    ):
        raise ContractCheckError(
            "META.yaml must record the backend that performed the review."
        )
    if not backend or backend.lower() == "self" or is_placeholder_value(backend):
        raise ContractCheckError(
            "An external review backend is required (subagent, skill, or manual_external)."
        )
    if current.meta.review_backend and current.meta.review_backend != backend:
        raise ContractCheckError("META.yaml review_backend does not match REVIEW.md.")

    rubrics = set(section_bullets(review_path, "Rubrics"))
    missing_rubrics = [
        name for name in current.meta.review_rubrics if name not in rubrics
    ]
    if missing_rubrics:
        lines = "\n".join(f"  - {rubric}" for rubric in missing_rubrics)
        raise ContractCheckError("REVIEW.md is missing rubric coverage for:\n" + lines)

    for heading in ("Findings", "Disposition"):
        if not section_has_meaningful_bullets(review_path, heading):
            raise ContractCheckError(
                f"REVIEW.md needs a meaningful '{heading}' section."
            )

    log_ok(f"Review contract ready: {current.path.relative_to(root)}")
    return 0


def run_contract_for_plan(root: Path, plan_dir: str) -> int:
    log_step(f"Checking plan: {plan_dir}")
    for task_name in CONTRACT_TASKS:
        run_check(root, task_name, plan_dir=plan_dir)
    return 0


def run_changed_plans(root: Path, refspec: str) -> int:
    try:
        contexts = changed_plan_contexts(root, refspec)
        changed_paths = git_diff_paths(root, refspec)
    except PlanContractError as e:
        raise ContractCheckError(str(e)) from e

    meaningful_paths = strip_changed_plan_paths(changed_paths, contexts, root)
    if not contexts:
        if meaningful_paths:
            lines = "\n".join(f"  - {path}" for path in meaningful_paths)
            raise ContractCheckError(
                "Meaningful branch changes exist, but no changed plan was found.\n"
                + lines
            )
        log_ok("No changed plans and no meaningful branch changes")
        return 0

    if meaningful_paths:
        log_step("Non-plan branch changes covered by changed plan validation")
        for path in meaningful_paths:
            print(f"  - {path}")

    for context in contexts:
        if context.meta.status != "complete":
            raise ContractCheckError(
                "Changed plans must be marked complete before PR sync-check passes: "
                f"{context.path.relative_to(root)}"
            )
        run_contract_for_plan(root, str(context.path.relative_to(root)))
    return 0


def run_check(root: Path, check_name: str, plan_dir: str | None = None) -> int:
    if check_name == "plan-check":
        return check_plan(root, plan_dir)
    if check_name == "spec-check":
        return check_spec(root, plan_dir)
    if check_name == "evidence-check":
        return check_evidence(root, plan_dir)
    if check_name == "review-check":
        return check_review(root, plan_dir)
    raise ContractCheckError(f"Unknown check: {check_name}")


def run_sync_check(
    root: Path,
    *,
    plan_dir: str | None = None,
    changed_plans: str | None = None,
) -> int:
    log_step("Running sync-check")
    if plan_dir and changed_plans:
        raise ContractCheckError("Use either --plan-dir or --changed-plans, not both.")
    if plan_dir:
        run_contract_for_plan(root, plan_dir)
    elif changed_plans:
        run_changed_plans(root, changed_plans)
    else:
        for task_name in CONTRACT_TASKS:
            run_check(root, task_name)
    log_ok("Sync-check passed")
    return 0
