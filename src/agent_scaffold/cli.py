"""Click CLI entry point for agent-scaffold.

Usage:
  agent-scaffold init --non-interactive --name myapp --shape single --stack python
  agent-scaffold init   # interactive
"""

from __future__ import annotations

import os
from pathlib import Path

import click

from agent_scaffold.config import (
    SUPPORTED_SHAPES,
    SUPPORTED_STACKS,
    Config,
    validate_name,
)


@click.group()
@click.option("--debug/--no-debug", default=False, envvar="AGENT_SCAFFOLD_DEBUG")
@click.pass_context
def cli(ctx: click.Context, debug: bool) -> None:
    """agent-scaffold — opinionated starter for agent-driven engineering."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug


@cli.command()
@click.option("--non-interactive", is_flag=True, help="Run without prompts")
@click.option("--name", default=None, help="Project name (lowercase, hyphens)")
@click.option(
    "--shape",
    type=click.Choice(list(SUPPORTED_SHAPES)),
    default=None,
    help="Repo shape: single or apps",
)
@click.option(
    "--stack",
    type=click.Choice(list(SUPPORTED_STACKS)),
    default=None,
    help="Language stack: python or go",
)
@click.option(
    "--modules", default=None, help="Comma-separated module names (apps shape)"
)
@click.option("--description", default=None, help="Project description")
@click.option("--author-name", default=None, help="Author name")
@click.option("--author-email", default=None, help="Author email")
@click.option("--go-module", default=None, help="Go module path (go stack only)")
@click.option("--no-hooks", is_flag=True, help="Skip pre-commit hook installation")
@click.option("--no-examples", is_flag=True, help="Remove example code after init")
@click.pass_context
def init(
    ctx: click.Context,
    non_interactive: bool,
    name: str | None,
    shape: str | None,
    stack: str | None,
    modules: str | None,
    description: str | None,
    author_name: str | None,
    author_email: str | None,
    go_module: str | None,
    no_hooks: bool,
    no_examples: bool,
) -> None:
    """Initialize agent-scaffold into a project.

    \b
    Non-interactive:
      agent-scaffold init --non-interactive --name myapp --shape single --stack python

    Interactive:
      agent-scaffold init
    """
    debug: bool = ctx.obj["debug"]

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
            from agent_scaffold.prompts import gather_interactive

            config = gather_interactive()

        root = Path(os.environ.get("MISE_PROJECT_ROOT", Path.cwd()))

        from agent_scaffold.common import run_init

        run_init(root, config)

    except ValueError as e:
        raise click.ClickException(str(e)) from e
    except Exception as e:
        if debug:
            raise
        raise click.ClickException(f"Init failed: {e}") from e


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_non_interactive_config(
    *,
    name: str | None,
    shape: str | None,
    stack: str | None,
    modules: str | None,
    description: str | None,
    author_name: str | None,
    author_email: str | None,
    go_module: str | None,
    no_hooks: bool,
    no_examples: bool,
) -> Config:
    """Validate CLI args and build a Config; raise ClickException on errors."""
    missing = []
    if not name:
        missing.append("--name")
    if not shape:
        missing.append("--shape")
    if not stack:
        missing.append("--stack")
    if missing:
        raise click.ClickException(f"Missing required flags: {', '.join(missing)}")

    # validate_name raises ValueError on bad input
    validate_name(name)  # type: ignore[arg-type]

    module_list: list[str] = []
    if modules:
        module_list = [m.strip() for m in modules.split(",") if m.strip()]

    resolved_go_module = go_module or ""
    if stack == "go" and not resolved_go_module:
        resolved_go_module = f"github.com/your-org/{name}"

    return Config(
        name=name,  # type: ignore[arg-type]
        description=description or f"A {name} project",
        shape=shape,  # type: ignore[arg-type]
        stack=stack,  # type: ignore[arg-type]
        modules=module_list,
        author_name=author_name or "",
        author_email=author_email or "",
        go_module=resolved_go_module,
        install_hooks=not no_hooks,
        keep_examples=not no_examples,
    )
