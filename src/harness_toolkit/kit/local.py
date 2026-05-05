"""Harness Kit 2.0 local assistant primitives.

This module intentionally keeps the first 2.0 implementation small: repo brief,
local/external state, ledger-backed work units, sync checkpoints, command
capture, generated handoff/materialized views, and local specs.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from harness_toolkit.kit.workflow import git_branch, git_root, repo_key

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
SENSITIVE_OPTION_NAMES = {
    "--password",
    "--passwd",
    "--pwd",
    "--secret",
    "--token",
    "--api-key",
    "--apikey",
    "--access-token",
}
SECRET_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (
        re.compile(
            r"(?i)(password|passwd|pwd|secret|token|api[_-]?key)(\s*[=:]\s*)\S+"
        ),
        r"\1\2[REDACTED]",
    ),
    (re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]{12,}"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(sk-[A-Za-z0-9]{12,})"), "[REDACTED]"),
    (re.compile(r"gh[pousr]_[A-Za-z0-9_]{12,}"), "[REDACTED]"),
    (
        re.compile(
            r"(?i)(--(?:password|passwd|pwd|secret|token|api-key|apikey|access-token)(?:=|\s+))(?:'[^']*'|\"[^\"]*\"|\S+)"
        ),
        r"\1[REDACTED]",
    ),
)

StateMode = Literal["local", "external"]
NoteKind = Literal[
    "context", "plan", "background", "learning", "decision", "gap", "spec-impact"
]
EvidenceKind = Literal["test", "lint", "typecheck", "build", "check", "e2e", "other"]
HandoffFormat = Literal["markdown", "pr", "json"]


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


@dataclass(frozen=True)
class NoteResult:
    work_id: str
    seq: int
    kind: str
    text: str


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


@dataclass(frozen=True)
class ReviewResult:
    work_id: str
    seq: int
    backend: str
    reviewer: str
    rubrics: list[str]
    summary: str
    disposition: str


@dataclass(frozen=True)
class ReadyCheck:
    id: str
    status: str
    message: str


@dataclass(frozen=True)
class ReadyResult:
    work_id: str
    ready: bool
    status: str
    checks: list[ReadyCheck]


@dataclass(frozen=True)
class SpecResult:
    spec_path: str
    source: str
    created: bool = False


@dataclass(frozen=True)
class SpecOutline:
    spec_path: str
    source: str
    headings: list[str]


@dataclass(frozen=True)
class HandoffResult:
    work_id: str
    content: str
    path: str = ""


JsonDataclass = (
    Brief
    | InitResult
    | WorkResult
    | NoteResult
    | SyncResult
    | CaptureResult
    | ReviewResult
    | ReadyResult
    | SpecResult
    | SpecOutline
    | HandoffResult
)


@dataclass(frozen=True)
class EventRecord:
    schema_version: int
    seq: int
    type: str
    at: str
    data: dict[str, object]


@dataclass(frozen=True)
class EvidenceRecord:
    schema_version: int
    id: str
    type: str
    capture_mode: str
    kind: str
    command_display: str
    argv: list[str]
    shell_command: str
    cwd: str
    target: str
    branch: str
    git_sha: str
    dirty_before: bool
    dirty_after: bool
    exit_code: int
    status: str
    started_at: str
    ended_at: str
    duration_ms: int
    transcript_path: str
    redaction: str
    why: str = ""


def utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def default_state_home() -> Path:
    state_home = Path(
        os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state")
    )
    return state_home / "harness-toolkit" / "repos"


def scope_key(target_root: Path, target_scope: Path) -> str:
    try:
        relative = target_scope.resolve().relative_to(target_root.resolve())
    except ValueError:
        return "root"
    if str(relative) == ".":
        return "root"
    raw = str(relative).strip().strip("/")
    if not raw:
        return "root"
    return re.sub(r"[^a-zA-Z0-9_.-]+", "-", raw)


def resolve_local_state(target: Path, *, no_local_files: bool = False) -> LocalState:
    target_scope = target.resolve()
    target_root = git_root(target_scope)
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


def git_diff_hash(path: Path) -> str:
    """Hash unstaged, staged, and status state for sync freshness."""
    hasher = hashlib.sha256()
    commands = (
        ["git", "diff", "--no-ext-diff", "--binary"],
        ["git", "diff", "--cached", "--no-ext-diff", "--binary"],
        ["git", "status", "--porcelain"],
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
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "-z"],
        cwd=path,
        capture_output=True,
        check=False,
    )
    if untracked.returncode != 0:
        return ""
    for raw_name in untracked.stdout.split(b"\0"):
        if not raw_name:
            continue
        relative = Path(raw_name.decode("utf-8", errors="surrogateescape"))
        full_path = path / relative
        hasher.update(b"untracked\0")
        hasher.update(raw_name)
        hasher.update(b"\0")
        if full_path.is_file():
            try:
                with full_path.open("rb") as file_obj:
                    for chunk in iter(lambda: file_obj.read(1024 * 1024), b""):
                        hasher.update(chunk)
            except OSError:
                hasher.update(b"<unreadable>")
        hasher.update(b"\0")
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
    if not events_path.exists():
        return 1
    seq = 0
    for line in events_path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        value = row.get("seq")
        if isinstance(value, int):
            seq = max(seq, value)
    return seq + 1


def append_event(
    work_dir: Path, event_type: str, data: dict[str, object]
) -> EventRecord:
    events_path = work_dir / "events.jsonl"
    seq = next_seq(events_path)
    record = EventRecord(
        schema_version=STATE_SCHEMA_VERSION,
        seq=seq,
        type=event_type,
        at=utc_now(),
        data=data,
    )
    events_path.parent.mkdir(parents=True, exist_ok=True)
    with events_path.open("a") as file:
        file.write(json.dumps(asdict(record), sort_keys=True) + "\n")
    return record


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
        raise LocalWorkflowError("No active work. Run `hk start <slug>` first.")
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
    events: list[EventRecord] = []
    path = work_dir / "events.jsonl"
    if not path.exists():
        return events
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        events.append(
            EventRecord(
                schema_version=int(data["schema_version"]),
                seq=int(data["seq"]),
                type=str(data["type"]),
                at=str(data["at"]),
                data=dict(data.get("data", {})),
            )
        )
    return events


def read_evidence(work_dir: Path) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    path = work_dir / "evidence.jsonl"
    if not path.exists():
        return records
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        data = json.loads(line)
        records.append(
            EvidenceRecord(
                schema_version=int(data["schema_version"]),
                id=str(data["id"]),
                type=str(data["type"]),
                capture_mode=str(data["capture_mode"]),
                kind=str(data["kind"]),
                command_display=str(data["command_display"]),
                argv=list(data.get("argv", [])),
                shell_command=str(data.get("shell_command", "")),
                cwd=str(data["cwd"]),
                target=str(data["target"]),
                branch=str(data["branch"]),
                git_sha=str(data["git_sha"]),
                dirty_before=bool(data["dirty_before"]),
                dirty_after=bool(data["dirty_after"]),
                exit_code=int(data["exit_code"]),
                status=str(data["status"]),
                started_at=str(data["started_at"]),
                ended_at=str(data["ended_at"]),
                duration_ms=int(data["duration_ms"]),
                transcript_path=str(data["transcript_path"]),
                redaction=str(data["redaction"]),
                why=str(data.get("why", "")),
            )
        )
    return records


def int_from_event_data(data: dict[str, object], key: str) -> int:
    value = data.get(key, 0)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value)
    return 0


def latest_sync_relevant_seq(events: list[EventRecord]) -> int:
    return max(
        (event.seq for event in events if event.type not in SYNC_IGNORED_EVENT_TYPES),
        default=0,
    )


def sync_checkpoint(
    target: Path, *, check: bool = False, no_local_files: bool = False
) -> SyncResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    events = read_events(work_dir)
    latest_seq = latest_sync_relevant_seq(events)
    current_hash = git_diff_hash(state.target_root)
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
        if not sync_events:
            return SyncResult(
                work_id=work_dir.name,
                synced=False,
                message="needs sync: no checkpoint",
                guidance=guidance,
            )
        latest_sync = sync_events[-1]
        synced_seq = int_from_event_data(latest_sync.data, "event_seq")
        synced_hash = str(latest_sync.data.get("diff_hash", ""))
        synced = synced_seq >= latest_seq and synced_hash == current_hash
        message = "synced" if synced else "needs sync: work changed after checkpoint"
        return SyncResult(
            work_id=work_dir.name, synced=synced, message=message, guidance=guidance
        )

    evidence_count = len(read_evidence(work_dir))
    note_count = len([event for event in events if event.type == "note_added"])
    append_event(
        work_dir,
        "sync_checkpoint",
        {
            "git_sha": git_sha(state.target_root),
            "diff_hash": current_hash,
            "event_seq": latest_seq,
            "evidence_count": evidence_count,
            "note_count": note_count,
        },
    )
    return SyncResult(
        work_id=work_dir.name,
        synced=True,
        message="recorded sync checkpoint",
        guidance=guidance,
    )


def redact_text(text: str, *, raw_log: bool) -> str:
    if raw_log:
        return text
    redacted = text
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    return redacted


def option_name(argument: str) -> str:
    return argument.split("=", 1)[0].lower()


def redact_argv(argv: list[str], *, raw_log: bool) -> list[str]:
    if raw_log:
        return argv
    redacted: list[str] = []
    redact_next = False
    for argument in argv:
        if redact_next:
            redacted.append("[REDACTED]")
            redact_next = False
            continue
        name = option_name(argument)
        if name in SENSITIVE_OPTION_NAMES:
            if "=" in argument:
                redacted.append(f"{argument.split('=', 1)[0]}=[REDACTED]")
            else:
                redacted.append(argument)
                redact_next = True
            continue
        redacted.append(redact_text(argument, raw_log=raw_log))
    return redacted


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
    no_log: bool = False,
    raw_log: bool = False,
    no_local_files: bool = False,
    stream_to_stderr: bool = False,
) -> CaptureResult:
    if not command and not shell_command:
        raise LocalWorkflowError("capture requires a command after -- or --shell TEXT")
    if kind not in VALID_EVIDENCE_KINDS:
        valid = ", ".join(VALID_EVIDENCE_KINDS)
        raise LocalWorkflowError(f"invalid evidence kind '{kind}'. Valid: {valid}")
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = active_work_dir(state)
    if work_dir is None:
        created = create_work(target, "implicit-work", no_local_files=no_local_files)
        work_dir = Path(created.work_dir)
    evidence_id = "ev_" + datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    transcript = work_dir / "artifacts" / f"{evidence_id}.transcript.log"
    started = utc_now()
    start_time = time.monotonic()
    dirty_before = git_dirty(state.target_root)
    if shell_command:
        popen_args: str | list[str] = shell_command
        use_shell = True
        argv: list[str] = []
    else:
        popen_args = list(command)
        use_shell = False
        argv = list(command)

    try:
        process = subprocess.Popen(
            popen_args,
            cwd=state.target_scope,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            shell=use_shell,
            bufsize=1,
        )
    except OSError as e:
        message = f"failed to start command: {e}\n"
        print(message, end="", file=sys.stderr if stream_to_stderr else sys.stdout)
        if not no_log:
            transcript.write_text(redact_text(message, raw_log=raw_log))
        exit_code = 127
    else:
        assert process.stdout is not None
        transcript_file = None if no_log else transcript.open("w")
        try:
            for chunk in process.stdout:
                print(
                    chunk, end="", file=sys.stderr if stream_to_stderr else sys.stdout
                )
                if transcript_file is not None:
                    transcript_file.write(redact_text(chunk, raw_log=raw_log))
        finally:
            if transcript_file is not None:
                transcript_file.close()
        exit_code = process.wait()
    ended = utc_now()
    duration_ms = int((time.monotonic() - start_time) * 1000)
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
        },
    )
    return CaptureResult(
        work_id=work_dir.name,
        evidence_id=evidence_id,
        exit_code=exit_code,
        status=status,
        transcript_path=str(transcript if not no_log else ""),
        why=why,
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
    specs: list[str] = []
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    local = state.state_dir / "spec" / "SPEC.md"
    if committed.exists():
        specs.append(str(committed))
    elif root_committed.exists():
        specs.append(str(root_committed))
    if local.exists():
        specs.append(str(local) + " (local draft)")
    return specs


def sync_status_for(state: LocalState) -> str:
    work_dir = active_work_dir(state)
    if work_dir is None:
        return "no-active-work"
    events = read_events(work_dir)
    if not events:
        return "needs-sync"
    sync_events = [event for event in events if event.type == "sync_checkpoint"]
    if not sync_events:
        return "needs-sync"
    latest_sync = sync_events[-1]
    synced_seq = int_from_event_data(latest_sync.data, "event_seq")
    if synced_seq < latest_sync_relevant_seq(events):
        return "needs-sync"
    if str(latest_sync.data.get("diff_hash", "")) != git_diff_hash(state.target_root):
        return "needs-sync"
    return "synced"


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
    profiles = ["generic", "python", "go", "rust", "rust-mise"]
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


def notes_by_kind(events: list[EventRecord], kind: str) -> list[str]:
    return notes_by_kinds(events, (kind,))


ACCEPTED_REVIEW_DISPOSITIONS = {
    "accepted",
    "approved",
    "no-blocking-findings",
    "no_blocking_findings",
    "no-findings",
    "no_findings",
}
SELF_REVIEW_TOKENS = ("self", "same-agent", "implementation-agent", "worker-self")
SELF_REVIEW_GUIDANCE = (
    "self-review does not count; run a separate reviewer/subagent with fresh "
    "context, record that review, or use `hk dangerously-skip review --reason ...`"
)


def is_self_review_identity(value: str) -> bool:
    clean = value.strip().lower()
    if clean in {"", "self", "pending", "todo"}:
        return True
    return any(token in clean for token in SELF_REVIEW_TOKENS)


def review_events(events: list[EventRecord]) -> list[dict[str, object]]:
    return [event.data for event in events if event.type == "review_added"]


def accepted_review_events(events: list[EventRecord]) -> list[dict[str, object]]:
    accepted: list[dict[str, object]] = []
    for review in review_events(events):
        backend = str(review.get("backend", "")).strip().lower()
        reviewer = str(review.get("reviewer", "")).strip().lower()
        disposition = str(review.get("disposition", "")).strip().lower()
        if is_self_review_identity(backend):
            continue
        if is_self_review_identity(reviewer):
            continue
        if disposition not in ACCEPTED_REVIEW_DISPOSITIONS:
            continue
        accepted.append(review)
    return accepted


def dangerous_skip_events(
    events: list[EventRecord], check_id: str
) -> list[dict[str, object]]:
    return [
        event.data
        for event in events
        if event.type == "dangerous_skip_added" and event.data.get("check") == check_id
    ]


def notes_by_kinds(events: list[EventRecord], kinds: tuple[str, ...]) -> list[str]:
    rows: list[str] = []
    for event in events:
        if event.type != "note_added":
            continue
        if event.data.get("kind") in kinds:
            rows.append(str(event.data.get("text", "")))
    return rows


def render_handoff(work_dir: Path, state: LocalState) -> str:
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    sync_status = sync_status_for(state)
    lines = [
        "# Handoff",
        "",
        "## Summary",
        f"- Work: `{work_dir.name}`",
        f"- Branch: `{git_branch(state.target_root)}`",
        f"- Git SHA: `{git_sha(state.target_root)}`",
        f"- Dirty: `{str(git_dirty(state.target_root)).lower()}`",
        f"- Sync status: `{sync_status}`",
        "",
        "## Context",
    ]
    lines.extend(
        [f"- {item}" for item in notes_by_kinds(events, ("context", "background"))]
        or ["- None recorded."]
    )
    lines.extend(["", "## Plan"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "plan")] or ["- None recorded."]
    )
    lines.extend(["", "## Decisions and spec reflection"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "decision")]
        or ["- None recorded."]
    )
    spec_impact = notes_by_kind(events, "spec-impact")
    if spec_impact:
        lines.extend([f"  - Spec: {item}" for item in spec_impact])
    lines.extend(["", "## Learning"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "learning")]
        or ["- None recorded."]
    )
    lines.extend(["", "## Gaps"])
    lines.extend(
        [f"- {item}" for item in notes_by_kind(events, "gap")] or ["- None recorded."]
    )
    lines.extend(["", "## Validation evidence"])
    if evidence:
        for record in evidence:
            transcript = (
                f" — `{record.transcript_path}`" if record.transcript_path else ""
            )
            why = f" — validates: {record.why}" if record.why else ""
            lines.append(
                f"- `{record.command_display}`: {record.status} (exit {record.exit_code}){why}{transcript}"
            )
    else:
        lines.append("- No validation evidence recorded.")
    lines.extend(["", "## Readiness"])
    readiness = ready_for_work(work_dir, state, check_handoff=False)
    lines.append(f"- Status: `{readiness.status}`")
    for check in readiness.checks:
        lines.append(f"- {check.id}: {check.status} — {check.message}")
    lines.extend(["", "## Review"])
    reviews = review_events(events)
    if reviews:
        for review in reviews:
            raw_rubrics = review.get("rubrics", [])
            rubrics_list = raw_rubrics if isinstance(raw_rubrics, list) else []
            rubrics = ", ".join(str(item) for item in rubrics_list)
            lines.append(
                f"- {review.get('backend')} / {review.get('reviewer')} ({rubrics}): {review.get('summary')} [{review.get('disposition')}]"
            )
    else:
        lines.append("- None recorded.")
    skips = [event.data for event in events if event.type == "dangerous_skip_added"]
    if skips:
        lines.extend(["", "## Dangerous skips"])
        for skip in skips:
            lines.append(f"- {skip.get('check')}: {skip.get('reason')}")
    return "\n".join(lines) + "\n"


def add_review(
    target: Path,
    *,
    backend: str,
    reviewer: str,
    rubrics: tuple[str, ...],
    summary: str,
    disposition: str = "accepted",
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
    record = append_event(
        work_dir,
        "review_added",
        {
            "backend": backend.strip(),
            "reviewer": reviewer.strip(),
            "rubrics": clean_rubrics,
            "summary": summary.strip(),
            "disposition": disposition.strip() or "accepted",
        },
    )
    return ReviewResult(
        work_id=work_dir.name,
        seq=record.seq,
        backend=backend.strip(),
        reviewer=reviewer.strip(),
        rubrics=clean_rubrics,
        summary=summary.strip(),
        disposition=disposition.strip() or "accepted",
    )


def add_dangerous_skip(
    target: Path,
    *,
    check: str,
    reason: str,
    no_local_files: bool = False,
) -> NoteResult:
    if check not in {"review", "validation"}:
        raise LocalWorkflowError("dangerously-skip supports: review, validation")
    if not reason.strip():
        raise LocalWorkflowError("dangerously-skip requires --reason")
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    record = append_event(
        work_dir,
        "dangerous_skip_added",
        {"check": check, "reason": reason.strip()},
    )
    return NoteResult(work_id=work_dir.name, seq=record.seq, kind=check, text=reason)


def ready(target: Path, *, no_local_files: bool = False) -> ReadyResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    return ready_for_work(work_dir, state, check_handoff=True)


def ready_for_work(
    work_dir: Path, state: LocalState, *, check_handoff: bool = True
) -> ReadyResult:
    events = read_events(work_dir)
    evidence = read_evidence(work_dir)
    checks: list[ReadyCheck] = []

    def add_check(check_id: str, passed: bool, message: str) -> None:
        checks.append(
            ReadyCheck(
                id=check_id, status="pass" if passed else "fail", message=message
            )
        )

    context = notes_by_kinds(events, ("context", "background"))
    checks.append(
        ReadyCheck(
            id="context",
            status="info",
            message=(
                "context recorded"
                if context
                else "no context recorded; okay for trivial work, add hk context if it prevents rediscovery"
            ),
        )
    )
    add_check("plan", bool(notes_by_kind(events, "plan")), "plan recorded")
    has_decision = bool(notes_by_kind(events, "decision"))
    has_spec_reflection = bool(notes_by_kind(events, "spec-impact"))
    add_check(
        "decision",
        has_decision and has_spec_reflection,
        "decision and spec reflection recorded",
    )
    validation_skipped = bool(dangerous_skip_events(events, "validation"))
    passing_evidence_with_why = [
        record for record in evidence if record.why and record.status == "pass"
    ]
    failed_evidence_with_why = [
        record for record in evidence if record.why and record.status != "pass"
    ]
    add_check(
        "validation",
        bool(passing_evidence_with_why) or validation_skipped,
        "validation evidence with rationale recorded"
        if passing_evidence_with_why
        else "validation dangerously skipped"
        if validation_skipped
        else "validation evidence with rationale failed"
        if failed_evidence_with_why
        else "missing validation evidence with --why",
    )
    review_skipped = bool(dangerous_skip_events(events, "review"))
    reviews = accepted_review_events(events)
    recorded_reviews = review_events(events)
    add_check(
        "review",
        bool(reviews) or review_skipped,
        "external-enough review recorded"
        if reviews
        else "review dangerously skipped"
        if review_skipped
        else SELF_REVIEW_GUIDANCE
        if recorded_reviews
        else "missing accepted external-enough review record; run a separate reviewer/subagent with fresh context",
    )
    synced = sync_status_for(state) == "synced"
    add_check(
        "sync", synced, "sync checkpoint fresh" if synced else "sync checkpoint stale"
    )
    if check_handoff:
        try:
            render_handoff(work_dir, state)
        except Exception as e:  # pragma: no cover - defensive render check
            add_check("handoff", False, f"handoff render failed: {e}")
        else:
            add_check("handoff", True, "handoff renders")
    failed = [check for check in checks if check.status == "fail"]
    has_skips = bool(validation_skipped or review_skipped)
    status = (
        "ready"
        if not failed and not has_skips
        else "ready-with-dangerous-skips"
        if not failed
        else "not-ready"
    )
    return ReadyResult(
        work_id=work_dir.name,
        ready=not failed,
        status=status,
        checks=checks,
    )


def materialize_work(target: Path, *, no_local_files: bool = False) -> HandoffResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    events = read_events(work_dir)
    views = work_dir / "views"
    views.mkdir(exist_ok=True)
    for filename, kinds, title in (
        ("plan.md", ("plan",), "Plan"),
        ("learning-log.md", ("learning",), "Learning Log"),
        ("decisions.md", ("decision",), "Decisions"),
        ("context.md", ("context", "background"), "Context"),
        ("background.md", ("context", "background"), "Context"),
        ("gaps.md", ("gap",), "Gaps"),
    ):
        items = notes_by_kinds(events, kinds)
        content = f"# {title}\n\n" + "\n".join(f"- {item}" for item in items)
        if not items:
            content += "None recorded."
        (views / filename).write_text(content + "\n")
    handoff = render_handoff(work_dir, state)
    path = views / "handoff.md"
    path.write_text(handoff)
    return HandoffResult(work_id=work_dir.name, content=handoff, path=str(path))


def handoff(
    target: Path, *, output_path: Path | None = None, no_local_files: bool = False
) -> HandoffResult:
    state = ensure_state(target, no_local_files=no_local_files)
    work_dir = require_work(state)
    content = render_handoff(work_dir, state)
    path_text = ""
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content)
        path_text = str(output_path)
    return HandoffResult(work_id=work_dir.name, content=content, path=path_text)


def init_spec(target: Path, *, no_local_files: bool = False) -> SpecResult:
    state = resolve_local_state(target, no_local_files=no_local_files)
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    if committed.exists():
        return SpecResult(spec_path=str(committed), source="committed", created=False)
    if root_committed.exists():
        return SpecResult(
            spec_path=str(root_committed), source="committed", created=False
        )

    state = ensure_state(target, no_local_files=no_local_files)
    spec_path = state.state_dir / "spec" / "SPEC.md"
    created = not spec_path.exists()
    if created:
        spec_path.parent.mkdir(parents=True, exist_ok=True)
        spec_path.write_text(
            "# Local Project Specification\n\n"
            "Status: local draft\n\n"
            "## Summary\n\nTODO\n\n"
            "## Invariants\n\nTODO\n\n"
            "## Validation Contract\n\nTODO\n"
        )
    return SpecResult(spec_path=str(spec_path), source="local", created=created)


def spec_status(target: Path, *, no_local_files: bool = False) -> SpecResult:
    state = resolve_local_state(target, no_local_files=no_local_files)
    committed = state.target_scope / "SPEC.md"
    root_committed = state.target_root / "SPEC.md"
    local = state.state_dir / "spec" / "SPEC.md"
    if committed.exists():
        return SpecResult(spec_path=str(committed), source="committed")
    if root_committed.exists():
        return SpecResult(spec_path=str(root_committed), source="committed")
    if local.exists():
        return SpecResult(spec_path=str(local), source="local")
    raise LocalWorkflowError(
        "No SPEC found. Run `hk spec init --local` to create a local draft."
    )


def spec_outline(target: Path, *, no_local_files: bool = False) -> SpecOutline:
    status = spec_status(target, no_local_files=no_local_files)
    path = Path(status.spec_path)
    headings = [
        line.strip() for line in path.read_text().splitlines() if line.startswith("#")
    ]
    return SpecOutline(
        spec_path=status.spec_path, source=status.source, headings=headings
    )


def spec_promote_dry_run(target: Path, *, no_local_files: bool = False) -> str:
    status = spec_status(target, no_local_files=no_local_files)
    if status.source == "committed":
        return f"Committed SPEC already exists: {status.spec_path}\n"
    target_path = git_root(target.resolve()) / "SPEC.md"
    content = Path(status.spec_path).read_text()
    return f"Would write local spec to {target_path}\n\n--- SPEC.md ---\n{content}"


def json_dump_dataclass(value: JsonDataclass) -> str:
    return json.dumps(asdict(value), indent=2, sort_keys=True)


def json_dump_object(value: object) -> str:
    return json.dumps(value, indent=2, sort_keys=True)


def print_capture_and_exit(result: CaptureResult) -> None:
    print(json_dump_dataclass(result))
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)
