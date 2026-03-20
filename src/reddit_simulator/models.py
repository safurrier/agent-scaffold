"""Core data models for the Historical Reddit Simulator."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Reply:
    author: str
    content: str
    score: int = 0


@dataclass
class Comment:
    author: str
    content: str
    score: int = 0
    replies: list[Reply] = field(default_factory=list)


@dataclass
class Post:
    id: str
    title: str
    author: str
    timestamp: str
    content: str
    score: int = 0
    comments: list[Comment] = field(default_factory=list)


@dataclass
class Persona:
    username: str
    traits: list[str]
    background: str = ""


@dataclass
class Session:
    era: str
    event: str
    posts: list[Post]
    personas: list[Persona]
    seed: int | None = None

    @property
    def total_comments(self) -> int:
        count = 0
        for post in self.posts:
            count += len(post.comments)
            for comment in post.comments:
                count += len(comment.replies)
        return count
