"""Built-in command/transcript redaction for HK evidence capture."""

from __future__ import annotations

import re

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
