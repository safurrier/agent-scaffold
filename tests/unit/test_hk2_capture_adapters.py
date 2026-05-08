from __future__ import annotations

import sys
from pathlib import Path

import pytest

from harness_toolkit.kit.capture.process import run_process_to_transcript
from harness_toolkit.kit.capture.redaction import redact_argv, redact_text
from harness_toolkit.kit.capture.transcripts import transcript_path

pytestmark = pytest.mark.unit


def test_redaction_masks_secret_text_and_arguments() -> None:
    assert redact_text("token=supersecretvalue", raw_log=False) == "token=[REDACTED]"
    assert redact_argv(["--token", "supersecretvalue"], raw_log=False) == [
        "--token",
        "[REDACTED]",
    ]
    assert redact_argv(["--token=supersecretvalue"], raw_log=False) == [
        "--token=[REDACTED]"
    ]


def test_raw_log_keeps_secret_text_and_arguments() -> None:
    assert (
        redact_text("token=supersecretvalue", raw_log=True) == "token=supersecretvalue"
    )
    assert redact_argv(["--token", "supersecretvalue"], raw_log=True) == [
        "--token",
        "supersecretvalue",
    ]


def test_process_adapter_writes_redacted_transcript(tmp_path: Path) -> None:
    transcript = tmp_path / "command.log"

    result = run_process_to_transcript(
        [sys.executable, "-c", "print('token=supersecretvalue')"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
    )

    assert result.exit_code == 0
    assert "token=[REDACTED]" in transcript.read_text()


def test_transcript_path_is_under_work_artifacts(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"

    assert (
        transcript_path(work_dir, "ev_1")
        == work_dir / "artifacts" / "ev_1.transcript.log"
    )
