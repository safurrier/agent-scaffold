"""Internal Git subprocess adapter for Harness Kit.

This module is the seam for trusted Git queries used by HK internals. It is
intentionally separate from ``capture.process``, which captures arbitrary
user/agent commands as product evidence.
"""

from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class GitCommandResult:
    argv: tuple[str, ...]
    cwd: Path
    returncode: int
    stdout: bytes
    stderr: bytes

    @property
    def stdout_text(self) -> str:
        return self.stdout.decode("utf-8", errors="surrogateescape")

    @property
    def stderr_text(self) -> str:
        return self.stderr.decode("utf-8", errors="surrogateescape")


@dataclass(frozen=True)
class GitWorktreeInfo:
    repo_root: Path
    git_dir: Path
    git_common_dir: Path


class GitClient:
    """Small semantic adapter for internal Git calls."""

    def _probe_path(self, target: Path) -> Path | None:
        probe = target
        if probe.exists() and not probe.is_dir():
            probe = probe.parent
        while not probe.exists() and probe != probe.parent:
            probe = probe.parent
        if not probe.is_dir():
            return None
        return probe

    def _env(self) -> dict[str, str]:
        env = os.environ.copy()
        for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE"):
            env.pop(name, None)
        return env

    def run(self, cwd: Path, args: tuple[str, ...] | list[str]) -> GitCommandResult:
        probe = self._probe_path(cwd)
        argv = ("git", *tuple(args))
        if probe is None:
            return GitCommandResult(
                argv=argv,
                cwd=cwd,
                returncode=1,
                stdout=b"",
                stderr=f"not a directory: {cwd}".encode(),
            )
        try:
            result = subprocess.run(
                [*argv],
                cwd=probe,
                capture_output=True,
                check=False,
                env=self._env(),
            )
        except OSError as error:
            return GitCommandResult(
                argv=argv,
                cwd=probe,
                returncode=1,
                stdout=b"",
                stderr=str(error).encode(),
            )
        return GitCommandResult(
            argv=argv,
            cwd=probe,
            returncode=result.returncode,
            stdout=result.stdout,
            stderr=result.stderr,
        )

    def root(self, path: Path) -> Path | None:
        result = self.run(path, ("rev-parse", "--show-toplevel"))
        if result.returncode != 0:
            return None
        text = result.stdout_text.strip()
        return Path(text).resolve() if text else None

    def root_result(self, path: Path) -> GitCommandResult:
        return self.run(path, ("rev-parse", "--show-toplevel"))

    def branch(self, path: Path) -> str:
        result = self.run(path, ("symbolic-ref", "--quiet", "--short", "HEAD"))
        return result.stdout_text.strip() if result.returncode == 0 else ""

    def remote_origin_url(self, path: Path) -> str:
        result = self.run(path, ("config", "--get", "remote.origin.url"))
        return result.stdout_text.strip() if result.returncode == 0 else ""

    def sha_short(self, path: Path) -> str:
        result = self.run(path, ("rev-parse", "--short", "HEAD"))
        return result.stdout_text.strip() if result.returncode == 0 else ""

    def git_path(self, path: Path, git_path: str) -> Path | None:
        result = self.run(path, ("rev-parse", "--git-path", git_path))
        if result.returncode != 0:
            return None
        text = result.stdout_text.strip()
        if not text:
            return None
        resolved = Path(text)
        return resolved if resolved.is_absolute() else result.cwd / resolved

    def worktree_info(self, path: Path) -> GitWorktreeInfo | None:
        repo_root = self.root(path)
        git_dir = self.run(
            path,
            ("rev-parse", "--path-format=absolute", "--git-dir"),
        )
        common_dir = self.run(
            path,
            ("rev-parse", "--path-format=absolute", "--git-common-dir"),
        )
        if repo_root is None or git_dir.returncode != 0 or common_dir.returncode != 0:
            return None
        git_dir_text = git_dir.stdout_text.strip()
        common_text = common_dir.stdout_text.strip()
        if not git_dir_text or not common_text:
            return None
        return GitWorktreeInfo(
            repo_root=repo_root,
            git_dir=Path(git_dir_text).resolve(strict=False),
            git_common_dir=Path(common_text).resolve(strict=False),
        )

    def status_porcelain(self, path: Path, pathspec: tuple[str, ...] = ()) -> str:
        result = self.run(path, ("status", "--porcelain", *pathspec))
        output = result.stdout if result.returncode == 0 else b""
        return output.decode("utf-8", errors="surrogateescape")

    def ls_files(
        self,
        path: Path,
        pathspec: tuple[str, ...] = (),
        *,
        others: bool = False,
        exclude_standard: bool = False,
        nul: bool = False,
    ) -> GitCommandResult:
        args = ["ls-files"]
        if others:
            args.append("--others")
        if exclude_standard:
            args.append("--exclude-standard")
        if nul:
            args.append("-z")
        args.extend(pathspec)
        return self.run(path, tuple(args))

    def ls_tracked(self, path: Path, candidate: str) -> list[str]:
        result = self.ls_files(path, ("--", candidate))
        if result.returncode != 0:
            return []
        return [line for line in result.stdout_text.splitlines() if line.strip()]

    def ls_untracked(
        self, path: Path, pathspec: tuple[str, ...] = (), *, nul: bool = False
    ) -> bytes | list[str]:
        result = self.ls_files(
            path,
            pathspec,
            others=True,
            exclude_standard=True,
            nul=nul,
        )
        if result.returncode != 0:
            return b"" if nul else []
        if nul:
            return result.stdout
        return [
            line.strip() for line in result.stdout_text.splitlines() if line.strip()
        ]

    def diff_binary(self, path: Path, args: tuple[str, ...] = ()) -> GitCommandResult:
        return self.run(path, ("diff", "--no-ext-diff", "--binary", *args))

    def diff_name_only(self, path: Path, args: tuple[str, ...] = ()) -> list[str]:
        result = self.run(path, ("diff", "--name-only", *args))
        if result.returncode != 0:
            return []
        return [
            line.strip() for line in result.stdout_text.splitlines() if line.strip()
        ]


DEFAULT_GIT_CLIENT = GitClient()
