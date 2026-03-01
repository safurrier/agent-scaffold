"""Interactive prompting for agent-scaffold init."""

from __future__ import annotations

import click

from agent_scaffold.config import (
    PLANNED_STACKS,
    SUPPORTED_SHAPES,
    SUPPORTED_STACKS,
    Config,
    validate_name,
)


def gather_interactive() -> Config:
    """Prompt the user for all project configuration fields."""
    click.echo("\n── agent-scaffold init ──\n")

    # Project name
    name = ""
    while not name:
        raw = click.prompt("  Project name")
        try:
            name = validate_name(raw.strip())
        except ValueError as e:
            click.secho(f"  Error: {e}", fg="red", err=True)

    description = click.prompt("  Description", default=f"A {name} project")

    shape = _choice_prompt("Repo shape", list(SUPPORTED_SHAPES), default="single")

    click.echo(f"\n  (Planned stacks not yet available: {', '.join(PLANNED_STACKS)})")
    stack = _choice_prompt("Stack", list(SUPPORTED_STACKS), default="python")

    modules: list[str] = []
    if shape == "apps":
        click.echo("\n  Enter module names (comma-separated), e.g.: api,worker")
        raw_modules = click.prompt("  Modules", default="app")
        modules = [m.strip() for m in raw_modules.split(",") if m.strip()]

    author_name = click.prompt("  Author name", default="")
    author_email = click.prompt("  Author email", default="")

    go_module = ""
    if stack == "go":
        default_mod = f"github.com/{author_name or 'your-org'}/{name}"
        go_module = click.prompt("  Go module path", default=default_mod)

    install_hooks = (
        _choice_prompt("Install pre-commit hooks?", ["yes", "no"], "yes") == "yes"
    )
    keep_examples = _choice_prompt("Keep example code?", ["yes", "no"], "yes") == "yes"

    return Config(
        name=name,
        description=description,
        shape=shape,
        stack=stack,
        modules=modules,
        author_name=author_name,
        author_email=author_email,
        go_module=go_module,
        install_hooks=install_hooks,
        keep_examples=keep_examples,
    )


def _choice_prompt(label: str, choices: list[str], default: str) -> str:
    click.echo(f"\n  {label}:")
    for i, c in enumerate(choices, 1):
        marker = " (default)" if c == default else ""
        click.echo(f"    {i}. {c}{marker}")
    while True:
        raw = click.prompt("  Choice", default=default)
        if raw in choices:
            return raw
        try:
            idx = int(raw) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
        except ValueError:
            pass
        click.secho(
            f"  Please choose from: {', '.join(choices)}", fg="yellow", err=True
        )
