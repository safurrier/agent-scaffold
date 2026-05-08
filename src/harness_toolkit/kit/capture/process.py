"""Process execution adapter for command evidence capture."""

from __future__ import annotations

import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

from harness_toolkit.kit.capture.redaction import redact_text


@dataclass(frozen=True)
class ProcessCaptureResult:
    exit_code: int
    duration_ms: int


def run_process_to_transcript(
    popen_args: str | list[str],
    *,
    cwd: Path,
    use_shell: bool,
    transcript: Path,
    no_log: bool,
    raw_log: bool,
    stream_to_stderr: bool,
) -> ProcessCaptureResult:
    start_time = time.monotonic()
    try:
        process = subprocess.Popen(
            popen_args,
            cwd=cwd,
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
    return ProcessCaptureResult(
        exit_code=exit_code, duration_ms=int((time.monotonic() - start_time) * 1000)
    )
