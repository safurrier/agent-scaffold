"""Click CLI for the Historical Reddit Simulator."""

from __future__ import annotations

import json
import sys

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from reddit_simulator.eras import ERAS, list_eras
from reddit_simulator.renderer import REDDIT_THEME, render_session
from reddit_simulator.validator import validate_session


@click.group()
def cli() -> None:
    """Historical Reddit Simulator — browse history like it's Reddit."""


@cli.command("list-eras")
def cmd_list_eras() -> None:
    """List all available historical eras."""
    console = Console(theme=REDDIT_THEME)
    console.print("\n[bold white]Available Historical Eras[/]\n")
    for key, name, event in list_eras():
        console.print(f"  [bold orange1]{key:<20}[/]  [grey89]{name}[/]")
        console.print(f"  {'':20}  [grey50]{event}[/]")
        console.print()


@cli.command("generate")
@click.option(
    "--era",
    "-e",
    default="pompeii",
    show_default=True,
    help=f"Historical era key. Available: {', '.join(ERAS.keys())}",
)
@click.option(
    "--seed", "-s", type=int, default=None, help="Random seed for reproducibility."
)
@click.option(
    "--posts",
    "-p",
    type=int,
    default=6,
    show_default=True,
    help="Target number of posts.",
)
@click.option(
    "--show-personas", is_flag=True, default=False, help="Show the persona list."
)
@click.option(
    "--validate",
    is_flag=True,
    default=False,
    help="Run validation checks after generation.",
)
@click.option(
    "--save", type=click.Path(), default=None, help="Save session JSON to a file."
)
@click.option("--api-key", envvar="ANTHROPIC_API_KEY", help="Anthropic API key.")
def cmd_generate(
    era: str,
    seed: int | None,
    posts: int,
    show_personas: bool,
    validate: bool,
    save: str | None,
    api_key: str | None,
) -> None:
    """Generate a historical Reddit session and display it."""
    # Lazy import to keep startup fast and avoid import errors when API unavailable
    from reddit_simulator.generator import generate_session

    console = Console(theme=REDDIT_THEME)
    err_console = Console(theme=REDDIT_THEME, stderr=True)

    if not api_key:
        err_console.print(
            "[bold red]Error:[/] No API key found. Set ANTHROPIC_API_KEY or use --api-key.",
        )
        sys.exit(1)

    if era not in ERAS:
        available = ", ".join(ERAS.keys())
        err_console.print(
            f"[bold red]Error:[/] Unknown era '{era}'. Available: {available}",
        )
        sys.exit(1)

    session = None

    def on_progress(msg: str) -> None:
        pass  # handled by spinner

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=Console(stderr=True),
        transient=True,
    ) as progress:
        task = progress.add_task(f"Generating {ERAS[era]['name']}...", total=None)

        try:
            session = generate_session(
                era_key=era,
                seed=seed,
                num_posts=posts,
                api_key=api_key,
            )
        except Exception as e:
            progress.stop()
            err_console.print(f"[bold red]Error during generation:[/] {e}")
            sys.exit(1)

        progress.update(task, description="Rendering...")

    render_session(session, console=console, show_personas=show_personas)

    if validate:
        result = validate_session(session, era)
        console.print()
        status_style = "bold green" if result.passed else "bold yellow"
        console.print(f"[{status_style}]Validation:[/]")
        console.print(result.summary())

    if save:
        _save_session(session, save)
        console.print(f"\n[grey50]Session saved to {save}[/]")


@cli.command("validate")
@click.argument("session_file", type=click.Path(exists=True))
@click.option(
    "--era", "-e", required=True, help="Era key the session was generated with."
)
def cmd_validate(session_file: str, era: str) -> None:
    """Validate a previously saved session JSON file."""
    from reddit_simulator.models import Comment, Persona, Post, Reply, Session

    console = Console(theme=REDDIT_THEME)

    with open(session_file) as f:
        data = json.load(f)

    # Reconstruct session from JSON
    personas = [
        Persona(
            username=p["username"],
            traits=p["traits"],
            background=p.get("background", ""),
        )
        for p in data.get("personas", [])
    ]
    posts = []
    for i, p in enumerate(data.get("posts", [])):
        comments = []
        for c in p.get("comments", []):
            replies = [Reply(**r) for r in c.get("replies", [])]
            comments.append(
                Comment(
                    author=c["author"],
                    content=c["content"],
                    score=c.get("score", 0),
                    replies=replies,
                )
            )
        posts.append(
            Post(
                id=p.get("id", f"p{i}"),
                title=p["title"],
                author=p["author"],
                timestamp=p.get("timestamp", ""),
                content=p.get("content", ""),
                score=p.get("score", 0),
                comments=comments,
            )
        )
    session = Session(
        era=data.get("era", ""),
        event=data.get("event", ""),
        posts=posts,
        personas=personas,
        seed=data.get("seed"),
    )

    result = validate_session(session, era)
    console.print(result.summary())
    sys.exit(0 if result.passed else 1)


def _save_session(session, path: str) -> None:
    """Serialize session to JSON and write to disk."""
    data = {
        "era": session.era,
        "event": session.event,
        "seed": session.seed,
        "personas": [
            {"username": p.username, "traits": p.traits, "background": p.background}
            for p in session.personas
        ],
        "posts": [
            {
                "id": post.id,
                "title": post.title,
                "author": post.author,
                "timestamp": post.timestamp,
                "content": post.content,
                "score": post.score,
                "comments": [
                    {
                        "author": c.author,
                        "content": c.content,
                        "score": c.score,
                        "replies": [
                            {"author": r.author, "content": r.content, "score": r.score}
                            for r in c.replies
                        ],
                    }
                    for c in post.comments
                ],
            }
            for post in session.posts
        ],
    }
    with open(path, "w") as f:
        json.dump(data, f, indent=2)
