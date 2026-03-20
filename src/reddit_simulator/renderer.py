"""Rich terminal renderer — displays sessions as Reddit-like UI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.text import Text
from rich.theme import Theme

from reddit_simulator.models import Comment, Post, Session

REDDIT_THEME = Theme(
    {
        "header": "bold white on dark_orange",
        "subreddit": "bold orange1",
        "score": "bold orange3",
        "score.low": "bold grey50",
        "author": "bold dodger_blue2",
        "timestamp": "grey50",
        "post.title": "bold white",
        "post.content": "grey89",
        "comment.author": "bold spring_green3",
        "comment.content": "grey89",
        "reply.author": "bold medium_purple1",
        "reply.content": "grey74",
        "separator": "grey30",
        "tag": "on dark_blue bold white",
        "warn": "bold yellow",
    }
)


def _score_str(score: int) -> Text:
    if score >= 100:
        t = Text(f"▲ {score:,}", style="score")
    elif score >= 10:
        t = Text(f"▲ {score}", style="score")
    else:
        t = Text(f"▲ {score}", style="score.low")
    return t


def _render_reply(reply, console: Console, *, prefix: str = "      │  ") -> None:
    author = Text(f"u/{reply.author}", style="reply.author")
    score = _score_str(reply.score)
    header = Text()
    header.append_text(score)
    header.append("  ")
    header.append_text(author)

    content = Text(reply.content, style="reply.content")

    console.print(f"{prefix}├─ ", end="")
    console.print(header)
    console.print(f"{prefix}│  ", end="")
    console.print(content)
    console.print(f"{prefix}│")


def _render_comment(comment: Comment, console: Console, *, indent: str = "   ") -> None:
    author = Text(f"u/{comment.author}", style="comment.author")
    score = _score_str(comment.score)

    header = Text()
    header.append("├─ ")
    header.append_text(score)
    header.append("  ")
    header.append_text(author)

    console.print(f"{indent}", end="")
    console.print(header)

    # Content lines
    for line in comment.content.split("\n"):
        console.print(f"{indent}│     ", end="")
        console.print(Text(line, style="comment.content"))

    if comment.replies:
        console.print(f"{indent}│")
        for reply in comment.replies:
            _render_reply(reply, console, prefix=f"{indent}│     ")
    else:
        console.print(f"{indent}│")


def _render_post(post: Post, console: Console, *, number: int = 1) -> None:
    # Score + title header
    score_text = _score_str(post.score)

    title_line = Text()
    title_line.append_text(score_text)
    title_line.append("  ")
    title_line.append(post.title, style="post.title")

    meta = Text()
    meta.append("       Posted by ", style="timestamp")
    meta.append(f"u/{post.author}", style="author")
    meta.append(f"  •  {post.timestamp}", style="timestamp")

    comment_count = len(post.comments) + sum(len(c.replies) for c in post.comments)
    comment_line = Text(
        f"       💬 {comment_count} comment{'s' if comment_count != 1 else ''}",
        style="timestamp",
    )

    console.print(title_line)
    console.print(meta)

    if post.content:
        console.print()
        for line in post.content.split("\n"):
            console.print(f"       {line}", style="post.content")

    console.print(comment_line)

    if post.comments:
        console.print()
        for comment in post.comments:
            _render_comment(comment, console)

    console.print(Rule(style="separator"))


def render_session(
    session: Session,
    *,
    console: Console | None = None,
    show_personas: bool = False,
    max_posts: int | None = None,
) -> None:
    """Render a session to the terminal using Rich.

    Args:
        session: The generated session to display.
        console: Optional Rich console. Creates a themed one if not provided.
        show_personas: Whether to show the persona list before posts.
        max_posts: Maximum number of posts to display.
    """
    if console is None:
        console = Console(theme=REDDIT_THEME)

    # Derive subreddit name from era
    era_short = session.era.split(",")[0].strip().replace(" ", "")
    subreddit = f"r/{era_short}"

    # Header panel
    header_text = Text()
    header_text.append(f"  {subreddit}", style="subreddit")
    header_text.append("  •  ", style="grey50")
    header_text.append(session.era, style="bold white")
    header_text.append("  •  ", style="grey50")
    header_text.append(session.event, style="bold orange1")
    if session.seed is not None:
        header_text.append(f"  •  seed={session.seed}", style="grey50")

    console.print()
    console.print(Panel(header_text, style="header", expand=True))
    console.print()

    # Persona list
    if show_personas:
        console.print(Text("Active users in this session:", style="bold grey70"))
        for persona in session.personas:
            traits = ", ".join(persona.traits)
            line = Text()
            line.append(f"  u/{persona.username}", style="author")
            line.append(f"  [{traits}]", style="grey50")
            console.print(line)
        console.print(Rule(style="separator"))
        console.print()

    # Posts
    posts = session.posts[:max_posts] if max_posts else session.posts
    # Sort by score descending (hot page)
    posts = sorted(posts, key=lambda p: p.score, reverse=True)

    for i, post in enumerate(posts, 1):
        _render_post(post, console, number=i)

    # Footer
    total = session.total_comments
    footer = Text(
        f"  {len(session.posts)} posts  •  {total} comments  •  {len(session.personas)} users",
        style="grey50",
    )
    console.print(footer)
    console.print()
