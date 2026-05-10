"""Harness Kit local assistant primitives.

This module intentionally keeps the first lifecycle implementation small: repo brief,
local/external state, ledger-backed work units, sync checkpoints, command
capture, generated handoff/materialized views, and local specs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import stat
import subprocess
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from harness_toolkit.kit.capture.process import run_process_to_transcript
from harness_toolkit.kit.capture.redaction import redact_argv, redact_text
from harness_toolkit.kit.capture.transcripts import transcript_path
from harness_toolkit.kit.ledger.events import append_lifecycle_event
from harness_toolkit.kit.ledger.models import EventRecord, EvidenceRecord
from harness_toolkit.kit.ledger.store import (
    LedgerStoreError,
)
from harness_toolkit.kit.ledger.store import (
    next_seq as ledger_next_seq,
)
from harness_toolkit.kit.ledger.store import (
    read_events as ledger_read_events,
)
from harness_toolkit.kit.ledger.store import (
    read_evidence as ledger_read_evidence,
)
from harness_toolkit.kit.profiles import ProfileCatalog, ProfileError, profile_names
from harness_toolkit.kit.readiness.diagnostics import ReadyCheck, ReadyResult
from harness_toolkit.kit.readiness.policy import (
    SELF_REVIEW_GUIDANCE,
    RequiredProfileItem,
    dangerous_skip_events,
    dangerous_skip_message,
    is_self_review_identity,
    notes_by_kind,
    notes_by_kinds,
    ready_for_events,
)
from harness_toolkit.kit.readiness.policy import (
    lifecycle_phase as policy_lifecycle_phase,
)
from harness_toolkit.kit.rendering.handoff import (
    render_handoff_markdown,
    render_handoff_pr_markdown,
    render_summary_markdown,
)
from harness_toolkit.kit.rendering.materialize import write_note_views
from harness_toolkit.kit.rendering.review_prompt import render_review_prompt
from harness_toolkit.kit.specs.models import SpecOutline, SpecResult
from harness_toolkit.kit.specs.operations import (
    SpecWorkflowError,
    find_specs_for_state,
    init_spec_for_state,
    spec_outline_for_state,
    spec_promote_dry_run_for_state,
    spec_status_for_state,
)
from harness_toolkit.kit.state.repo import (
    RepoStateError,
    git_branch,
    git_root,
    repo_key,
)
from harness_toolkit.kit.state.repo import (
    scope_key as repo_scope_key,
)

LOCAL_STATE_DIR = ".harness-local"
KIT_STATE_DIR = "harness-kit"
STATE_SCHEMA_VERSION = 1
WORK_DIR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{6}-")
VALID_NOTE_KINDS = (
    "context",
    "plan",
    "background",
    "learning",
    "decision",
    "gap",
    "spec-impact",
)
VALID_EVIDENCE_KINDS = ("test", "lint", "typecheck", "build", "check", "e2e", "other")
SYNC_IGNORED_EVENT_TYPES = frozenset(
    {"sync_checkpoint", "view_materialized", "handoff_generated"}
)
COMMON_AGENT_LOCAL_STATE_PATHS = (".pi", ".claude/worktrees")
StateMode = Literal["local", "external"]
NoteKind = Literal[
    "context", "plan", "background", "learning", "decision", "gap", "spec-impact"
]
EvidenceKind = Literal["test", "lint", "typecheck", "build", "check", "e2e", "other"]
HandoffFormat = Literal["markdown", "pr"]


class LocalWorkflowError(RuntimeError):
    """Expected local assistant failure shown without traceback."""


@dataclass(frozen=True)
class LocalState:
    target_root: Path
    target_scope: Path
    state_dir: Path
    mode: StateMode
    scope: str
    repo_key: str


@dataclass(frozen=True)
class Brief:
    target_root: str
    target_scope: str
    branch: str
    git_sha: str
    dirty: bool
    state_dir: str
    state_exists: bool
    active_work: str
    sync_status: str
    agents_md: list[str]
    spec_sources: list[str]
    repo_surfaces: list[str]
    profiles: list[str]


@dataclass(frozen=True)
class InitResult:
    target_root: str
    target_scope: str
    state_dir: str
    mode: str
    ignored_by_local_git: bool


@dataclass(frozen=True)
class WorkResult:
    work_id: str
    work_dir: str
    state_dir: str
    resumed: bool = False


@dataclass(frozen=True)
class NoteResult:
    work_id: str
    seq: int
    kind: str
    text: str


@dataclass(frozen=True)
class DangerousSkipResult:
    work_id: str
    seq: int
    check: str
    label: str
    reason: str
    mitigation: str


@dataclass(frozen=True)
class SyncResult:
    work_id: str
    synced: bool
    message: str
    guidance: list[str]


@dataclass(frozen=True)
class CaptureResult:
    work_id: str
    evidence_id: str
    exit_code: int
    status: str
    transcript_path: str
    why: str = ""
    check_name: str = ""


@dataclass(frozen=True)
class ReviewResult:
    work_id: str
    seq: int
    backend: str
    reviewer: str
    rubrics: list[str]
    summary: str
    disposition: str
    review_name: str = ""


@dataclass(frozen=True)
class StatusResult:
    active_work: str
    target_root: str
    target_scope: str
    state_dir: str
    sync_status: str
    ready_status: str
    phase: str
    checks: list[ReadyCheck]
    next_actions: list[str]


@dataclass(frozen=True)
class ReviewPromptResult:
    work_id: str
    prompt: str


@dataclass(frozen=True)
class HandoffResult:
    work_id: str
    content: str
    path: str = ""


@dataclass(frozen=True)
class ExportResult:
    work_id: str
    path: str
    format: str
    checked: bool = False
    fresh: bool = True
    message: str = ""


@dataclass(frozen=True)
class ArtifactResult:
    work_id: str
    seq: int
    kind: str
    label: str
    source_path: str
    artifact_path: str
    sha256: str
    size_bytes: int
    copied: bool
    redaction: str


JsonDataclass = (
    Brief
    | InitResult
    | WorkResult
    | NoteResult
    | DangerousSkipResult
    | SyncResult
    | CaptureResult
    | ReviewResult
    | ReadyResult
    | StatusResult
    | ReviewPromptResult
    | SpecResult
    | SpecOutline
    | HandoffResult
    | ExportResult
    | ArtifactResult
)


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def default_state_home() -> Path:
    state_home = Path(
        os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    )
    return state_home / "harness-toolkit" / "repos"


def scope_key(target_root: Path, target_scope: Path) -> str:
    return repo_scope_key(target_root, target_scope)


def resolve_local_state(target: Path, *, no_local_files: bool = False) -> LocalState:
    target_scope = target.resolve()
    try:
        target_root = git_root(target_scope)
    except RepoStateError as e:
        raise LocalWorkflowError(str(e)) from e
    scope = scope_key(target_root, target_scope)
    key = repo_key(target_root)
    if no_local_files:
        state_dir = default_state_home() / key / scope
        mode: StateMode = "external"
    else:
        state_dir = target_root / LOCAL_STATE_DIR / KIT_STATE_DIR / scope
        mode = "local"
    return LocalState(
        target_root=target_root,
        target_scope=target_scope,
        state_dir=state_dir.resolve(),
        mode=mode,
        scope=scope,
        repo_key=key,
    )


def git_sha(path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else ""


def git_dirty(path: Path) -> bool:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return bool(result.stdout.strip()) if result.returncode == 0 else False


def agent_local_state_paths(path: Path) -> list[str]:
    """Return common agent-local paths that are currently part of git status."""
    present: list[str] = []
    for candidate in COMMON_AGENT_LOCAL_STATE_PATHS:
        result = subprocess.run(
            ["git", "status", "--porcelain", "--", candidate],
            cwd=path,
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            present.append(candidate)
    return present


def agent_local_state_warning(path: Path) -> str:
    paths = agent_local_state_paths(path)
    if not paths:
        return ""
    examples = " ".join(f"--exclude {item}" for item in paths)
    return (
        " Common agent-local state is present in git status "
        f"({', '.join(paths)}); remove/ignore it, or record a constrained "
        f"checkpoint with `hk sync {examples} --reason ...`."
    )


def git_pathspec_excludes(exclude_paths: tuple[str, ...] = ()) -> list[str]:
    return [f":(exclude){path}" for path in exclude_paths]


def git_tracked_paths_for_path(path: Path, candidate: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--", candidate],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line for line in result.stdout.splitlines() if line.strip()]


def sync_exclude_safety_error(path: Path, candidate: str) -> str:
    tracked = git_tracked_paths_for_path(path, candidate)
    if tracked:
        return (
            "sync --exclude only supports untracked local-only paths; "
            f"refusing tracked paths or descendants under {candidate}: {', '.join(tracked[:3])}"
        )
    status = git_status_for_path(path, candidate).strip()
    if not status:
        return f"sync --exclude path is not present in git status: {candidate}"
    if any(not line.startswith("?? ") for line in status.splitlines()):
        return (
            "sync --exclude only supports untracked local-only paths; "
            f"refusing tracked or staged path: {candidate}"
        )
    return ""


def git_status_for_path(path: Path, candidate: str) -> str:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--", candidate],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    return result.stdout if result.returncode == 0 else ""


def _hash_untracked_paths(hasher, path: Path, pathspec: list[str]) -> None:
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z", *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
    )
    if untracked.returncode != 0:
        return
    for raw_name in untracked.stdout.split(b"\0"):
        if not raw_name:
            continue
        relative = Path(raw_name.decode("utf-8", errors="surrogateescape"))
        full_path = path / relative
        hasher.update(b"untracked\0")
        hasher.update(raw_name)
        hasher.update(b"\0")
        try:
            stat_result = full_path.lstat()
        except OSError:
            hasher.update(b"<missing>")
            hasher.update(b"\0")
            continue
        hasher.update(str(stat_result.st_mode).encode("ascii"))
        hasher.update(b"\0")
        if stat.S_ISLNK(stat_result.st_mode):
            hasher.update(b"symlink\0")
            try:
                hasher.update(os.readlink(full_path).encode("utf-8", "surrogateescape"))
            except OSError:
                hasher.update(b"<unreadable-symlink>")
        elif stat.S_ISREG(stat_result.st_mode):
            hasher.update(b"file\0")
            try:
                with full_path.open("rb") as file_obj:
                    for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                        hasher.update(chunk)
            except OSError:
                hasher.update(b"<unreadable>")
        hasher.update(b"\0")


def git_diff_hash(path: Path, exclude_paths: tuple[str, ...] = ()) -> str:
    """Hash unstaged, staged, and status state for sync freshness."""
    hasher = hashlib.sha256()
    pathspec = (
        ["--", ".", *git_pathspec_excludes(exclude_paths)] if exclude_paths else []
    )
    commands = (
        ["git", "diff", "--no-ext-diff", "--binary", *pathspec],
        ["git", "diff", "--cached", "--no-ext-diff", "--binary", *pathspec],
        ["git", "status", "--porcelain", *pathspec],
    )
    for command in commands:
        result = subprocess.run(
            command,
            cwd=path,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            return ""
        hasher.update("\0".join(command).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(result.stdout)
        hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def git_work_diff_hash(
    path: Path, *, base_sha: str, exclude_paths: tuple[str, ...] = ()
) -> str:
    """Hash the work diff from the HK work start SHA to the current tree."""
    if not base_sha.strip():
        return git_diff_hash(path, exclude_paths)
    hasher = hashlib.sha256()
    pathspec = ["--", ".", *git_pathspec_excludes(exclude_paths)]
    result = subprocess.run(
        ["git", "diff", "--no-ext-diff", "--binary", base_sha, *pathspec],
        cwd=path,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    hasher.update(b"work-diff\0")
    hasher.update(base_sha.encode("utf-8"))
    hasher.update(b"\0")
    hasher.update(result.stdout)
    hasher.update(b"\0")
    _hash_untracked_paths(hasher, path, pathspec)
    return "sha256:" + hasher.hexdigest()


def local_exclude_file(path: Path) -> Path | None:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", "info/exclude"],
        cwd=path,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return None
    raw = Path(result.stdout.strip())
    return raw if raw.is_absolute() else path / raw


def ensure_local_exclude(state: LocalState) -> bool:
    if state.mode != "local":
        return False
    exclude = local_exclude_file(state.target_root)
    if exclude is None:
        return False
    exclude.parent.mkdir(parents=True, exist_ok=True)
    existing = exclude.read_text() if exclude.exists() else ""
    pattern = f"/{LOCAL_STATE_DIR}/{KIT_STATE_DIR}/"
    if pattern in existing:
        return True
    marker = f"# harness-kit 2 local state\n{pattern}\n# /harness-kit 2 local state\n"
    separator = "" if not existing or existing.endswith("\n") else "\n"
    exclude.write_text(existing + separator + marker)
    return True


def init_state(target: Path, *, no_local_files: bool = False) -> InitResult:
    state = resolve_local_state(target, no_local_files=no_local_files)
    state.state_dir.mkdir(parents=True, exist_ok=True)
    for child in ("work", "spec"):
        (state.state_dir / child).mkdir(exist_ok=True)
    metadata = {
        "schema_version": STATE_SCHEMA_VERSION,
        "target_root": str(state.target_root),
        "target_scope": str(state.target_scope),
        "state_dir": str(state.state_dir),
        "mode": state.mode,
        "scope": state.scope,
        "repo_key": state.repo_key,
        "updated_at": utc_now(),
    }
    (state.state_dir / "state.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    )
    ignored = ensure_local_exclude(state)
    return InitResult(
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        state_dir=str(state.state_dir),
        mode=state.mode,
        ignored_by_local_git=ignored,
    )


def ensure_state(target: Path, *, no_local_files: bool = False) -> LocalState:
    state = resolve_local_state(target, no_local_files=no_local_files)
    if not (state.state_dir / "state.json").exists():
        init_state(target, no_local_files=no_local_files)
    return state


def list_work_dirs(state: LocalState) -> list[Path]:
    root = state.state_dir / "work"
    if not root.is_dir():
        return []
    return sorted(
        path
        for path in root.iterdir()
        if path.is_dir() and WORK_DIR_RE.match(path.name)
    )


def active_work_dir(state: LocalState) -> Path | None:
    active = state.state_dir / "active-work"
    if active.exists():
        candidate = state.state_dir / "work" / active.read_text().strip()
        if candidate.is_dir():
            return candidate
    work = list_work_dirs(state)
    return work[-1] if work else None


def validate_slug(slug: str) -> str:
    normalized = slug.strip()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", normalized):
        raise LocalWorkflowError(
            "Invalid slug: use lowercase letters, digits, and hyphens"
        )
    return normalized


def next_seq(events_path: Path) -> int:
    try:
        return ledger_next_seq(events_path)
    except LedgerStoreError as e:
        raise LocalWorkflowError(str(e)) from e


def append_event(
    work_dir: Path, event_type: str, data: dict[str, object]
) -> EventRecord:
    try:
        return append_lifecycle_event(
            work_dir, event_type, data, schema_version=STATE_SCHEMA_VERSION
        )
    except LedgerStoreError as e:
        raise LocalWorkflowError(str(e)) from e


def create_work(
    target: Path, slug_arg: str, *, no_local_files: bool = False
) -> WorkResult:
    slug = validate_slug(slug_arg)
    state = ensure_state(target, no_local_files=no_local_files)
    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M%S")
    work_id = f"{timestamp}-{slug}"
    work_dir = state.state_dir / "work" / work_id
    if work_dir.exists():
        raise LocalWorkflowError(f"work already exists: {work_dir}")
    (work_dir / "artifacts").mkdir(parents=True)
    (work_dir / "views").mkdir()
    (work_dir / "evidence.jsonl").write_text("")
    append_event(
        work_dir,
        "work_started",
        {
            "slug": slug,
            "target_root": str(state.target_root),
            "target_scope": str(state.target_scope),
            "branch": git_branch(state.target_root),
            "git_sha": git_sha(state.target_root),
        },
    )
    (state.state_dir / "active-work").write_text(work_id + "\n")
    return WorkResult(
        work_id=work_id, work_dir=str(work_dir), state_dir=str(state.state_dir)
    )


def require_work(state: LocalState) -> Path:
    work_dir = active_work_dir(state)
    if work_dir is None:
        raise LocalWorkflowError(
            "No active work. Run `hk start demo-work --plan 'Describe the intended change'` first."
        )
    return work_dir


def add_note(
    target: Path,
    *,
    kind: str,
    text: str,
    no_local_files: bool = False,
) -> NoteResult:
    if kind not in VALID_NOTE_KINDS:
        valid = ", ".join(VALID_NOTE_KINDS)
        raise LocalWorkflowError(f"invalid note kind '{kind}'. Valid: {valid}")
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    record = append_event(work_dir, "note_added", {"kind": kind, "text": text})
    return NoteResult(work_id=work_dir.name, seq=record.seq, kind=kind, text=text)


def read_events(work_dir: Path) -> list[EventRecord]:
    try:
        return ledger_read_events(work_dir)
    except LedgerStoreError as e:
        raise LocalWorkflowError(str(e)) from e


def read_evidence(work_dir: Path) -> list[EvidenceRecord]:
    try:
        return ledger_read_evidence(work_dir)
    except LedgerStoreError as e:
        raise LocalWorkflowError(str(e)) from e


def int_from_event_data(data: dict[str, object], key: str) -> int:
    value = data.get(key, 0)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    return 0


def string_list_from_event_data(data: dict[str, object], key: str) -> tuple[str, ...]:
    value = data.get(key, [])
    if not isinstance(value, list):
        return ()
    return tuple(str(item) for item in value)


def latest_sync_relevant_seq(events: list[EventRecord]) -> int:
    return max(
        (event.seq for event in events if event.type not in SYNC_IGNORED_EVENT_TYPES),
        default=0,
    )


def normalize_exclude_paths(exclude_paths: tuple[str | Path, ...]) -> tuple[str, ...]:
    normalized: list[str] = []
    for path in exclude_paths:
        text = str(path).strip().replace("\\", "/")
        if not text:
            raise LocalWorkflowError("sync --exclude path cannot be empty")
        text = text.rstrip("/")
        if text in {"", "."}:
            raise LocalWorkflowError(
                "sync --exclude cannot exclude the repository root"
            )
        candidate = Path(text)
        if candidate.is_absolute():
            raise LocalWorkflowError("sync --exclude path must be relative")
        if ".." in candidate.parts:
            raise LocalWorkflowError("sync --exclude path cannot contain '..'")
        if text.startswith(":") or any(char in text for char in "*?["):
            raise LocalWorkflowError(
                "sync --exclude path must be a literal path, not a git pathspec"
            )
        normalized.append(text)
    return tuple(dict.fromkeys(normalized))


def git_path_state_hash(path: Path, candidate: str) -> str:
    hasher = hashlib.sha256()
    commands = (
        ["git", "diff", "--no-ext-diff", "--binary", "--", candidate],
        ["git", "diff", "--cached", "--no-ext-diff", "--binary", "--", candidate],
        ["git", "status", "--porcelain", "--", candidate],
    )
    for command in commands:
        result = subprocess.run(command, cwd=path, capture_output=True, check=False)
        if result.returncode != 0:
            return ""
        hasher.update("\0".join(command).encode("utf-8"))
        hasher.update(b"\0")
        hasher.update(result.stdout)
        hasher.update(b"\0")
    return "sha256:" + hasher.hexdigest()


def excluded_path_metadata(
    path: Path, exclude_paths: tuple[str, ...]
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for candidate in exclude_paths:
        status = git_status_for_path(path, candidate)
        rows.append(
            {
                "path": candidate,
                "status": status.strip(),
                "state_hash": git_path_state_hash(path, candidate),
            }
        )
    return rows


def sync_checkpoint(
    target: Path,
    *,
    check: bool = False,
    exclude_paths: tuple[str | Path, ...] = (),
    reason: str = "",
    no_local_files: bool = False,
) -> SyncResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    events = read_events(work_dir)
    latest_seq = latest_sync_relevant_seq(events)
    normalized_excludes = normalize_exclude_paths(exclude_paths)
    if check and normalized_excludes:
        raise LocalWorkflowError("sync --check cannot be combined with --exclude")
    if normalized_excludes and not reason.strip():
        raise LocalWorkflowError("sync --exclude requires --reason")
    for candidate in normalized_excludes:
        if error := sync_exclude_safety_error(state.target_root, candidate):
            raise LocalWorkflowError(error)
    current_hash = git_diff_hash(state.target_root, normalized_excludes)
    if not current_hash:
        raise LocalWorkflowError("could not compute git diff hash for sync checkpoint")
    sync_events = [event for event in events if event.type == "sync_checkpoint"]
    guidance = [
        "Plan: did you record the agreed implementation intent?",
        "Evidence: did you capture or explain validation?",
        "Learning: did you record anything future agents should know?",
        "Decisions: did you record non-obvious choices?",
        "Gaps: did you disclose missing validation or follow-up work?",
        "Spec/docs: did behavior or product intent change?",
    ]
    if check:
        skip = fresh_sync_skip(events, state) if sync_events else None
        if not sync_events:
            return SyncResult(
                work_id=work_dir.name,
                synced=False,
                message="needs sync: no checkpoint",
                guidance=guidance,
            )
        latest_sync = sync_events[-1]
        synced_seq = int_from_event_data(latest_sync.data, "event_seq")
        checkpoint_excludes = normalize_exclude_paths(
            string_list_from_event_data(latest_sync.data, "excluded_paths")
        )
        for candidate in checkpoint_excludes:
            if sync_exclude_safety_error(state.target_root, candidate):
                return SyncResult(
                    work_id=work_dir.name,
                    synced=False,
                    message="needs sync: excluded path changed or is no longer local-only",
                    guidance=guidance,
                )
        synced_hash = str(latest_sync.data.get("diff_hash", ""))
        current_hash = git_diff_hash(state.target_root, checkpoint_excludes)
        if not current_hash:
            raise LocalWorkflowError("could not compute git diff hash for sync check")
        synced = synced_seq >= latest_seq and synced_hash == current_hash
        if not synced and skip is not None:
            return SyncResult(
                work_id=work_dir.name,
                synced=True,
                message=dangerous_skip_message("sync", [skip]),
                guidance=guidance,
            )
        message = "synced" if synced else "needs sync: work changed after checkpoint"
        return SyncResult(
            work_id=work_dir.name, synced=synced, message=message, guidance=guidance
        )

    evidence_count = len(read_evidence(work_dir))
    note_count = len([event for event in events if event.type == "note_added"])
    data: dict[str, object] = {
        "git_sha": git_sha(state.target_root),
        "diff_hash": current_hash,
        "event_seq": latest_seq,
        "evidence_count": evidence_count,
        "note_count": note_count,
    }
    if normalized_excludes:
        data.update(
            {
                "excluded_paths": list(normalized_excludes),
                "exclude_reason": reason.strip(),
                "excluded": excluded_path_metadata(
                    state.target_root, normalized_excludes
                ),
            }
        )
    append_event(work_dir, "sync_checkpoint", data)
    return SyncResult(
        work_id=work_dir.name,
        synced=True,
        message="recorded sync checkpoint",
        guidance=guidance,
    )


def command_display(command: tuple[str, ...], shell_command: str) -> str:
    if shell_command:
        return shell_command
    return " ".join(shlex.quote(part) for part in command)


def capture_command(
    target: Path,
    command: tuple[str, ...],
    *,
    shell_command: str = "",
    kind: str = "other",
    why: str = "",
    check_name: str = "",
    no_log: bool = False,
    raw_log: bool = False,
    no_local_files: bool = False,
    stream_to_stderr: bool = False,
) -> CaptureResult:
    if not command and not shell_command:
        raise LocalWorkflowError("capture requires a command after -- or --shell TEXT")
    if command and shell_command:
        raise LocalWorkflowError(
            "capture accepts either --shell TEXT or argv after --, not both"
        )
    if kind not in VALID_EVIDENCE_KINDS:
        valid = ", ".join(VALID_EVIDENCE_KINDS)
        raise LocalWorkflowError(f"invalid evidence kind '{kind}'. Valid: {valid}")
    state = ensure_state(target, no_local_files=no_local_files)
    clean_check_name = check_name.strip()
    if clean_check_name:
        try:
            catalog = ProfileCatalog.load()
            profile = catalog.get(catalog.resolve(state.target_scope).profile)
        except (KeyError, ProfileError) as e:
            raise LocalWorkflowError(str(e)) from e
        if clean_check_name not in {check.name for check in profile.checks}:
            valid = ", ".join(check.name for check in profile.checks) or "none"
            raise LocalWorkflowError(
                f"unknown profile check '{clean_check_name}'. Valid checks: {valid}"
            )
    work_dir = active_work_dir(state)
    if work_dir is None:
        created = create_work(target, "implicit-work", no_local_files=no_local_files)
        work_dir = Path(created.work_dir)
    evidence_id = "ev_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    transcript = transcript_path(work_dir, evidence_id)
    started = utc_now()
    dirty_before = git_dirty(state.target_root)
    if shell_command:
        popen_args: str | list[str] = shell_command
        use_shell = True
        argv: list[str] = []
    else:
        popen_args = list(command)
        use_shell = False
        argv = list(command)

    process_result = run_process_to_transcript(
        popen_args,
        cwd=state.target_scope,
        use_shell=use_shell,
        transcript=transcript,
        no_log=no_log,
        raw_log=raw_log,
        stream_to_stderr=stream_to_stderr,
    )
    exit_code = process_result.exit_code
    ended = utc_now()
    duration_ms = process_result.duration_ms
    dirty_after = git_dirty(state.target_root)
    status = "pass" if exit_code == 0 else "fail"
    redacted_argv = redact_argv(argv, raw_log=raw_log)
    redacted_shell_command = redact_text(shell_command, raw_log=raw_log)
    redacted_display = (
        redacted_shell_command
        if shell_command
        else command_display(tuple(redacted_argv), "")
    )
    record = EvidenceRecord(
        schema_version=STATE_SCHEMA_VERSION,
        id=evidence_id,
        type="command",
        capture_mode="captured",
        kind=kind,
        command_display=redacted_display,
        argv=redacted_argv,
        shell_command=redacted_shell_command,
        cwd=str(state.target_scope),
        target=str(state.target_scope),
        branch=git_branch(state.target_root),
        git_sha=git_sha(state.target_root),
        dirty_before=dirty_before,
        dirty_after=dirty_after,
        exit_code=exit_code,
        status=status,
        started_at=started,
        ended_at=ended,
        duration_ms=duration_ms,
        transcript_path=str(transcript if not no_log else ""),
        redaction="raw" if raw_log else "builtin",
        why=why,
        check_name=clean_check_name,
    )
    with (work_dir / "evidence.jsonl").open("a") as file:
        file.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    append_event(
        work_dir,
        "command_captured",
        {
            "evidence_id": evidence_id,
            "exit_code": exit_code,
            "status": status,
            "why": why,
            "check_name": clean_check_name,
        },
    )
    return CaptureResult(
        work_id=work_dir.name,
        evidence_id=evidence_id,
        exit_code=exit_code,
        status=status,
        transcript_path=str(transcript if not no_log else ""),
        why=why,
        check_name=clean_check_name,
    )


def file_sha256(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as file_obj:
        for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
            hasher.update(chunk)
    return "sha256:" + hasher.hexdigest()


def validate_artifact_kind(kind: str) -> str:
    normalized = kind.strip()
    if not re.fullmatch(r"[a-z0-9]+(?:[-_.][a-z0-9]+)*", normalized):
        raise LocalWorkflowError(
            "invalid artifact kind: use lowercase letters, digits, hyphens, underscores, or dots"
        )
    return normalized


def artifact_filename(source: Path, *, kind: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    stem = re.sub(r"[^a-zA-Z0-9_.-]+", "-", source.name).strip(".-")
    name = stem or "artifact"
    return f"artifact_{timestamp}_{kind}_{name}"


def attach_artifact(
    target: Path,
    *,
    source_path: Path,
    kind: str,
    label: str = "",
    redaction: str = "unknown",
    copy: bool = True,
    no_local_files: bool = False,
) -> ArtifactResult:
    clean_kind = validate_artifact_kind(kind)
    if redaction not in {"none", "unknown", "external"}:
        raise LocalWorkflowError(
            "artifact redaction must be one of: none, unknown, external"
        )
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    source = source_path.expanduser().resolve()
    if not source.exists():
        raise LocalWorkflowError(f"artifact path does not exist: {source_path}")
    if not source.is_file():
        raise LocalWorkflowError(f"artifact path is not a file: {source_path}")
    size_bytes = source.stat().st_size
    digest = file_sha256(source)
    artifacts_dir = work_dir / "artifacts"
    artifacts_dir.mkdir(exist_ok=True)
    if copy:
        destination = artifacts_dir / artifact_filename(source, kind=clean_kind)
        shutil.copy2(source, destination)
        artifact_path = str(destination)
    else:
        artifact_path = ""
    data = {
        "kind": clean_kind,
        "label": label.strip(),
        "source_path": str(source),
        "artifact_path": artifact_path,
        "sha256": digest,
        "size_bytes": size_bytes,
        "copied": copy,
        "redaction": redaction,
    }
    record = append_event(work_dir, "artifact_attached", data)
    return ArtifactResult(
        work_id=work_dir.name,
        seq=record.seq,
        kind=clean_kind,
        label=label.strip(),
        source_path=str(source),
        artifact_path=artifact_path,
        sha256=digest,
        size_bytes=size_bytes,
        copied=copy,
        redaction=redaction,
    )


def repo_surfaces(root: Path) -> list[str]:
    candidates = [
        "AGENTS.md",
        "SPEC.md",
        ".mise.toml",
        "scripts/check",
        "pyproject.toml",
        "Cargo.toml",
        "package.json",
        "go.mod",
        ".github/workflows/ci.yml",
        ".pre-commit-config.yaml",
    ]
    return [name for name in candidates if (root / name).exists()]


def find_specs(state: LocalState) -> list[str]:
    return find_specs_for_state(state)


def fresh_sync_skip(
    events: list[EventRecord], state: LocalState
) -> dict[str, object] | None:
    """Return the latest dangerous sync skip if it still covers this snapshot."""
    skips = dangerous_skip_events(events, "sync")
    if not skips:
        return None
    latest = skips[-1]
    skipped_seq = int_from_event_data(latest, "event_seq")
    skipped_hash = str(latest.get("diff_hash", ""))
    if skipped_seq < latest_sync_relevant_seq(events):
        return None
    if skipped_hash != git_diff_hash(state.target_root):
        return None
    return latest


def sync_status_for(state: LocalState) -> str:
    work_dir = active_work_dir(state)
    if work_dir is None:
        return "no-active-work"
    events = read_events(work_dir)
    if not events:
        return "needs-sync"
    sync_events = [event for event in events if event.type == "sync_checkpoint"]
    if sync_events:
        latest_sync = sync_events[-1]
        synced_seq = int_from_event_data(latest_sync.data, "event_seq")
        checkpoint_excludes = normalize_exclude_paths(
            string_list_from_event_data(latest_sync.data, "excluded_paths")
        )
        if any(
            sync_exclude_safety_error(state.target_root, candidate)
            for candidate in checkpoint_excludes
        ):
            return "needs-sync"
        if synced_seq >= latest_sync_relevant_seq(events) and str(
            latest_sync.data.get("diff_hash", "")
        ) == git_diff_hash(state.target_root, checkpoint_excludes):
            return "synced"
    if sync_events and fresh_sync_skip(events, state) is not None:
        return "sync-dangerously-skipped"
    return "needs-sync"


def unique_paths(paths: list[Path]) -> list[str]:
    seen: set[str] = set()
    rows: list[str] = []
    for path in paths:
        text = str(path)
        if text in seen or not path.exists():
            continue
        seen.add(text)
        rows.append(text)
    return rows


def brief(target: Path, *, no_local_files: bool = False) -> Brief:
    state = resolve_local_state(target, no_local_files=no_local_files)
    active = active_work_dir(state) if state.state_dir.exists() else None
    try:
        profiles = list(profile_names())
    except ProfileError as e:
        raise LocalWorkflowError(str(e)) from e
    spec_sources = (
        find_specs(state)
        if state.state_dir.exists()
        else unique_paths(
            [state.target_scope / "SPEC.md", state.target_root / "SPEC.md"]
        )
    )
    return Brief(
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        branch=git_branch(state.target_root),
        git_sha=git_sha(state.target_root),
        dirty=git_dirty(state.target_root),
        state_dir=str(state.state_dir),
        state_exists=state.state_dir.exists(),
        active_work=active.name if active else "",
        sync_status=sync_status_for(state) if active else "no-active-work",
        agents_md=unique_paths(
            [state.target_scope / "AGENTS.md", state.target_root / "AGENTS.md"]
        ),
        spec_sources=spec_sources,
        repo_surfaces=repo_surfaces(state.target_root),
        profiles=profiles,
    )


def brief_markdown(value: Brief) -> str:
    lines = [
        "# Current Repo Brief",
        "",
        "## Repo state",
        f"- Target root: `{value.target_root}`",
        f"- Target scope: `{value.target_scope}`",
        f"- Branch: `{value.branch}`",
        f"- Git SHA: `{value.git_sha}`",
        f"- Dirty: `{str(value.dirty).lower()}`",
        "",
        "## Harness state",
        f"- State exists: `{str(value.state_exists).lower()}`",
        f"- State dir: `{value.state_dir}`",
        f"- Active work: `{value.active_work or 'none'}`",
        f"- Sync status: `{value.sync_status}`",
        "",
        "## Instructions and specs",
    ]
    lines.extend(
        [f"- AGENTS: `{path}`" for path in value.agents_md] or ["- AGENTS: none found"]
    )
    lines.extend(
        [f"- SPEC: `{path}`" for path in value.spec_sources] or ["- SPEC: none found"]
    )
    lines.extend(["", "## Repo surfaces"])
    lines.extend(
        [f"- `{surface}`" for surface in value.repo_surfaces] or ["- none detected"]
    )
    lines.extend(
        [
            "",
            "## Profiles",
            "Use `hk profile list --target <target> --json` and repo instructions to choose a profile. No profile is auto-selected here.",
        ]
    )
    lines.extend([f"- `{profile}`" for profile in value.profiles])
    return "\n".join(lines) + "\n"


def render_handoff(
    work_dir: Path, state: LocalState, *, format: HandoffFormat = "markdown"
) -> str:
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    render = render_handoff_pr_markdown if format == "pr" else render_handoff_markdown
    return render(
        work_id=work_dir.name,
        branch=git_branch(state.target_root),
        git_sha=git_sha(state.target_root),
        dirty=git_dirty(state.target_root),
        sync_status=sync_status_for(state),
        events=events,
        evidence=evidence,
        readiness=ready_for_work(work_dir, state, check_handoff=False),
    )


def _status_changed_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    paths: list[str] = []
    for line in result.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else line.strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path.endswith("/"):
            continue
        paths.append(path)
    return paths


def _diff_changed_paths(root: Path, base_sha: str) -> list[str]:
    if not base_sha.strip():
        return []
    result = subprocess.run(
        ["git", "diff", "--name-only", base_sha, "--"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def _untracked_paths(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        capture_output=True,
        check=False,
        text=True,
    )
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def work_start_git_sha(events: list[EventRecord]) -> str:
    for event in events:
        if event.type == "work_started":
            return str(event.data.get("git_sha") or "")
    return ""


def changed_paths(root: Path, *, base_sha: str = "") -> list[str]:
    paths = [
        *_diff_changed_paths(root, base_sha),
        *_status_changed_paths(root),
        *_untracked_paths(root),
    ]
    return list(dict.fromkeys(path.replace("\\", "/") for path in paths if path))


def changed_paths_for_work(root: Path, work_dir: Path) -> list[str]:
    return changed_paths(root, base_sha=work_start_git_sha(read_events(work_dir)))


def review_prompt(
    target: Path, *, review_name: str = "", no_local_files: bool = False
) -> ReviewPromptResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    profile_review = None
    if review_name.strip():
        try:
            catalog = ProfileCatalog.load()
            profile = catalog.get(catalog.resolve(state.target_scope).profile)
        except (KeyError, ProfileError) as e:
            raise LocalWorkflowError(str(e)) from e
        profile_review = next(
            (
                review
                for review in profile.reviews
                if review.name == review_name.strip()
            ),
            None,
        )
        if profile_review is None:
            valid = ", ".join(review.name for review in profile.reviews) or "none"
            raise LocalWorkflowError(
                f"unknown profile review '{review_name}'. Valid reviews: {valid}"
            )
    prompt = render_review_prompt(
        work_id=work_dir.name,
        target_root=str(state.target_root),
        branch=git_branch(state.target_root),
        events=read_events(work_dir),
        evidence=read_evidence(work_dir),
        changed_paths=changed_paths_for_work(state.target_root, work_dir),
        profile_review=profile_review,
    )
    return ReviewPromptResult(work_id=work_dir.name, prompt=prompt)


def add_review(
    target: Path,
    *,
    backend: str,
    reviewer: str,
    rubrics: tuple[str, ...],
    summary: str,
    disposition: str = "accepted",
    review_name: str = "",
    no_local_files: bool = False,
) -> ReviewResult:
    if not backend.strip():
        raise LocalWorkflowError("review requires --backend")
    if not reviewer.strip():
        raise LocalWorkflowError("review requires --reviewer")
    if is_self_review_identity(backend) or is_self_review_identity(reviewer):
        raise LocalWorkflowError(f"review must be independent: {SELF_REVIEW_GUIDANCE}")
    if not summary.strip():
        raise LocalWorkflowError("review requires --summary")
    clean_rubrics = [item.strip() for item in rubrics if item.strip()]
    if not clean_rubrics:
        raise LocalWorkflowError("review requires at least one --rubric")
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    clean_review_name = review_name.strip()
    if clean_review_name:
        try:
            catalog = ProfileCatalog.load()
            profile = catalog.get(catalog.resolve(state.target_scope).profile)
        except (KeyError, ProfileError) as e:
            raise LocalWorkflowError(str(e)) from e
        if clean_review_name not in {review.name for review in profile.reviews}:
            valid = ", ".join(review.name for review in profile.reviews) or "none"
            raise LocalWorkflowError(
                f"unknown profile review '{clean_review_name}'. Valid reviews: {valid}"
            )
    record_data: dict[str, object] = {
        "backend": backend.strip(),
        "reviewer": reviewer.strip(),
        "rubrics": clean_rubrics,
        "summary": summary.strip(),
        "disposition": disposition.strip() or "accepted",
    }
    if clean_review_name:
        record_data["review_name"] = clean_review_name
    record = append_event(work_dir, "review_added", record_data)
    return ReviewResult(
        work_id=work_dir.name,
        seq=record.seq,
        backend=backend.strip(),
        reviewer=reviewer.strip(),
        rubrics=clean_rubrics,
        summary=summary.strip(),
        disposition=disposition.strip() or "accepted",
        review_name=clean_review_name,
    )


def add_dangerous_skip(
    target: Path,
    *,
    check: str,
    label: str,
    reason: str,
    mitigation: str,
    no_local_files: bool = False,
) -> DangerousSkipResult:
    if check not in {"review", "validation", "sync"}:
        raise LocalWorkflowError("dangerously-skip supports: review, validation, sync")
    if not label.strip():
        raise LocalWorkflowError("dangerously-skip requires --label")
    if not reason.strip():
        raise LocalWorkflowError("dangerously-skip requires --reason")
    if not mitigation.strip():
        raise LocalWorkflowError("dangerously-skip requires --mitigation")
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    data: dict[str, object] = {
        "check": check,
        "label": label.strip(),
        "reason": reason.strip(),
        "mitigation": mitigation.strip(),
    }
    if check == "sync":
        events = read_events(work_dir)
        if not any(event.type == "sync_checkpoint" for event in events):
            raise LocalWorkflowError(
                "dangerously-skip sync requires a prior `hk sync` checkpoint"
            )
        data.update(
            {
                "git_sha": git_sha(state.target_root),
                "diff_hash": git_diff_hash(state.target_root),
                "event_seq": max((event.seq for event in events), default=0) + 1,
            }
        )
    record = append_event(work_dir, "dangerous_skip_added", data)
    return DangerousSkipResult(
        work_id=work_dir.name,
        seq=record.seq,
        check=check,
        label=label.strip(),
        reason=reason.strip(),
        mitigation=mitigation.strip(),
    )


def ready(target: Path, *, no_local_files: bool = False) -> ReadyResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    return ready_for_work(work_dir, state, check_handoff=True)


def required_profile_items_for_work(
    state: LocalState, work_dir: Path
) -> tuple[tuple[RequiredProfileItem, ...], tuple[RequiredProfileItem, ...]]:
    try:
        catalog = ProfileCatalog.load()
        profile_name = catalog.resolve(state.target_scope).profile
        view = catalog.checks_view(
            profile_name,
            target=state.target_scope,
            repo_root=state.target_root,
            changed_paths=tuple(changed_paths_for_work(state.target_root, work_dir)),
        )
    except (KeyError, ProfileError) as e:
        raise LocalWorkflowError(str(e)) from e
    required_checks = tuple(
        RequiredProfileItem(
            name=item.name,
            purpose=item.purpose,
            matched_paths=item.matched_paths,
        )
        for item in view.suggested_checks
        if item.required
    )
    required_reviews = tuple(
        RequiredProfileItem(
            name=item.name,
            purpose=item.purpose,
            matched_paths=item.matched_paths,
        )
        for item in view.suggested_reviews
        if item.required
    )
    return required_checks, required_reviews


def ready_for_work(
    work_dir: Path, state: LocalState, *, check_handoff: bool = True
) -> ReadyResult:
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    required_checks, required_reviews = required_profile_items_for_work(state, work_dir)
    return ready_for_events(
        work_id=work_dir.name,
        events=events,
        evidence=evidence,
        sync_status=sync_status_for(state),
        agent_local_warning=agent_local_state_warning(state.target_root),
        check_handoff=check_handoff,
        handoff_check=lambda: render_handoff(work_dir, state),
        required_profile_checks=required_checks,
        required_profile_reviews=required_reviews,
    )


def lifecycle_phase(events: list[EventRecord], readiness: ReadyResult | None) -> str:
    return policy_lifecycle_phase(events, readiness)


def status(target: Path, *, no_local_files: bool = False) -> StatusResult:
    state = resolve_local_state(target, no_local_files=no_local_files)
    work_dir = active_work_dir(state) if state.state_dir.exists() else None
    if work_dir is None:
        return StatusResult(
            active_work="",
            target_root=str(state.target_root),
            target_scope=str(state.target_scope),
            state_dir=str(state.state_dir),
            sync_status="no-active-work",
            ready_status="not-started",
            phase="not-started",
            checks=[],
            next_actions=[
                "start: hk start demo-work --plan 'Describe the intended change and validation approach'"
            ],
        )

    events = read_events(work_dir)
    readiness = ready_for_work(work_dir, state, check_handoff=False)
    actions: list[str] = []
    if not notes_by_kind(events, "plan"):
        actions.append(
            "plan: hk plan 'Describe the intended change and validation approach' (next time: hk start demo-work --plan '...')"
        )
    if not notes_by_kinds(events, ("context", "background")):
        actions.append(
            "context (optional): hk context 'Constraints, relevant files, or repo facts' if it prevents rediscovery"
        )
    if not notes_by_kind(events, "decision") or not notes_by_kind(
        events, "spec-impact"
    ):
        actions.append(
            "decision: hk decide 'Decision/spec reflection' --spec-impact none|updated|not-needed [--spec-ref PATH]"
        )
    check_map = {check.id: check for check in readiness.checks}
    if check_map.get("validation") and check_map["validation"].status == "fail":
        actions.append(
            "validation: hk validate --why 'Fast gate passes' -- mise run check"
        )
    if check_map.get("review") and check_map["review"].status == "fail":
        actions.append(
            "review required: preferred independent AI/tool reviewer; minimum fresh-context subagent. Run `hk review prompt`; dispatch it via your harness if available (Pi `subagent` tool, Claude Code `Agent` tool/`Task` alias, Codex Shell tool running `codex review --uncommitted`); record with `hk review add ...`, then re-run `hk status`; or explicitly `hk dangerously-skip review --label no-review --reason ... --mitigation ...`; self-review does not count"
        )
    for check in readiness.checks:
        if check.status == "fail" and check.id.startswith("profile-check:"):
            actions.append(f"validation: {check.message}")
        if check.status == "fail" and check.id.startswith("profile-review:"):
            actions.append(f"review: {check.message}")
    if check_map.get("sync") and check_map["sync"].status == "fail":
        sync_action = "sync: hk sync after reconciling changes"
        warning = agent_local_state_warning(state.target_root)
        if warning:
            sync_action += warning
        actions.append(sync_action)
    if not actions and readiness.ready:
        actions.append("handoff: hk handoff")
    return StatusResult(
        active_work=work_dir.name,
        target_root=str(state.target_root),
        target_scope=str(state.target_scope),
        state_dir=str(state.state_dir),
        sync_status=sync_status_for(state),
        ready_status=readiness.status,
        phase=lifecycle_phase(events, readiness),
        checks=readiness.checks,
        next_actions=actions,
    )


def materialize_work(target: Path, *, no_local_files: bool = False) -> HandoffResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    events = read_events(work_dir)
    views = work_dir / "views"
    write_note_views(views, events)
    handoff = render_handoff(work_dir, state)
    path = views / "handoff.md"
    path.write_text(handoff)
    return HandoffResult(work_id=work_dir.name, content=handoff, path=str(path))


def summary(target: Path, *, no_local_files: bool = False) -> HandoffResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    content = render_summary_markdown(
        work_id=work_dir.name,
        branch=git_branch(state.target_root),
        git_sha=git_sha(state.target_root),
        dirty=git_dirty(state.target_root),
        sync_status=sync_status_for(state),
        events=events,
        evidence=evidence,
        readiness=ready_for_work(work_dir, state, check_handoff=False),
    )
    return HandoffResult(work_id=work_dir.name, content=content)


def handoff(
    target: Path,
    *,
    output_path: Path | None = None,
    no_local_files: bool = False,
    format: HandoffFormat = "markdown",
) -> HandoffResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    content = render_handoff(work_dir, state, format=format)
    path_text = ""
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        path_text = str(output_path)
    return HandoffResult(work_id=work_dir.name, content=content, path=path_text)


def _relative_to_root(path: Path, root: Path) -> str:
    try:
        return (
            path.resolve(strict=False)
            .relative_to(root.resolve(strict=False))
            .as_posix()
        )
    except ValueError:
        return str(path.resolve(strict=False))


def _export_relevant_events(events: list[EventRecord]) -> list[EventRecord]:
    return [event for event in events if event.type not in SYNC_IGNORED_EVENT_TYPES]


def _event_count(events: list[EventRecord]) -> int:
    return len(_export_relevant_events(events))


def _max_event_seq(events: list[EventRecord]) -> int:
    return max((event.seq for event in _export_relevant_events(events)), default=0)


def _text_hash(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _file_hash(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _handoff_dir_metadata(
    *,
    state: LocalState,
    work_dir: Path,
    output_path: Path,
    events: list[EventRecord],
    evidence: list[EvidenceRecord],
    readiness: ReadyResult,
    file_hashes: dict[str, str] | None = None,
) -> dict[str, object]:
    output_relative = _relative_to_root(output_path, state.target_root)
    return {
        "schema_version": 1,
        "generated_by": "hk export --format handoff-dir",
        "generated_at": datetime.now(UTC).isoformat(),
        "work_id": work_dir.name,
        "target_root": ".",
        "target_scope": _relative_to_root(state.target_scope, state.target_root),
        "branch": git_branch(state.target_root),
        "git_sha": git_sha(state.target_root),
        "dirty": git_dirty(state.target_root),
        "sync_status": sync_status_for(state),
        "ready_status": readiness.status,
        "ready": readiness.ready,
        "diff_hash": git_work_diff_hash(
            state.target_root,
            base_sha=work_start_git_sha(events),
            exclude_paths=(output_relative,),
        ),
        "event_count": _event_count(events),
        "event_seq": _max_event_seq(events),
        "evidence_count": len(evidence),
        "evidence_ids": [record.id for record in evidence],
        "output_path": output_relative,
        "files": [
            "README.md",
            "meta.json",
            "artifacts/README.md",
        ],
        "file_hashes": file_hashes or {},
    }


def _export_readme(work_id: str, handoff_content: str, output_relative: str) -> str:
    handoff_body = handoff_content.removeprefix("# Handoff\n\n")
    return (
        f"# HK export: `{work_id}`\n\n"
        "This directory is a generated review/handoff package from the Harness Kit "
        "ledger. Do not hand-edit it; update HK with `hk plan`, `hk decide`, "
        "`hk validate`, `hk review add`, and `hk sync`, then regenerate.\n\n"
        "## Freshness\n"
        "Validate this export against local HK state with:\n\n"
        "```bash\n"
        f"hk export --format handoff-dir --output {shlex.quote(output_relative)} --target . --check\n"
        "```\n\n"
        "Historical hand-authored slice plans live under `.ai/plans/`; new "
        "Harness Toolkit repo work should use HK and generated `.ai/hk/` exports.\n\n"
        "## Handoff\n\n"
        f"{handoff_body}"
    )


def _artifacts_readme() -> str:
    return (
        "# Artifacts\n\n"
        "Artifacts are intentionally explicit. Raw validation transcripts stay in "
        "local/external HK state and are referenced from `README.md`; attach durable, "
        "reviewable files with `hk artifact attach` before export when they should be "
        "shared.\n"
    )


def _safe_export_relative(value: object) -> str | None:
    relative = str(value)
    path = Path(relative)
    if path.is_absolute() or ".." in path.parts or not relative.strip():
        return None
    return path.as_posix()


def _previous_export_files(destination: Path) -> set[str]:
    generated_names = {
        "AGENTS.md",
        "SUMMARY.md",
        "HANDOFF.md",
        "VALIDATION.md",
        "REVIEW.md",
        "DECISIONS.md",
        "META.json",
    }
    previous: set[str] = set()
    for metadata_name in ("meta.json", "META.json"):
        metadata_path = destination / metadata_name
        if not metadata_path.exists():
            continue
        try:
            metadata = json.loads(metadata_path.read_text())
        except json.JSONDecodeError:
            continue
        if not isinstance(metadata, dict):
            continue
        files = metadata.get("files", [])
        if isinstance(files, list):
            previous.update(
                relative for item in files if (relative := _safe_export_relative(item))
            )
    previous.update(name for name in generated_names if (destination / name).exists())
    return previous


def _remove_obsolete_export_files(destination: Path, keep: set[str]) -> None:
    destination_root = destination.resolve(strict=False)
    for relative in sorted(_previous_export_files(destination) - keep):
        path = destination / relative
        try:
            path.resolve(strict=False).relative_to(destination_root)
        except ValueError:
            continue
        if path.exists() and path.is_file():
            path.unlink()


def _sanitize_export_content(content: str, state: LocalState) -> str:
    root = str(state.target_root)
    return content.replace(root + "/", "").replace(root, ".")


def _compare_export_metadata(
    current: dict[str, object], recorded: dict[str, object]
) -> list[str]:
    ignored = {
        "generated_at",
        "dirty",
        "sync_status",
        "ready_status",
        "ready",
        "git_sha",
        "target_root",
        "target_scope",
        "file_hashes",
    }
    mismatches: list[str] = []
    for key, value in current.items():
        if key in ignored:
            continue
        if recorded.get(key) != value:
            mismatches.append(key)
    return mismatches


def _regenerate_export_hint(destination: Path) -> str:
    return (
        "Try: regenerate with `hk export --format handoff-dir "
        f"--output {shlex.quote(str(destination))} --target .`."
    )


def export_handoff_dir(
    target: Path,
    *,
    output_path: Path | None = None,
    check: bool = False,
    no_local_files: bool = False,
) -> ExportResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    destination = output_path or (state.target_root / ".ai" / "hk" / work_dir.name)
    if not destination.is_absolute():
        destination = state.target_root / destination
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    readiness = ready_for_work(work_dir, state, check_handoff=False)
    metadata = _handoff_dir_metadata(
        state=state,
        work_dir=work_dir,
        output_path=destination,
        events=events,
        evidence=evidence,
        readiness=readiness,
    )
    meta_path = destination / "meta.json"
    if check:
        if not meta_path.exists():
            raise LocalWorkflowError(
                f"HK export metadata missing: {meta_path}\n"
                + _regenerate_export_hint(destination)
            )
        try:
            recorded = json.loads(meta_path.read_text())
        except json.JSONDecodeError as e:
            raise LocalWorkflowError(
                f"invalid HK export metadata {meta_path}: {e}\n"
                + _regenerate_export_hint(destination)
            ) from e
        if not isinstance(recorded, dict):
            raise LocalWorkflowError(
                f"invalid HK export metadata {meta_path}: expected JSON object\n"
                + _regenerate_export_hint(destination)
            )
        expected_files = metadata.get("files", [])
        if not isinstance(expected_files, list):
            raise LocalWorkflowError(
                f"HK export metadata files field is invalid: {meta_path}"
            )
        missing_files = [
            str(item)
            for item in expected_files
            if not (destination / str(item)).exists()
        ]
        recorded_hashes = recorded.get("file_hashes", {})
        if not isinstance(recorded_hashes, dict):
            raise LocalWorkflowError(
                f"HK export metadata file_hashes field is invalid: {meta_path}\n"
                + _regenerate_export_hint(destination)
            )
        hash_mismatches = [
            str(relative)
            for relative, expected_hash in recorded_hashes.items()
            if (destination / str(relative)).exists()
            and _file_hash(destination / str(relative)) != expected_hash
        ]
        mismatches = _compare_export_metadata(metadata, recorded)
        if missing_files or mismatches or hash_mismatches:
            details = []
            if missing_files:
                details.append("missing files: " + ", ".join(missing_files))
            if mismatches:
                details.append("stale metadata: " + ", ".join(mismatches))
            if hash_mismatches:
                details.append(
                    "modified generated files: " + ", ".join(hash_mismatches)
                )
            raise LocalWorkflowError(
                "HK export is stale or incomplete: "
                + "; ".join(details)
                + "\n"
                + _regenerate_export_hint(destination)
            )
        return ExportResult(
            work_id=work_dir.name,
            path=str(destination),
            format="handoff-dir",
            checked=True,
            fresh=True,
            message="HK export is fresh",
        )

    destination.mkdir(parents=True, exist_ok=True)
    artifacts_dir = destination / "artifacts"
    if artifacts_dir.is_symlink():
        artifacts_dir.unlink()
    artifacts_dir.mkdir(exist_ok=True)
    output_relative = _relative_to_root(destination, state.target_root)
    handoff_content = _sanitize_export_content(
        render_handoff(work_dir, state, format="markdown"), state
    )
    files = {
        "README.md": _export_readme(
            work_dir.name,
            handoff_content,
            output_relative,
        ),
        "artifacts/README.md": _artifacts_readme(),
    }
    file_hashes = {relative: _text_hash(content) for relative, content in files.items()}
    metadata = _handoff_dir_metadata(
        state=state,
        work_dir=work_dir,
        output_path=destination,
        events=events,
        evidence=evidence,
        readiness=readiness,
        file_hashes=file_hashes,
    )
    files["meta.json"] = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    _remove_obsolete_export_files(destination, set(files))
    for relative, content in files.items():
        path = destination / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return ExportResult(
        work_id=work_dir.name,
        path=str(destination),
        format="handoff-dir",
        message="HK handoff directory exported",
    )


def init_spec(target: Path, *, no_local_files: bool = False) -> SpecResult:
    state = ensure_state(target, no_local_files=no_local_files)
    try:
        return init_spec_for_state(state)
    except SpecWorkflowError as e:
        raise LocalWorkflowError(str(e)) from e


def spec_status(target: Path, *, no_local_files: bool = False) -> SpecResult:
    state = resolve_local_state(target, no_local_files=no_local_files)
    try:
        return spec_status_for_state(state)
    except SpecWorkflowError as e:
        raise LocalWorkflowError(str(e)) from e


def spec_outline(target: Path, *, no_local_files: bool = False) -> SpecOutline:
    state = resolve_local_state(target, no_local_files=no_local_files)
    try:
        return spec_outline_for_state(state)
    except SpecWorkflowError as e:
        raise LocalWorkflowError(str(e)) from e


def spec_promote_dry_run(target: Path, *, no_local_files: bool = False) -> str:
    state = resolve_local_state(target, no_local_files=no_local_files)
    try:
        return spec_promote_dry_run_for_state(state)
    except SpecWorkflowError as e:
        raise LocalWorkflowError(str(e)) from e


def json_dump_dataclass(value: JsonDataclass) -> str:
    return json.dumps(asdict(value), indent=2, sort_keys=True)


def json_dump_object(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def print_capture_and_exit(result: CaptureResult) -> None:
    print(json_dump_dataclass(result))
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)
