"""Verify docs frontmatter and structure for the scaffold itself.

These tests run on the scaffold's own docs/ directory (before any init).
Fast — no subprocess, just file-system assertions.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests._docs_helpers import (
    find_doc_files,
    has_frontmatter,
    parse_frontmatter,
    validate_frontmatter,
)
from tests._support import SCAFFOLD_ROOT

pytestmark = pytest.mark.contract

DOCS_DIR = SCAFFOLD_ROOT / "docs"

# All docs/*.md files that MUST have frontmatter (excludes docs/AGENTS.md)
DOCS_WITH_FRONTMATTER = find_doc_files(DOCS_DIR)

# Files that must NOT have frontmatter
NO_FRONTMATTER_FILES = [
    SCAFFOLD_ROOT / "AGENTS.md",
    DOCS_DIR / "AGENTS.md",
]


# ── Frontmatter presence ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "doc",
    DOCS_WITH_FRONTMATTER,
    ids=lambda p: str(p.relative_to(SCAFFOLD_ROOT)),
)
def test_doc_has_frontmatter(doc: Path) -> None:
    """Every docs/*.md file (except AGENTS.md) must have YAML frontmatter."""
    assert has_frontmatter(doc), (
        f"{doc.relative_to(SCAFFOLD_ROOT)} is missing YAML frontmatter (---)"
    )


@pytest.mark.parametrize(
    "path",
    [p for p in NO_FRONTMATTER_FILES if p.exists()],
    ids=lambda p: str(p.relative_to(SCAFFOLD_ROOT)),
)
def test_agents_md_has_no_frontmatter(path: Path) -> None:
    """AGENTS.md files must NOT have frontmatter — only docs/ files get it."""
    assert not has_frontmatter(path), (
        f"{path.relative_to(SCAFFOLD_ROOT)} should NOT have frontmatter"
    )


# ── Frontmatter schema validation ─────────────────────────────────────────


@pytest.mark.parametrize(
    "doc",
    DOCS_WITH_FRONTMATTER,
    ids=lambda p: str(p.relative_to(SCAFFOLD_ROOT)),
)
def test_doc_frontmatter_is_valid(doc: Path) -> None:
    """Frontmatter must have id, title, description, and non-empty index."""
    fm = parse_frontmatter(doc)
    if fm is None:
        pytest.skip("no frontmatter (covered by test_doc_has_frontmatter)")
    errors = validate_frontmatter(fm)
    assert not errors, (
        f"{doc.relative_to(SCAFFOLD_ROOT)} frontmatter errors: {'; '.join(errors)}"
    )


# ── Uniqueness ────────────────────────────────────────────────────────────


def test_doc_ids_are_unique() -> None:
    """All frontmatter ids across docs/ must be unique."""
    ids: dict[str, Path] = {}
    for doc in DOCS_WITH_FRONTMATTER:
        fm = parse_frontmatter(doc)
        if fm is None or not fm.id:
            continue
        if fm.id in ids:
            pytest.fail(
                f"Duplicate id '{fm.id}' in "
                f"{doc.relative_to(SCAFFOLD_ROOT)} and "
                f"{ids[fm.id].relative_to(SCAFFOLD_ROOT)}"
            )
        ids[fm.id] = doc


# ── Index entries have keywords ───────────────────────────────────────────


@pytest.mark.parametrize(
    "doc",
    DOCS_WITH_FRONTMATTER,
    ids=lambda p: str(p.relative_to(SCAFFOLD_ROOT)),
)
def test_doc_index_entries_have_keywords(doc: Path) -> None:
    """Every index entry must have at least one keyword."""
    fm = parse_frontmatter(doc)
    if fm is None:
        pytest.skip("no frontmatter")
    for entry in fm.index:
        keywords = entry.get("keywords", [])
        assert keywords, (
            f"{doc.relative_to(SCAFFOLD_ROOT)}: "
            f"index entry '{entry.get('id', '?')}' has no keywords"
        )


# ── mkdocs.yml consistency ────────────────────────────────────────────────


def test_mkdocs_nav_entries_exist() -> None:
    """Every .md path listed in mkdocs.yml nav must exist on disk."""
    mkdocs_yml = SCAFFOLD_ROOT / "mkdocs.yml"
    if not mkdocs_yml.exists():
        pytest.skip("mkdocs.yml not found")
    content = mkdocs_yml.read_text()
    for m in re.finditer(r":\s+(\S+\.md)\s*$", content, re.MULTILINE):
        md_path = DOCS_DIR / m.group(1)
        assert md_path.exists(), (
            f"mkdocs.yml references {m.group(1)} but {md_path} does not exist"
        )
