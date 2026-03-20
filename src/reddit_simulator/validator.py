"""Validation layer: anachronism detection and quality checks."""

from __future__ import annotations

from dataclasses import dataclass

from reddit_simulator.eras import get_era
from reddit_simulator.models import Session

# Common modern anachronisms to flag regardless of era
UNIVERSAL_MODERN_TERMS = [
    "internet",
    "online",
    "website",
    "email",
    "smartphone",
    "phone",
    "computer",
    "laptop",
    "television",
    "tv",
    "radio broadcast",
    "lol",
    "omg",
    "wtf",
    "btw",
    "afaik",
    "imo",
    "fwiw",
    "hashtag",
    "trending",
    "viral",
    "meme",
    "selfie",
    "photo",
    "electricity",
    "battery",
    "nuclear",
    "robot",
    "algorithm",
]


@dataclass
class ValidationResult:
    passed: bool
    anachronism_hits: list[tuple[str, str]]  # (term, location)
    diversity_score: float  # 0.0–1.0
    depth_score: float  # avg comment depth
    post_count: int
    comment_count: int
    persona_count: int
    warnings: list[str]

    def summary(self) -> str:
        status = "PASS" if self.passed else "WARN"
        lines = [
            f"[{status}] Posts: {self.post_count} | Comments: {self.comment_count} | Personas: {self.persona_count}",
            f"  Diversity score: {self.diversity_score:.2f} | Depth score: {self.depth_score:.2f}",
        ]
        if self.anachronism_hits:
            lines.append(f"  Anachronism hits ({len(self.anachronism_hits)}):")
            for term, location in self.anachronism_hits[:5]:
                lines.append(f"    - '{term}' in {location}")
        if self.warnings:
            for w in self.warnings:
                lines.append(f"  Warning: {w}")
        return "\n".join(lines)


def validate_session(session: Session, era_key: str) -> ValidationResult:
    """Run quality checks on a generated session.

    Checks:
    - Minimum post/comment counts
    - Anachronism detection (keyword matching)
    - Persona diversity (unique authors across posts)
    - Comment depth adequacy
    """
    era = get_era(era_key)
    forbidden = [t.lower() for t in era["forbidden_concepts"]] + UNIVERSAL_MODERN_TERMS
    warnings: list[str] = []
    anachronism_hits: list[tuple[str, str]] = []

    # Collect all text content for checking
    def check_text(text: str, location: str) -> None:
        lower = text.lower()
        for term in forbidden:
            if term in lower:
                anachronism_hits.append((term, location))

    # Check all posts and comments
    for post in session.posts:
        check_text(post.title, f"post '{post.id}' title")
        check_text(post.content, f"post '{post.id}' content")
        for j, comment in enumerate(post.comments):
            check_text(comment.content, f"post '{post.id}' comment {j}")
            for k, reply in enumerate(comment.replies):
                check_text(reply.content, f"post '{post.id}' comment {j} reply {k}")

    # Persona diversity: unique authors across posts
    all_authors: set[str] = set()
    for post in session.posts:
        all_authors.add(post.author)
        for comment in post.comments:
            all_authors.add(comment.author)
            for reply in comment.replies:
                all_authors.add(reply.author)
    persona_usernames = {p.username for p in session.personas}
    diversity_score = len(all_authors) / max(len(persona_usernames), 1)

    # Comment depth: average replies per comment
    total_comments = 0
    total_replies = 0
    for post in session.posts:
        total_comments += len(post.comments)
        for comment in post.comments:
            total_replies += len(comment.replies)
    depth_score = total_replies / max(total_comments, 1)

    total_comment_count = session.total_comments

    # Check minimums per acceptance criteria
    if len(session.posts) < 5:
        warnings.append(f"Only {len(session.posts)} posts (minimum 5 required)")
    if total_comment_count < 20:
        warnings.append(f"Only {total_comment_count} comments (minimum 20 required)")
    if len(session.personas) < 5:
        warnings.append(f"Only {len(session.personas)} personas (minimum 5 required)")

    passed = (
        len(session.posts) >= 5
        and total_comment_count >= 20
        and len(anachronism_hits) == 0
    )

    return ValidationResult(
        passed=passed,
        anachronism_hits=anachronism_hits,
        diversity_score=min(diversity_score, 1.0),
        depth_score=depth_score,
        post_count=len(session.posts),
        comment_count=total_comment_count,
        persona_count=len(session.personas),
        warnings=warnings,
    )
