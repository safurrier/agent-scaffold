"""Python stack implementation."""

from __future__ import annotations

import shutil
from pathlib import Path

from agent_scaffold.config import Config, to_module_name
from agent_scaffold.templates import copy_tree, render_template

# Scaffold root — two levels up from this file (src/agent_scaffold/stacks/)
_SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class PythonStack:
    def tools_toml(self) -> str:
        return 'python = "3.12"\nuv = "latest"\n'

    def adr_notes(self) -> str:
        return """\
The Python stack uses:
- **uv** for package management and virtual environments
- **ruff** for formatting and linting
- **ty** for type checking
- **pytest** with coverage for testing"""

    def stack_notes(self) -> str:
        return """\
- Formatter: ruff format (line-length 88)
- Linter: ruff check (E, W, F, I, B, C4, UP, N, S, PTH, RUF)
- Type checker: ty (error-on-warning)
- Tests: pytest with coverage"""

    def init_single(self, root: Path, config: Config) -> dict[str, str]:
        module_name = to_module_name(config.name)
        stack_dir = _SCAFFOLD_ROOT / "stacks" / "python"
        context = _build_context(config, module_name)

        render_template(stack_dir / "pyproject.toml.tmpl", context)
        _write(stack_dir / "pyproject.toml.tmpl", root / "pyproject.toml", context)

        # Source directory: stacks/python/src/ → <module_name>/
        copy_tree(stack_dir / "src", root / module_name, context)

        # Tests — replace scaffold's own tests/ completely
        tests_dir = root / "tests"
        if tests_dir.exists():
            shutil.rmtree(tests_dir)
        copy_tree(stack_dir / "tests", tests_dir, context)

        # .gitignore
        gitignore = _SCAFFOLD_ROOT / "templates" / "single" / ".gitignore.python.tmpl"
        if gitignore.exists():
            _write(gitignore, root / ".gitignore", context)

        return {
            "project_structure": _single_structure(config.name, module_name),
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def init_module(
        self, mod_dir: Path, config: Config, mod_name: str
    ) -> dict[str, str]:
        module_name = to_module_name(mod_name)
        stack_dir = _SCAFFOLD_ROOT / "stacks" / "python"
        context = {**_build_context(config, module_name), "project_name": mod_name}

        _write(stack_dir / "pyproject.toml.tmpl", mod_dir / "pyproject.toml", context)
        copy_tree(stack_dir / "src", mod_dir / module_name, context)
        copy_tree(stack_dir / "tests", mod_dir / "tests", context)

        return {
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def remove_examples(self, root: Path, config: Config) -> None:
        module_name = to_module_name(config.name)
        for path in [
            root / module_name / "example.py",
            root / "tests" / "test_example.py",
        ]:
            if path.exists():
                path.unlink()

    def remove_module_examples(self, mod_dir: Path) -> None:
        for f in list(mod_dir.rglob("example.py")) + list(
            mod_dir.rglob("test_example.py")
        ):
            f.unlink()


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_context(config: Config, module_name: str) -> dict[str, str]:
    return {
        "project_name": config.name,
        "project_description": config.description,
        "project_stack": config.stack,
        "author_name": config.author_name,
        "author_email": config.author_email,
        "module_name": module_name,
        "go_module": "",
    }


def _write(src: Path, dst: Path, context: dict[str, str]) -> None:
    """Render *src* template to *dst*."""
    from agent_scaffold.templates import render_template

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render_template(src, context))


def _single_structure(project_name: str, module_name: str) -> str:
    return f"""\
```
{project_name}/
├── {module_name}/          # Source code
├── tests/                  # Test suite
├── .mise.toml              # Task runner config
├── pyproject.toml          # Python project config
└── README.md
```"""
