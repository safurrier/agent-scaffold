"""Multi-agent session generator using the Claude API."""

from __future__ import annotations

import json
import os
import random

import anthropic

from reddit_simulator.eras import EraDefinition, get_era
from reddit_simulator.models import Comment, Persona, Post, Reply, Session

# JSON schema for the full session output (non-recursive, 3-level depth)
SESSION_SCHEMA: dict = {
    "type": "object",
    "properties": {
        "personas": {
            "type": "array",
            "description": "8-12 historically plausible user personas for this era",
            "items": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Era-appropriate username (e.g. Marcus_Mercator, GabrielleDeVaux)",
                    },
                    "traits": {
                        "type": "array",
                        "description": "2-4 personality/role traits",
                        "items": {"type": "string"},
                    },
                    "background": {
                        "type": "string",
                        "description": "One sentence about this person's background",
                    },
                },
                "required": ["username", "traits", "background"],
                "additionalProperties": False,
            },
        },
        "posts": {
            "type": "array",
            "description": "5-8 top-level Reddit-style posts",
            "items": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The post title — engaging, era-authentic",
                    },
                    "author": {
                        "type": "string",
                        "description": "Username from the personas list",
                    },
                    "content": {
                        "type": "string",
                        "description": "Post body text — 2-5 sentences",
                    },
                    "score": {
                        "type": "integer",
                        "description": "Simulated upvote score (0-9999)",
                    },
                    "timestamp": {
                        "type": "string",
                        "description": "Relative time string like '3 hours ago' or '47 minutes ago'",
                    },
                    "comments": {
                        "type": "array",
                        "description": "3-8 top-level comments on this post",
                        "items": {
                            "type": "object",
                            "properties": {
                                "author": {"type": "string"},
                                "content": {
                                    "type": "string",
                                    "description": "Comment text — 1-3 sentences",
                                },
                                "score": {"type": "integer"},
                                "replies": {
                                    "type": "array",
                                    "description": "1-3 replies to this comment",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "author": {"type": "string"},
                                            "content": {"type": "string"},
                                            "score": {"type": "integer"},
                                        },
                                        "required": ["author", "content", "score"],
                                        "additionalProperties": False,
                                    },
                                },
                            },
                            "required": ["author", "content", "score", "replies"],
                            "additionalProperties": False,
                        },
                    },
                },
                "required": [
                    "title",
                    "author",
                    "content",
                    "score",
                    "timestamp",
                    "comments",
                ],
                "additionalProperties": False,
            },
        },
    },
    "required": ["personas", "posts"],
    "additionalProperties": False,
}


def _build_system_prompt(era: EraDefinition) -> str:
    return f"""You are a multi-agent historical simulation engine. Your task is to generate a
realistic Reddit-like session set in a specific historical era, as if the people of that time
had access to an online forum.

HISTORICAL CONTEXT:
{era["context"].strip()}

VOICE & STYLE GUIDE:
{era["style_guide"].strip()}

FORBIDDEN CONCEPTS (do not reference these — they don't exist yet):
{", ".join(era["forbidden_concepts"])}

SIMULATION RULES:
1. All content must be historically grounded — no future knowledge leakage
2. Voice must match the era — language, concerns, worldview
3. Simulate multiple distinct personas with consistent personalities across posts/comments
4. Generate organic discussion — agreement, disagreement, humor, fear, speculation
5. Anchor content around the central event but allow organic tangents
6. Vary the emotional register: panic, curiosity, humor, skepticism, expertise
7. Recurring usernames must maintain consistent voice and perspective
8. Timestamps should be relative and internally consistent (earlier posts have higher scores)
9. Scores reflect community engagement — hot topics get higher scores

Generate a complete session JSON object with diverse personas and rich threaded discussions."""


def _build_user_prompt(era: EraDefinition, post_topics: list[str], seed: int) -> str:
    topics_str = "\n".join(f"- {t}" for t in post_topics)
    return f"""Generate a historical Reddit session for: {era["name"]}
Central event: {era["event"]}
Random seed: {seed} (use this to vary your output)

Generate posts covering these topics (you may adapt or expand them):
{topics_str}

Ensure:
- 8-12 distinct personas with era-appropriate usernames
- 5-8 posts with titles that feel authentic to the era
- Each post has 3-8 comments with 1-3 replies each
- Total comment count ≥ 20
- Personas appear consistently across multiple posts
- At least one humorous post, one serious/practical post, one emotional/fearful post
- No anachronisms — nothing that wouldn't exist in {era["date"]}"""


def generate_session(
    era_key: str,
    seed: int | None = None,
    num_posts: int = 6,
    *,
    api_key: str | None = None,
    on_progress: Callable[[str], None] | None = None,  # noqa: F821
) -> Session:
    """Generate a full historical Reddit session using Claude.

    Args:
        era_key: One of the keys in ERAS (e.g. 'pompeii', 'moon_landing').
        seed: Random seed for reproducibility. If None, uses a random seed.
        num_posts: Target number of posts (passed as hint to the model).
        api_key: Anthropic API key. Falls back to ANTHROPIC_API_KEY env var.
        on_progress: Optional callback receiving status strings.

    Returns:
        A fully populated Session dataclass.
    """
    if seed is None:
        seed = random.randint(0, 999999)

    era = get_era(era_key)
    rng = random.Random(seed)

    # Pick post topics using seeded RNG for reproducibility
    all_seeds = era["post_seeds"]
    topics = rng.sample(all_seeds, min(num_posts, len(all_seeds)))
    if len(topics) < num_posts:
        topics = topics + rng.choices(all_seeds, k=num_posts - len(topics))

    if on_progress:
        on_progress(f"Generating session for {era['name']} (seed={seed})...")

    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))

    system = _build_system_prompt(era)
    user_msg = _build_user_prompt(era, topics, seed)

    if on_progress:
        on_progress("Calling Claude API (streaming)...")

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=16000,
        thinking={"type": "adaptive"},
        system=system,
        messages=[{"role": "user", "content": user_msg}],
        output_config={
            "format": {
                "type": "json_schema",
                "name": "historical_reddit_session",
                "schema": SESSION_SCHEMA,
            }
        },
    ) as stream:
        final = stream.get_final_message()

    if on_progress:
        on_progress("Parsing response...")

    # Extract JSON from the text block
    text = next(b.text for b in final.content if b.type == "text")
    data = json.loads(text)

    # Build persona objects
    personas = [
        Persona(
            username=p["username"],
            traits=p["traits"],
            background=p.get("background", ""),
        )
        for p in data["personas"]
    ]

    # Build post objects
    posts = []
    for i, p in enumerate(data["posts"]):
        comments = []
        for c in p.get("comments", []):
            replies = [
                Reply(
                    author=r["author"],
                    content=r["content"],
                    score=r.get("score", 0),
                )
                for r in c.get("replies", [])
            ]
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
                id=f"p{i + 1}",
                title=p["title"],
                author=p["author"],
                timestamp=p.get("timestamp", "1 hour ago"),
                content=p["content"],
                score=p.get("score", 0),
                comments=comments,
            )
        )

    return Session(
        era=era["name"],
        event=era["event"],
        posts=posts,
        personas=personas,
        seed=seed,
    )
