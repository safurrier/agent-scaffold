"""Shared helpers for docs frontmatter and structure validation.

Zero external dependencies — uses only stdlib so it's portable into
generated repos without adding pyyaml or python-frontmatter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Frontmatter:
    """Parsed YAML frontmatter from a markdown file."""

    id: str = ""
    title: str = ""
    description: str = ""
    index: list[dict[str, object]] = field(default_factory=list)
    raw: str = ""


def has_frontmatter(path: Path) -> bool:
    """Return True if the file starts with a YAML frontmatter fence."""
    return path.read_text().startswith("---\n")


def parse_frontmatter(path: Path) -> Frontmatter | None:
    """Parse YAML frontmatter from a markdown file. Returns None if absent."""
    text = path.read_text()
    if not text.startswith("---\n"):
        return None

    end = text.find("\n---\n", 4)
    if end == -1:
        return None

    raw = text[4:end]
    fm = Frontmatter(raw=raw)

    # Parse id
    m = re.search(r"^id:\s*(.+)$", raw, re.MULTILINE)
    if m:
        fm.id = m.group(1).strip()

    # Parse title
    m = re.search(r"^title:\s*(.+)$", raw, re.MULTILINE)
    if m:
        fm.title = m.group(1).strip()

    # Parse description (may be multi-line with > folding)
    m = re.search(r"^description:\s*>?\s*\n((?:\s{2,}.+\n?)+)", raw, re.MULTILINE)
    if m:
        fm.description = " ".join(
            line.strip() for line in m.group(1).strip().splitlines()
        )
    else:
        m = re.search(r"^description:\s*(.+)$", raw, re.MULTILINE)
        if m:
            fm.description = m.group(1).strip()

    # Parse index entries
    fm.index = _parse_index(raw)

    return fm


def _parse_index(raw: str) -> list[dict[str, object]]:
    """Parse the index list from frontmatter raw text."""
    entries: list[dict[str, object]] = []
    in_index = False
    current: dict[str, object] | None = None

    for line in raw.splitlines():
        if re.match(r"^index:\s*$", line):
            in_index = True
            continue
        if not in_index:
            continue
        # End of index: non-indented, non-empty line that isn't a list item
        if line and not line.startswith(" ") and not line.startswith("\t"):
            break

        id_match = re.match(r"\s+-\s+id:\s*(.+)$", line)
        if id_match:
            if current is not None:
                entries.append(current)
            current = {"id": id_match.group(1).strip(), "keywords": []}
            continue

        kw_match = re.match(r"\s+keywords:\s*\[(.+)\]", line)
        if kw_match and current is not None:
            keywords = [k.strip().strip("'\"") for k in kw_match.group(1).split(",")]
            current["keywords"] = keywords

    if current is not None:
        entries.append(current)

    return entries


def validate_frontmatter(fm: Frontmatter) -> list[str]:
    """Validate frontmatter fields. Returns list of error messages (empty = valid)."""
    errors: list[str] = []

    if not fm.id:
        errors.append("missing 'id' field")
    elif not re.match(r"^[a-z][a-z0-9-]*$", fm.id):
        errors.append(f"id '{fm.id}' is not kebab-case")

    if not fm.title:
        errors.append("missing 'title' field")

    if not fm.description:
        errors.append("missing 'description' field")

    if not fm.index:
        errors.append("missing or empty 'index' field")

    for entry in fm.index:
        entry_id = entry.get("id", "")
        keywords = entry.get("keywords", [])
        if not entry_id:
            errors.append("index entry missing 'id'")
        if not keywords:
            errors.append(f"index entry '{entry_id}' has no keywords")

    return errors


def find_doc_files(docs_dir: Path) -> list[Path]:
    """Find all .md files in docs_dir (recursive), excluding AGENTS.md."""
    if not docs_dir.exists():
        return []
    return sorted(p for p in docs_dir.rglob("*.md") if p.name != "AGENTS.md")
