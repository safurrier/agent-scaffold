from __future__ import annotations

import sys
from pathlib import Path

import pytest

from harness_toolkit.kit.capture.process import run_process_to_transcript
from harness_toolkit.kit.capture.redaction import redact_argv, redact_text
from harness_toolkit.kit.capture.transcripts import transcript_path


@pytest.mark.unit
def test_redaction_masks_secret_text_and_arguments() -> None:
    assert redact_text("token=supersecretvalue", raw_log=False) == "token=[REDACTED]"
    assert redact_argv(["--token", "supersecretvalue"], raw_log=False) == [
        "--token",
        "[REDACTED]",
    ]
    assert redact_argv(["--token=supersecretvalue"], raw_log=False) == [
        "--token=[REDACTED]"
    ]


@pytest.mark.unit
def test_raw_log_keeps_secret_text_and_arguments() -> None:
    assert (
        redact_text("token=supersecretvalue", raw_log=True) == "token=supersecretvalue"
    )
    assert redact_argv(["--token", "supersecretvalue"], raw_log=True) == [
        "--token",
        "supersecretvalue",
    ]


@pytest.mark.integration
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


@pytest.mark.integration
def test_process_adapter_times_out_and_records_marker(tmp_path: Path) -> None:
    transcript = tmp_path / "timeout.log"

    result = run_process_to_transcript(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
        timeout_seconds=1,
    )

    assert result.exit_code == 124
    assert result.timed_out is True
    assert "[hk command timed out]" in transcript.read_text()


@pytest.mark.integration
def test_process_adapter_preserves_timeout_marker_when_truncated(
    tmp_path: Path,
) -> None:
    transcript = tmp_path / "timeout-truncated.log"

    result = run_process_to_transcript(
        [
            "sh",
            "-c",
            "printf '%s' 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'; sleep 5",
        ],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
        timeout_seconds=1,
        max_log_bytes=20,
    )

    content = transcript.read_text()
    assert result.exit_code == 124
    assert result.timed_out is True
    assert result.truncated is True
    assert "[hk command timed out]" in content
    assert "[hk transcript truncated]" in content


@pytest.mark.integration
def test_process_adapter_streams_full_output_when_transcript_truncates(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = tmp_path / "streamed-truncated.log"

    result = run_process_to_transcript(
        [sys.executable, "-c", "print('abcdef')"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
        max_log_bytes=3,
    )

    assert result.exit_code == 0
    assert "abcdef" in capsys.readouterr().out
    assert "abc" in transcript.read_text()
    assert "def" not in transcript.read_text()
    assert "[hk transcript truncated]" in transcript.read_text()


@pytest.mark.integration
def test_process_adapter_truncates_transcript(tmp_path: Path) -> None:
    transcript = tmp_path / "truncated.log"

    result = run_process_to_transcript(
        [sys.executable, "-c", "print('x' * 200)"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
        max_log_bytes=20,
    )

    assert result.exit_code == 0
    assert result.truncated is True
    assert "[hk transcript truncated]" in transcript.read_text()


@pytest.mark.integration
def test_process_adapter_start_failure_streams_full_error_when_truncated(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    transcript = tmp_path / "missing.log"

    result = run_process_to_transcript(
        ["definitely-missing-hk-command"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=False,
        raw_log=False,
        stream_to_stderr=False,
        max_log_bytes=10,
    )

    assert result.exit_code == 127
    assert "failed to start command" in capsys.readouterr().out
    assert "failed to " in transcript.read_text()
    assert "[hk transcript truncated]" in transcript.read_text()


@pytest.mark.integration
def test_process_adapter_no_log_keeps_transcript_empty(tmp_path: Path) -> None:
    transcript = tmp_path / "no-log.log"

    result = run_process_to_transcript(
        [sys.executable, "-c", "print('token=supersecretvalue')"],
        cwd=tmp_path,
        use_shell=False,
        transcript=transcript,
        no_log=True,
        raw_log=False,
        stream_to_stderr=False,
    )

    assert result.exit_code == 0
    assert result.transcript_bytes == 0
    assert not transcript.exists()


@pytest.mark.unit
def test_transcript_path_is_under_work_artifacts(tmp_path: Path) -> None:
    work_dir = tmp_path / "work"

    assert (
        transcript_path(work_dir, "ev_1")
        == work_dir / "artifacts" / "ev_1.transcript.log"
    )
