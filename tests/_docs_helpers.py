"""Shared helpers for docs frontmatter and structure validation.

Zero external dependencies — uses only stdlib so it's portable into
generated repos without adding pyyaml or python-frontmatter.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

# ── Frontmatter ──────────────────────────────────────────────────────────


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


# ── Section parsing ──────────────────────────────────────────────────────


@dataclass
class DocSection:
    """A markdown heading and its content."""

    heading: str
    level: int
    content: str
    line_number: int


def parse_sections(path: Path) -> list[DocSection]:
    """Parse all markdown headings and their content from a file."""
    text = path.read_text()

    # Strip frontmatter if present
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            text = text[end + 5 :]

    sections: list[DocSection] = []
    lines = text.splitlines()

    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            sections.append(
                DocSection(
                    heading=m.group(2).strip(),
                    level=len(m.group(1)),
                    content="",  # filled below
                    line_number=i + 1,
                )
            )

    # Fill content: everything between this heading and the next
    for idx, section in enumerate(sections):
        start = section.line_number  # line after heading
        end = (
            sections[idx + 1].line_number - 1 if idx + 1 < len(sections) else len(lines)
        )
        section.content = "\n".join(lines[start:end]).strip()

    return sections


def find_section(
    sections: list[DocSection], heading_pattern: str, *, level: int | None = None
) -> DocSection | None:
    """Find first section matching heading pattern (case-insensitive substring)."""
    pat = heading_pattern.lower()
    for s in sections:
        if level is not None and s.level != level:
            continue
        if pat in s.heading.lower():
            return s
    return None


# Required H2 sections for SPEC.md (correctness envelope)
SPEC_REQUIRED_SECTIONS = [
    "Summary",
    "Goals",  # matches "Goals / Non-Goals"
    "Requirements",
    "Interfaces",  # matches "Interfaces & Contracts"
    "Invariants",
    "Acceptance",
]

# Required H2 sections for architecture.md (from AI Native Engineering RFC)
ARCHITECTURE_REQUIRED_SECTIONS = [
    "System Overview",
    "Goals",  # matches "Goals / Non-Goals"
    "Invariants",  # matches "Invariants & Boundaries"
    "Principles",  # matches "Principles & Preferred Patterns"
    "Cross-Cutting Workflows",
    "Decisions",
    "Module Map",
    "Where Human Thought Goes",
]


# ── ADR parsing ──────────────────────────────────────────────────────────


ALLOWED_ADR_STATUSES = {"Proposed", "Accepted", "Deprecated", "Superseded"}


@dataclass
class ADRMetadata:
    """Parsed metadata from an Architecture Decision Record."""

    number: int
    filename: str
    status: str = ""
    date: str = ""
    title: str = ""
    has_context: bool = False
    has_decision: bool = False
    has_consequences: bool = False
    has_alternatives: bool = False
    generated_from: str | None = None


def parse_adr(path: Path) -> ADRMetadata | None:
    """Parse ADR metadata from a decision record file."""
    name = path.name
    # Extract number from filename: NNNN-slug.md
    num_match = re.match(r"^(\d{4})-", name)
    if not num_match:
        return None

    text = path.read_text()
    adr = ADRMetadata(number=int(num_match.group(1)), filename=name)

    # Parse title from first H1
    m = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    if m:
        adr.title = m.group(1).strip()

    # Parse bold key-value fields: **Key**: Value
    m = re.search(r"\*\*Status\*\*:\s*(.+)$", text, re.MULTILINE)
    if m:
        adr.status = m.group(1).strip()

    m = re.search(r"\*\*Date\*\*:\s*(.+)$", text, re.MULTILINE)
    if m:
        adr.date = m.group(1).strip()

    m = re.search(r"\*\*Generated from\*\*:\s*(.+)$", text, re.MULTILINE)
    if m:
        adr.generated_from = m.group(1).strip()

    # Check for required H2 sections
    sections = parse_sections(path)
    adr.has_context = find_section(sections, "Context", level=2) is not None
    adr.has_decision = find_section(sections, "Decision", level=2) is not None
    adr.has_consequences = find_section(sections, "Consequences", level=2) is not None
    adr.has_alternatives = find_section(sections, "Alternatives", level=2) is not None

    return adr


def find_adrs(decisions_dir: Path) -> list[ADRMetadata]:
    """Find and parse all ADR files in a decisions directory."""
    if not decisions_dir.exists():
        return []
    adrs: list[ADRMetadata] = []
    for p in sorted(decisions_dir.glob("*.md")):
        adr = parse_adr(p)
        if adr is not None:
            adrs.append(adr)
    return adrs


def validate_adr(adr: ADRMetadata) -> list[str]:
    """Validate ADR metadata. Returns list of error messages (empty = valid)."""
    errors: list[str] = []

    if not adr.status:
        errors.append("missing Status field")
    elif adr.status not in ALLOWED_ADR_STATUSES:
        errors.append(
            f"status '{adr.status}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_ADR_STATUSES))}"
        )

    if not adr.has_context:
        errors.append("missing '## Context' section")
    if not adr.has_decision:
        errors.append("missing '## Decision' section")
    if not adr.has_consequences:
        errors.append("missing '## Consequences' section")

    if adr.generated_from is not None:
        allowed_sources = {"diff", "pr", "agent-session", "init", "manual"}
        if adr.generated_from not in allowed_sources:
            errors.append(
                f"generated-from '{adr.generated_from}' not in allowed values: "
                f"{', '.join(sorted(allowed_sources))}"
            )

    return errors


def derive_decisions_index(decisions_dir: Path) -> str:
    """Generate the markdown table for architecture.md Decisions section."""
    adrs = find_adrs(decisions_dir)
    if not adrs:
        return "| ADR | Decision |\n|---|---|\n"
    lines = ["| ADR | Decision |", "|---|---|"]
    for adr in adrs:
        link = f"[{adr.filename[:-3]}](decisions/{adr.filename})"
        title = adr.title or adr.filename
        lines.append(f"| {link} | {title} |")
    return "\n".join(lines)


# ── Plan META.yaml validation ────────────────────────────────────────────


REQUIRED_META_FIELDS = ["slug", "created", "status"]
ALLOWED_META_STATUSES = {"planned", "in-progress", "complete", "abandoned"}


@dataclass
class PlanMeta:
    """Parsed META.yaml from a plan directory."""

    slug: str = ""
    branch: str = ""
    created: str = ""
    pr: str = ""
    status: str = ""
    source: str = ""


def parse_meta_yaml(path: Path) -> PlanMeta | None:
    """Parse META.yaml from a plan directory. Returns None if absent."""
    if not path.exists():
        return None

    text = path.read_text()
    meta = PlanMeta()

    for line in text.splitlines():
        m = re.match(r"^(\w+):\s*(.*)$", line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            if hasattr(meta, key):
                setattr(meta, key, value)

    return meta


def validate_meta_yaml(meta: PlanMeta) -> list[str]:
    """Validate META.yaml fields. Returns list of error messages (empty = valid)."""
    errors: list[str] = []

    if not meta.slug:
        errors.append("missing 'slug' field")

    if not meta.created:
        errors.append("missing 'created' field")
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", meta.created):
        errors.append(f"created '{meta.created}' is not YYYY-MM-DD format")

    if not meta.status:
        errors.append("missing 'status' field")
    elif meta.status not in ALLOWED_META_STATUSES:
        errors.append(
            f"status '{meta.status}' not in allowed values: "
            f"{', '.join(sorted(ALLOWED_META_STATUSES))}"
        )

    return errors


PLAN_REQUIRED_FILES = ["META.yaml", "TODO.md", "LEARNING_LOG.md", "VALIDATION.md"]
