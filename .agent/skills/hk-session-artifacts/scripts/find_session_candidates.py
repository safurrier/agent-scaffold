#!/usr/bin/env python3
"""List likely Pi, Claude, or Codex session transcript candidates as JSON.

This helper is intentionally discovery-only. It does not attach artifacts and it
never chooses a candidate for the caller. Agents should inspect the output and
then call `hk artifact attach --path ...` with an exact path.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal

Source = Literal["pi", "claude", "codex"]


@dataclass(frozen=True)
class Candidate:
    path: str
    size_bytes: int
    mtime: float
    reason: str
    confidence: str


def safe_project_key(path: Path) -> str:
    resolved = str(path.resolve())
    # Pi uses doubled hyphen sentinels and dots preserved in path segments.
    return "--" + resolved.strip("/").replace("/", "-") + "--"


def claude_project_key(path: Path) -> str:
    # Claude Code project dirs use one leading hyphen and replace path punctuation with hyphens.
    return "-" + re.sub(r"[^A-Za-z0-9]+", "-", str(path.resolve()).strip("/")).strip(
        "-"
    )


def iter_files(root: Path, pattern: str = "*.jsonl") -> list[Path]:
    if not root.exists():
        return []
    return [path for path in root.rglob(pattern) if path.is_file()]


def candidate(path: Path, *, reason: str, confidence: str) -> Candidate:
    stat = path.stat()
    return Candidate(
        path=str(path),
        size_bytes=stat.st_size,
        mtime=stat.st_mtime,
        reason=reason,
        confidence=confidence,
    )


def pi_session_root() -> Path:
    override = os.environ.get("PI_CODING_AGENT_SESSION_DIR")
    if override:
        return Path(override).expanduser()
    return Path.home() / ".pi" / "agent" / "sessions"


def pi_candidates(target: Path) -> list[Candidate]:
    root = pi_session_root()
    scoped = root / safe_project_key(target)
    paths = iter_files(scoped)
    rows = [
        candidate(
            path,
            reason="repo-scoped Pi session directory; verify this is the intended session before attaching",
            confidence="medium",
        )
        for path in paths
    ]
    if not rows:
        rows = [
            candidate(
                path,
                reason="global Pi session search fallback; low confidence because repo scope did not match",
                confidence="low",
            )
            for path in iter_files(root)
        ]
    return rows


def claude_candidates(target: Path) -> list[Candidate]:
    root = Path.home() / ".claude" / "projects"
    scoped = root / claude_project_key(target)
    rows = [
        candidate(
            path,
            reason="repo-scoped Claude project session; verify session id or timestamp before attaching",
            confidence="medium",
        )
        for path in iter_files(scoped)
    ]
    if not rows:
        rows = [
            candidate(
                path,
                reason="global Claude project search fallback; low confidence because repo scope did not match",
                confidence="low",
            )
            for path in iter_files(root)
        ]
    return rows


def codex_candidates(target: Path) -> list[Candidate]:
    _ = target
    root = Path.home() / ".codex" / "sessions"
    return [
        candidate(
            path,
            reason="Codex persisted session; match by run time or session id before attaching",
            confidence="low",
        )
        for path in iter_files(root)
    ]


def load_jsonl_first_line(path: Path) -> object | None:
    try:
        with path.open("r", encoding="utf-8", errors="replace") as file_obj:
            for line in file_obj:
                if line.strip():
                    return json.loads(line)
    except (OSError, json.JSONDecodeError):
        return None
    return None


def include_matching_text(rows: list[Candidate], text: str) -> list[Candidate]:
    if not text:
        return rows
    needle = text.lower()
    filtered: list[Candidate] = []
    for row in rows:
        haystack = row.path.lower()
        first = load_jsonl_first_line(Path(row.path))
        if first is not None:
            haystack += "\n" + json.dumps(first, sort_keys=True).lower()
        if needle in haystack:
            filtered.append(row)
    return filtered


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", choices=("pi", "claude", "codex"), required=True)
    parser.add_argument("--target", type=Path, default=Path("."))
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument(
        "--match",
        default="",
        help="Optional substring matched against candidate path and first JSONL row.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    finders = {
        "pi": pi_candidates,
        "claude": claude_candidates,
        "codex": codex_candidates,
    }
    rows = finders[args.source](args.target)
    rows = include_matching_text(rows, args.match)
    rows.sort(key=lambda row: row.mtime, reverse=True)
    limit = max(args.limit, 0)
    warnings = [
        "Discovery is heuristic. Prefer an exact transcript path provided by the harness/tool when available.",
        "Do not attach global latest sessions without confirming timestamp, repo scope, prompt, or session id.",
    ]
    print(
        json.dumps(
            {
                "source": args.source,
                "target": str(args.target.resolve()),
                "warnings": warnings,
                "candidates": [asdict(row) for row in rows[:limit]],
            },
            indent=2,
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
