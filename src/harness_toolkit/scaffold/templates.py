"""Jinja2-backed template engine for harness-scaffold.

Two public functions:
- render_template(src, context) → rendered string
- copy_tree(src_dir, dst_dir, context) → recursively copy + render
"""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined


def render_template(src: Path, context: dict[str, Any]) -> str:
    """Render a Jinja2 template file and return the result as a string."""
    env = Environment(
        loader=FileSystemLoader(str(src.parent)),
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template(src.name)
    return template.render(**context)


def render_string(source: str, context: dict[str, Any]) -> str:
    """Render a Jinja2 template string and return the result."""
    env = Environment(
        undefined=StrictUndefined,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    return env.from_string(source).render(**context)


def copy_tree(src: Path, dst: Path, context: dict[str, Any]) -> None:
    """Recursively copy *src* into *dst*, rendering .tmpl files via Jinja2.

    - Files ending in .tmpl are rendered and written without the .tmpl suffix.
    - Other text files are copied verbatim.
    - Binary files (UnicodeDecodeError) are copied byte-for-byte.
    """
    for item in src.rglob("*"):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        if item.suffix == ".tmpl":
            target = dst / rel.with_suffix("")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_template(item, context))
        else:
            target = dst / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            try:
                target.write_text(item.read_text())
            except UnicodeDecodeError:
                shutil.copy2(item, target)
