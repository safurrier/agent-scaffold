"""Unit tests for the Historical Reddit Simulator."""

from __future__ import annotations

import pytest

from reddit_simulator.eras import ERAS, get_era, list_eras
from reddit_simulator.models import Comment, Persona, Post, Reply, Session
from reddit_simulator.validator import validate_session


# ─── fixtures ────────────────────────────────────────────────────────────────


def _make_session(
    era: str = "Pompeii, 79 AD",
    event: str = "Mount Vesuvius eruption",
    num_posts: int = 5,
    comments_per_post: int = 5,
    replies_per_comment: int = 1,
) -> Session:
    """Build a minimal synthetic session for testing."""
    personas = [
        Persona(username=f"user_{i}", traits=["merchant"], background="A local trader.")
        for i in range(8)
    ]
    posts = []
    for p in range(num_posts):
        comments = []
        for c in range(comments_per_post):
            replies = [
                Reply(author=f"user_{(c + r) % 8}", content="A reply.", score=5)
                for r in range(replies_per_comment)
            ]
            comments.append(
                Comment(
                    author=f"user_{c % 8}",
                    content="A comment about the current events.",
                    score=10,
                    replies=replies,
                )
            )
        posts.append(
            Post(
                id=f"p{p}",
                title=f"Post {p} about Vesuvius",
                author=f"user_{p % 8}",
                timestamp="2 hours ago",
                content="Something is happening on the mountain today.",
                score=100 * (p + 1),
                comments=comments,
            )
        )
    return Session(era=era, event=event, posts=posts, personas=personas, seed=42)


# ─── model tests ─────────────────────────────────────────────────────────────


class TestModels:
    def test_session_total_comments(self) -> None:
        session = _make_session(num_posts=3, comments_per_post=4, replies_per_comment=2)
        # 3 posts × (4 comments + 4×2 replies) = 3 × 12 = 36
        assert session.total_comments == 36

    def test_session_total_comments_no_replies(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=0)
        assert session.total_comments == 20

    def test_reply_dataclass(self) -> None:
        r = Reply(author="test_user", content="Hello", score=42)
        assert r.author == "test_user"
        assert r.score == 42

    def test_comment_default_replies(self) -> None:
        c = Comment(author="u1", content="Hi")
        assert c.replies == []
        assert c.score == 0

    def test_post_default_comments(self) -> None:
        p = Post(id="p1", title="T", author="a", timestamp="1h ago", content="C")
        assert p.comments == []
        assert p.score == 0

    def test_persona_fields(self) -> None:
        p = Persona(username="Marcus_Mercator", traits=["merchant", "skeptical"])
        assert p.background == ""
        assert "merchant" in p.traits


# ─── era registry tests ───────────────────────────────────────────────────────


class TestEras:
    def test_all_eras_have_required_keys(self) -> None:
        required = {"name", "date", "subreddit", "event", "context", "style_guide", "post_seeds", "forbidden_concepts"}
        for key, era in ERAS.items():
            missing = required - set(era.keys())
            assert not missing, f"Era '{key}' missing keys: {missing}"

    def test_all_eras_have_post_seeds(self) -> None:
        for key, era in ERAS.items():
            assert len(era["post_seeds"]) >= 3, f"Era '{key}' needs at least 3 post seeds"

    def test_get_era_valid(self) -> None:
        era = get_era("pompeii")
        assert era["name"] == "Pompeii, 79 AD"

    def test_get_era_invalid(self) -> None:
        with pytest.raises(ValueError, match="Unknown era"):
            get_era("futuristic_mars")

    def test_list_eras_returns_all(self) -> None:
        eras = list_eras()
        assert len(eras) == len(ERAS)
        keys = [k for k, _, _ in eras]
        assert "pompeii" in keys
        assert "moon_landing" in keys

    def test_list_eras_tuple_structure(self) -> None:
        for key, name, event in list_eras():
            assert isinstance(key, str)
            assert isinstance(name, str)
            assert isinstance(event, str)
            assert len(key) > 0
            assert len(name) > 0


# ─── validator tests ──────────────────────────────────────────────────────────


class TestValidator:
    def test_valid_session_passes(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=2)
        result = validate_session(session, "pompeii")
        assert result.post_count == 5
        assert result.comment_count == 60  # 5 × (4 + 8)
        # No anachronism hits for generic content
        assert result.persona_count == 8

    def test_too_few_posts_warns(self) -> None:
        session = _make_session(num_posts=3, comments_per_post=10, replies_per_comment=2)
        result = validate_session(session, "pompeii")
        assert not result.passed
        assert any("posts" in w for w in result.warnings)

    def test_too_few_comments_warns(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=2, replies_per_comment=0)
        result = validate_session(session, "pompeii")
        # 5 × 2 = 10 comments, less than minimum 20
        assert not result.passed
        assert any("comment" in w for w in result.warnings)

    def test_anachronism_detected_in_post(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=2)
        # Inject an anachronism into a post
        session.posts[0].content = "I posted about this on the internet yesterday."
        result = validate_session(session, "pompeii")
        assert len(result.anachronism_hits) > 0
        terms = [hit[0] for hit in result.anachronism_hits]
        assert "internet" in terms

    def test_anachronism_detected_in_comment(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=2)
        session.posts[0].comments[0].content = "lol this is so crazy"
        result = validate_session(session, "pompeii")
        assert len(result.anachronism_hits) > 0

    def test_diversity_score_range(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=2)
        result = validate_session(session, "pompeii")
        assert 0.0 <= result.diversity_score <= 1.0

    def test_depth_score_positive(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=4, replies_per_comment=2)
        result = validate_session(session, "pompeii")
        assert result.depth_score > 0

    def test_validation_summary_contains_key_info(self) -> None:
        session = _make_session(num_posts=5, comments_per_post=5, replies_per_comment=2)
        result = validate_session(session, "pompeii")
        summary = result.summary()
        assert "Posts:" in summary
        assert "Comments:" in summary
