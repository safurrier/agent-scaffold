"""Application-level Harness Kit lifecycle operations.

This module is the deep lifecycle seam used by CLI adapters and future tests.
The lower-level modules still own storage, capture, rendering, and specs while
this facade keeps command orchestration in one place.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from harness_toolkit.kit import local

EvidenceKind = Literal["test", "lint", "typecheck", "build", "check", "e2e", "other"]


@dataclass(frozen=True)
class TargetRequest:
    target: Path
    no_local_files: bool = False


@dataclass(frozen=True)
class StartRequest(TargetRequest):
    slug: str = ""
    plan: str = ""
    context: str = ""


@dataclass(frozen=True)
class NoteRequest(TargetRequest):
    kind: str = "learning"
    text: str = ""


@dataclass(frozen=True)
class SyncRequest(TargetRequest):
    check: bool = False
    exclude_paths: tuple[Path, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class CaptureRequest(TargetRequest):
    command: tuple[str, ...] = ()
    shell_command: str = ""
    kind: EvidenceKind = "other"
    why: str = ""
    check_name: str = ""
    no_log: bool = False
    raw_log: bool = False
    stream_to_stderr: bool = False
    timeout_seconds: int = 0
    max_log_bytes: int = 0


@dataclass(frozen=True)
class ArtifactAttachRequest(TargetRequest):
    path: Path = Path("")
    kind: str = ""
    label: str = ""
    redaction: str = "unknown"
    copy: bool = True


@dataclass(frozen=True)
class ReviewRequest(TargetRequest):
    backend: str = ""
    reviewer: str = ""
    rubrics: tuple[str, ...] = ()
    summary: str = ""
    disposition: str = "accepted"
    review_name: str = ""


@dataclass(frozen=True)
class DangerousSkipRequest(TargetRequest):
    check: str = ""
    label: str = ""
    reason: str = ""
    mitigation: str = ""


@dataclass(frozen=True)
class HandoffRequest(TargetRequest):
    output_path: Path | None = None
    format: Literal["markdown", "pr"] = "markdown"


@dataclass(frozen=True)
class ExportRequest(TargetRequest):
    format: Literal["handoff", "handoff-dir"] = "handoff"
    output_path: Path | None = None
    check: bool = False


def _work_started_slug(work_dir: Path) -> str:
    for event in local.read_events(work_dir):
        if event.type == "work_started":
            return str(event.data.get("slug", ""))
    return ""


def _note_exists(work_dir: Path, *, kind: str, text: str) -> bool:
    return any(
        event.type == "note_added"
        and event.data.get("kind") == kind
        and event.data.get("text") == text
        for event in local.read_events(work_dir)
    )


class LifecycleApp:
    """Deep Harness Kit lifecycle Module over local state primitives."""

    def init(self, request: TargetRequest) -> local.InitResult:
        return local.init_state(request.target, no_local_files=request.no_local_files)

    def start(self, request: StartRequest) -> local.WorkResult:
        slug = local.validate_slug(request.slug)
        state = local.ensure_state(
            request.target, no_local_files=request.no_local_files
        )
        active_work = local.active_work_dir(state)
        if active_work is not None and _work_started_slug(active_work) == slug:
            for kind, text in (
                ("plan", request.plan.strip()),
                ("context", request.context.strip()),
            ):
                if text and not _note_exists(active_work, kind=kind, text=text):
                    local.add_note(
                        request.target,
                        kind=kind,
                        text=text,
                        no_local_files=request.no_local_files,
                    )
            return local.WorkResult(
                work_id=active_work.name,
                work_dir=str(active_work),
                state_dir=str(state.state_dir),
                resumed=True,
            )

        result = local.create_work(
            request.target,
            slug,
            no_local_files=request.no_local_files,
        )
        if request.plan.strip():
            local.add_note(
                request.target,
                kind="plan",
                text=request.plan.strip(),
                no_local_files=request.no_local_files,
            )
        if request.context.strip():
            local.add_note(
                request.target,
                kind="context",
                text=request.context.strip(),
                no_local_files=request.no_local_files,
            )
        return result

    def note(self, request: NoteRequest) -> local.NoteResult:
        return local.add_note(
            request.target,
            kind=request.kind,
            text=request.text,
            no_local_files=request.no_local_files,
        )

    def sync(self, request: SyncRequest) -> local.SyncResult:
        return local.sync_checkpoint(
            request.target,
            check=request.check,
            exclude_paths=request.exclude_paths,
            reason=request.reason,
            no_local_files=request.no_local_files,
        )

    def capture(self, request: CaptureRequest) -> local.CaptureResult:
        return local.capture_command(
            request.target,
            request.command,
            shell_command=request.shell_command,
            kind=request.kind,
            why=request.why,
            check_name=request.check_name,
            no_log=request.no_log,
            raw_log=request.raw_log,
            no_local_files=request.no_local_files,
            stream_to_stderr=request.stream_to_stderr,
            timeout_seconds=request.timeout_seconds,
            max_log_bytes=request.max_log_bytes,
        )

    def attach_artifact(self, request: ArtifactAttachRequest) -> local.ArtifactResult:
        return local.attach_artifact(
            request.target,
            source_path=request.path,
            kind=request.kind,
            label=request.label,
            redaction=request.redaction,
            copy=request.copy,
            no_local_files=request.no_local_files,
        )

    def add_review(self, request: ReviewRequest) -> local.ReviewResult:
        return local.add_review(
            request.target,
            backend=request.backend,
            reviewer=request.reviewer,
            rubrics=request.rubrics,
            summary=request.summary,
            disposition=request.disposition,
            review_name=request.review_name,
            no_local_files=request.no_local_files,
        )

    def review_prompt(
        self, request: TargetRequest, *, review_name: str = ""
    ) -> local.ReviewPromptResult:
        return local.review_prompt(
            request.target,
            review_name=review_name,
            no_local_files=request.no_local_files,
        )

    def dangerously_skip(
        self, request: DangerousSkipRequest
    ) -> local.DangerousSkipResult:
        return local.add_dangerous_skip(
            request.target,
            check=request.check,
            label=request.label,
            reason=request.reason,
            mitigation=request.mitigation,
            no_local_files=request.no_local_files,
        )

    def ready(self, request: TargetRequest) -> local.ReadyResult:
        return local.ready(request.target, no_local_files=request.no_local_files)

    def status(self, request: TargetRequest) -> local.StatusResult:
        return local.status(request.target, no_local_files=request.no_local_files)

    def materialize(self, request: TargetRequest) -> local.HandoffResult:
        return local.materialize_work(
            request.target, no_local_files=request.no_local_files
        )

    def export(
        self, request: ExportRequest
    ) -> local.HandoffResult | local.ExportResult:
        if request.format == "handoff":
            return local.materialize_work(
                request.target, no_local_files=request.no_local_files
            )
        return local.export_handoff_dir(
            request.target,
            output_path=request.output_path,
            check=request.check,
            no_local_files=request.no_local_files,
        )

    def handoff(self, request: HandoffRequest) -> local.HandoffResult:
        return local.handoff(
            request.target,
            output_path=request.output_path,
            no_local_files=request.no_local_files,
            format=request.format,
        )

    def summary(self, request: TargetRequest) -> local.HandoffResult:
        return local.summary(request.target, no_local_files=request.no_local_files)

    def spec_init(self, request: TargetRequest) -> local.SpecResult:
        return local.init_spec(request.target, no_local_files=request.no_local_files)

    def spec_status(self, request: TargetRequest) -> local.SpecResult:
        return local.spec_status(request.target, no_local_files=request.no_local_files)

    def spec_outline(self, request: TargetRequest) -> local.SpecOutline:
        return local.spec_outline(request.target, no_local_files=request.no_local_files)

    def spec_promote_dry_run(self, request: TargetRequest) -> str:
        return local.spec_promote_dry_run(
            request.target, no_local_files=request.no_local_files
        )
