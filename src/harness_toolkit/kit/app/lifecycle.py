"""Application-level HK2 lifecycle operations.

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
    no_log: bool = False
    raw_log: bool = False
    stream_to_stderr: bool = False


@dataclass(frozen=True)
class ReviewRequest(TargetRequest):
    backend: str = ""
    reviewer: str = ""
    rubrics: tuple[str, ...] = ()
    summary: str = ""
    disposition: str = "accepted"


@dataclass(frozen=True)
class DangerousSkipRequest(TargetRequest):
    check: str = ""
    reason: str = ""


@dataclass(frozen=True)
class HandoffRequest(TargetRequest):
    output_path: Path | None = None


class LifecycleApp:
    """Deep HK2 lifecycle Module over local state primitives."""

    def init(self, request: TargetRequest) -> local.InitResult:
        return local.init_state(request.target, no_local_files=request.no_local_files)

    def start(self, request: StartRequest) -> local.WorkResult:
        result = local.create_work(
            request.target,
            request.slug,
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
            no_log=request.no_log,
            raw_log=request.raw_log,
            no_local_files=request.no_local_files,
            stream_to_stderr=request.stream_to_stderr,
        )

    def add_review(self, request: ReviewRequest) -> local.ReviewResult:
        return local.add_review(
            request.target,
            backend=request.backend,
            reviewer=request.reviewer,
            rubrics=request.rubrics,
            summary=request.summary,
            disposition=request.disposition,
            no_local_files=request.no_local_files,
        )

    def review_prompt(self, request: TargetRequest) -> local.ReviewPromptResult:
        return local.review_prompt(
            request.target, no_local_files=request.no_local_files
        )

    def dangerously_skip(self, request: DangerousSkipRequest) -> local.NoteResult:
        return local.add_dangerous_skip(
            request.target,
            check=request.check,
            reason=request.reason,
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

    def handoff(self, request: HandoffRequest) -> local.HandoffResult:
        return local.handoff(
            request.target,
            output_path=request.output_path,
            no_local_files=request.no_local_files,
        )

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
