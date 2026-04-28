"""Rust stack implementation."""

from __future__ import annotations

import shutil
from pathlib import Path

from agent_scaffold.config import SCAFFOLD_ROOT, Config
from agent_scaffold.templates import copy_tree, render_template


class RustStack:
    def tools_toml(self) -> str:
        return 'python = "3.12"\nuv = "latest"\nrust = "stable"\n'

    def adr_notes(self) -> str:
        return """\
The Rust stack uses:
- **cargo fmt** for formatting (rustfmt under the hood)
- **cargo clippy** for linting (hundreds of lint rules)
- **cargo check** for fast type/borrow checking
- **cargo test** for testing"""

    def stack_notes(self) -> str:
        return """\
- Formatter: cargo fmt (rustfmt)
- Linter: cargo clippy (deny warnings)
- Type checker: cargo check (compiler type + borrow analysis)
- Tests: cargo test"""

    def init_single(self, root: Path, config: Config) -> dict[str, str]:
        stack_dir = SCAFFOLD_ROOT / "stacks" / "rust"
        context = _build_context(config)

        _write(stack_dir / "Cargo.toml.tmpl", root / "Cargo.toml", context)
        copy_tree(stack_dir / "src", root / "src", context)
        _write(stack_dir / "Dockerfile.tmpl", root / "Dockerfile", context)

        rustfmt = stack_dir / "rustfmt.toml"
        if rustfmt.exists():
            shutil.copy2(rustfmt, root / "rustfmt.toml")

        gitignore = SCAFFOLD_ROOT / "templates" / "single" / ".gitignore.rust.tmpl"
        if gitignore.exists():
            _write(gitignore, root / ".gitignore", context)

        return {
            "project_structure": _single_structure(config.name),
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def init_module(
        self, mod_dir: Path, config: Config, mod_name: str
    ) -> dict[str, str]:
        stack_dir = SCAFFOLD_ROOT / "stacks" / "rust"
        context = {**_build_context(config), "project_name": mod_name}

        _write(stack_dir / "Cargo.toml.tmpl", mod_dir / "Cargo.toml", context)
        copy_tree(stack_dir / "src", mod_dir / "src", context)

        return {
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def remove_examples(self, root: Path, config: Config) -> None:
        lib_rs = root / "src" / "lib.rs"
        if lib_rs.exists():
            lib_rs.unlink()

    def remove_module_examples(self, mod_dir: Path) -> None:
        for f in mod_dir.rglob("lib.rs"):
            f.unlink()


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_context(config: Config) -> dict[str, str]:
    return {
        "project_name": config.name,
        "project_description": config.description,
        "project_stack": config.stack,
        "author_name": config.author_name,
        "author_email": config.author_email,
        "module_name": config.name.replace("-", "_"),
    }


def _write(src: Path, dst: Path, context: dict[str, str]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render_template(src, context))


def _single_structure(project_name: str) -> str:
    return f"""\
```
{project_name}/
├── src/                    # Source code
│   ├── main.rs             # Entry point
│   └── lib.rs              # Library with examples
├── .mise.toml              # Task runner config
├── Cargo.toml              # Package manifest
├── rustfmt.toml            # Formatter config
├── Dockerfile              # Multi-stage build
└── README.md
```"""
