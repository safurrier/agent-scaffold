"""Process execution adapter for command evidence capture."""

from __future__ import annotations

import codecs
import os
import selectors
import signal
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TextIO

from harness_toolkit.kit.capture.redaction import redact_text

TIMEOUT_EXIT_CODE = 124
TRUNCATION_MARKER = "\n[hk transcript truncated]\n"
TIMEOUT_MARKER = "\n[hk command timed out]\n"
READ_CHUNK_SIZE = 8192
LIVE_REDACTION_BUFFER_LIMIT = 64 * 1024
LIVE_SUPPRESSION_MARKER = (
    "\n[hk live output suppressed until whitespace/newline redaction boundary]\n"
)


@dataclass(frozen=True)
class ProcessCaptureResult:
    exit_code: int
    duration_ms: int
    timed_out: bool = False
    truncated: bool = False
    transcript_bytes: int = 0


def _append_capped(
    buffer: bytearray, chunk: bytes, *, max_log_bytes: int
) -> tuple[bytes, bool]:
    if max_log_bytes <= 0:
        buffer.extend(chunk)
        return chunk, False
    remaining = max_log_bytes - len(buffer)
    if remaining <= 0:
        return b"", True
    appended = chunk[:remaining]
    buffer.extend(appended)
    return appended, len(chunk) > remaining


def _render_output(
    output: bytes, *, raw_log: bool, timed_out: bool, truncated: bool
) -> tuple[str, int]:
    rendered = output.decode("utf-8", errors="replace")
    rendered = redact_text(rendered, raw_log=raw_log)
    if timed_out:
        rendered += TIMEOUT_MARKER
    if truncated:
        rendered += TRUNCATION_MARKER
    return rendered, len(rendered.encode("utf-8", errors="replace"))


def _terminate_process_group(process: subprocess.Popen[bytes]) -> None:
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except OSError:
        process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except OSError:
            process.kill()
        try:
            process.wait(timeout=1)
        except subprocess.TimeoutExpired:
            pass


class _StreamingRedactor:
    """Boundary-buffered live-output redactor.

    Redacting each os.read chunk independently can leak a secret suffix when a
    token crosses chunk boundaries. Buffer until a whitespace/control boundary so
    every non-raw live write sees enough context for secret redaction. If a
    command emits one huge delimiter-free token, suppress that token in live
    output instead of growing memory without bound; transcript capture remains
    governed by the separate transcript byte cap.
    """

    def __init__(self, *, raw_log: bool, stream_file: TextIO) -> None:
        self._raw_log = raw_log
        self._stream_file = stream_file
        self._decoder = codecs.getincrementaldecoder("utf-8")("replace")
        self._pending = ""
        self._suppressing = False
        self._suppression_reported = False

    @staticmethod
    def _last_boundary(value: str) -> int:
        for index in range(len(value) - 1, -1, -1):
            if value[index].isspace() or value[index] in {"\r", "\n"}:
                return index
        return -1

    def _emit(self, value: str) -> None:
        if not value:
            return
        print(
            redact_text(value, raw_log=False),
            end="",
            file=self._stream_file,
            flush=True,
        )

    def _report_suppression(self) -> None:
        if self._suppression_reported:
            return
        print(LIVE_SUPPRESSION_MARKER, end="", file=self._stream_file, flush=True)
        self._suppression_reported = True

    def _feed_redacted(self, rendered: str) -> None:
        if self._suppressing:
            boundary = self._last_boundary(rendered)
            if boundary < 0:
                return
            self._suppressing = False
            self._pending = rendered[boundary + 1 :]
        else:
            self._pending += rendered

        boundary = self._last_boundary(self._pending)
        if boundary >= 0:
            safe = self._pending[: boundary + 1]
            self._pending = self._pending[boundary + 1 :]
            self._emit(safe)

        if len(self._pending) > LIVE_REDACTION_BUFFER_LIMIT:
            self._report_suppression()
            self._pending = ""
            self._suppressing = True

    def feed(self, chunk: bytes) -> None:
        if not chunk:
            return
        rendered = self._decoder.decode(chunk, final=False)
        if self._raw_log:
            print(rendered, end="", file=self._stream_file, flush=True)
            return
        self._feed_redacted(rendered)

    def flush(self) -> None:
        rendered = self._decoder.decode(b"", final=True)
        if self._raw_log:
            if rendered:
                print(rendered, end="", file=self._stream_file, flush=True)
            return
        self._feed_redacted(rendered)
        if self._suppressing:
            self._suppressing = False
            self._pending = ""
            return
        if self._pending:
            self._emit(self._pending)
            self._pending = ""


def _read_available(
    fd: int,
    buffer: bytearray,
    *,
    max_log_bytes: int,
    stream_redactor: _StreamingRedactor,
    capture_output: bool,
) -> bool:
    any_truncated = False
    while True:
        try:
            chunk = os.read(fd, READ_CHUNK_SIZE)
        except BlockingIOError:
            break
        except OSError:
            break
        if not chunk:
            break
        stream_redactor.feed(chunk)
        if capture_output:
            _appended, truncated = _append_capped(
                buffer, chunk, max_log_bytes=max_log_bytes
            )
            any_truncated = any_truncated or truncated
    return any_truncated


def run_process_to_transcript(
    popen_args: str | list[str],
    *,
    cwd: Path,
    use_shell: bool,
    transcript: Path,
    no_log: bool,
    raw_log: bool,
    stream_to_stderr: bool,
    timeout_seconds: int = 0,
    max_log_bytes: int = 0,
) -> ProcessCaptureResult:
    start_time = time.monotonic()
    timed_out = False
    truncated = False
    transcript_bytes = 0
    output = bytearray()
    stream_file = sys.stderr if stream_to_stderr else sys.stdout
    stream_redactor = _StreamingRedactor(raw_log=raw_log, stream_file=stream_file)
    try:
        process = subprocess.Popen(
            popen_args,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=use_shell,
            start_new_session=True,
        )
    except OSError as e:
        message = f"failed to start command: {e}\n".encode()
        stream_redactor.feed(message)
        if not no_log:
            _appended, truncated = _append_capped(
                output, message, max_log_bytes=max_log_bytes
            )
        exit_code = 127
    else:
        assert process.stdout is not None
        fd = process.stdout.fileno()
        os.set_blocking(fd, False)
        selector = selectors.DefaultSelector()
        selector.register(process.stdout, selectors.EVENT_READ)
        deadline = time.monotonic() + timeout_seconds if timeout_seconds > 0 else None
        try:
            while True:
                for _key, _mask in selector.select(timeout=0.05):
                    truncated = (
                        _read_available(
                            fd,
                            output,
                            max_log_bytes=max_log_bytes,
                            stream_redactor=stream_redactor,
                            capture_output=not no_log,
                        )
                        or truncated
                    )
                if process.poll() is not None:
                    truncated = (
                        _read_available(
                            fd,
                            output,
                            max_log_bytes=max_log_bytes,
                            stream_redactor=stream_redactor,
                            capture_output=not no_log,
                        )
                        or truncated
                    )
                    exit_code = process.returncode
                    break
                if deadline is not None and time.monotonic() >= deadline:
                    timed_out = True
                    _terminate_process_group(process)
                    truncated = (
                        _read_available(
                            fd,
                            output,
                            max_log_bytes=max_log_bytes,
                            stream_redactor=stream_redactor,
                            capture_output=not no_log,
                        )
                        or truncated
                    )
                    exit_code = TIMEOUT_EXIT_CODE
                    break
        finally:
            selector.close()
            try:
                process.stdout.close()
            except OSError:
                pass
    rendered, transcript_bytes = _render_output(
        bytes(output), raw_log=raw_log, timed_out=timed_out, truncated=truncated
    )
    stream_redactor.flush()
    marker_text = ""
    if timed_out:
        marker_text += TIMEOUT_MARKER
    if truncated:
        marker_text += TRUNCATION_MARKER
    if marker_text:
        print(marker_text, end="", file=stream_file, flush=True)
    if not no_log:
        transcript.write_text(rendered)
    else:
        transcript_bytes = 0
    return ProcessCaptureResult(
        exit_code=exit_code,
        duration_ms=int((time.monotonic() - start_time) * 1000),
        timed_out=timed_out,
        truncated=truncated,
        transcript_bytes=transcript_bytes,
    )
