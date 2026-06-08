"""Cyclopts CLI entry point for harness-scaffold."""

from __future__ import annotations

import os
import sys
from importlib.metadata import version
from pathlib import Path
from typing import Literal

from cyclopts import App

from harness_toolkit.names import DISTRIBUTION_NAME, SCAFFOLD_COMMAND
from harness_toolkit.scaffold.config import Config, validate_module_name, validate_name

Shape = Literal["single", "apps"]
Stack = Literal["python", "go", "rust", "web"]

cli = App(
    name=SCAFFOLD_COMMAND,
    help="Starter-template CLI for the Harness Engineering Toolkit.",
    version=lambda: version(DISTRIBUTION_NAME),
)


def print_error(message: str) -> None:
    print(f"Error: {message}", file=sys.stderr)


@cli.command(
    help_epilogue=(
        "Examples:\n"
        f"  {SCAFFOLD_COMMAND} init --non-interactive --name myapp --shape single --stack python\n"
        f"  {SCAFFOLD_COMMAND} init --non-interactive --name platform --shape apps --stack go --modules api,worker\n"
        f"  {SCAFFOLD_COMMAND} init --non-interactive --name dashboard --shape single --stack web"
    )
)
def init(
    *,
    non_interactive: bool = False,
    name: str | None = None,
    shape: Shape | None = None,
    stack: Stack | None = None,
    modules: str | None = None,
    description: str | None = None,
    author_name: str | None = None,
    author_email: str | None = None,
    go_module: str | None = None,
    no_hooks: bool = False,
    no_examples: bool = False,
    debug: bool = False,
) -> None:
    """Initialize harness-scaffold into a project.

    Parameters
    ----------
    non_interactive
        Run without prompts. Requires --name, --shape, and --stack.
    name
        Project name: lowercase letters, digits, and hyphens.
    shape
        Repo shape to generate.
    stack
        Language stack to generate.
    modules
        Comma-separated module names for apps shape.
    description
        Project description.
    author_name
        Author name for generated metadata.
    author_email
        Author email for generated metadata.
    go_module
        Go module path for Go stack.
    no_hooks
        Skip pre-commit hook installation.
    no_examples
        Remove generated example code.
    debug
        Show tracebacks instead of short errors.
    """
    debug_enabled = debug or os.environ.get("HARNESS_SCAFFOLD_DEBUG") == "1"
    try:
        if non_interactive:
            config = _build_non_interactive_config(
                name=name,
                shape=shape,
                stack=stack,
                modules=modules,
                description=description,
                author_name=author_name,
                author_email=author_email,
                go_module=go_module,
                no_hooks=no_hooks,
                no_examples=no_examples,
            )
        else:
            from harness_toolkit.scaffold.prompts import gather_interactive

            config = gather_interactive()

        root = Path(os.environ.get("MISE_PROJECT_ROOT", Path.cwd()))

        from harness_toolkit.scaffold.init import run_init

        run_init(root, config)
    except Exception as e:
        if debug_enabled:
            raise
        print_error(f"Init failed: {e}" if not isinstance(e, ValueError) else str(e))
        raise SystemExit(1) from e


def _build_non_interactive_config(
    *,
    name: str | None,
    shape: Shape | None,
    stack: Stack | None,
    modules: str | None,
    description: str | None,
    author_name: str | None,
    author_email: str | None,
    go_module: str | None,
    no_hooks: bool,
    no_examples: bool,
) -> Config:
    """Validate CLI args and build a Config."""
    missing = []
    if not name:
        missing.append("--name")
    if not shape:
        missing.append("--shape")
    if not stack:
        missing.append("--stack")
    if missing:
        raise ValueError(f"Missing required flags: {', '.join(missing)}")

    assert name is not None
    assert shape is not None
    assert stack is not None
    validate_name(name)

    module_list: list[str] = []
    if modules:
        module_list = [
            validate_module_name(m.strip()) for m in modules.split(",") if m.strip()
        ]

    resolved_go_module = go_module or ""
    if stack == "go" and not resolved_go_module:
        resolved_go_module = f"github.com/your-org/{name}"

    return Config(
        name=name,
        description=description or f"A {name} project",
        shape=shape,
        stack=stack,
        modules=module_list,
        author_name=author_name or "",
        author_email=author_email or "",
        go_module=resolved_go_module,
        install_hooks=not no_hooks,
        keep_examples=not no_examples,
    )


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
