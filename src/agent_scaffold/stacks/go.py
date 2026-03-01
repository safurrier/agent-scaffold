"""Go stack implementation."""

from __future__ import annotations

import shutil
from pathlib import Path

from agent_scaffold.config import Config
from agent_scaffold.templates import copy_tree

_SCAFFOLD_ROOT = Path(__file__).resolve().parent.parent.parent.parent


class GoStack:
    def tools_toml(self) -> str:
        return 'go = "1.23.12"\ngofumpt = "latest"\ngolangci-lint = "latest"\n'

    def adr_notes(self) -> str:
        return """\
The Go stack uses:
- **go** (1.23) as the compiler and module manager
- **gofumpt** for formatting (stricter than gofmt)
- **golangci-lint** for linting (17 linters)
- **go vet** for static analysis
- **go test** for testing"""

    def stack_notes(self) -> str:
        return """\
- Formatter: gofumpt (stricter than gofmt)
- Linter: golangci-lint (17 linters enabled)
- Type checker: go vet (integrated compiler checks)
- Tests: go test"""

    def init_single(self, root: Path, config: Config) -> dict[str, str]:
        stack_dir = _SCAFFOLD_ROOT / "stacks" / "go"
        context = _build_context(config)

        _write(stack_dir / "go.mod.tmpl", root / "go.mod", context)
        copy_tree(stack_dir / "cmd", root / "cmd", context)
        copy_tree(stack_dir / "internal", root / "internal", context)
        shutil.copy2(stack_dir / ".golangci.yml", root / ".golangci.yml")
        _write(stack_dir / "Dockerfile.tmpl", root / "Dockerfile", context)

        gitignore = _SCAFFOLD_ROOT / "templates" / "single" / ".gitignore.go.tmpl"
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
        stack_dir = _SCAFFOLD_ROOT / "stacks" / "go"
        go_module = (
            f"{config.go_module}/{mod_name}"
            if config.go_module
            else f"github.com/your-org/{mod_name}"
        )
        context = {**_build_context(config), "go_module": go_module}

        _write(stack_dir / "go.mod.tmpl", mod_dir / "go.mod", context)
        copy_tree(stack_dir / "cmd", mod_dir / "cmd", context)
        copy_tree(stack_dir / "internal", mod_dir / "internal", context)
        shutil.copy2(stack_dir / ".golangci.yml", mod_dir / ".golangci.yml")

        return {
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def remove_examples(self, root: Path, config: Config) -> None:
        for path in [
            root / "internal" / "app" / "app.go",
            root / "internal" / "app" / "app_test.go",
        ]:
            if path.exists():
                path.unlink()

    def remove_module_examples(self, mod_dir: Path) -> None:
        for pattern in ["app.go", "app_test.go"]:
            for f in mod_dir.rglob(pattern):
                f.unlink()


# ── helpers ───────────────────────────────────────────────────────────────────


def _build_context(config: Config) -> dict[str, str]:
    return {
        "project_name": config.name,
        "project_description": config.description,
        "project_stack": config.stack,
        "author_name": config.author_name,
        "author_email": config.author_email,
        "go_module": config.go_module or f"github.com/your-org/{config.name}",
        "module_name": config.name,
    }


def _write(src: Path, dst: Path, context: dict[str, str]) -> None:
    from agent_scaffold.templates import render_template

    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render_template(src, context))


def _single_structure(project_name: str) -> str:
    return f"""\
```
{project_name}/
├── cmd/                    # Entry points
├── internal/               # Private packages
│   └── app/                # Core application logic
├── .mise.toml              # Task runner config
├── go.mod                  # Go module config
├── .golangci.yml           # Linter config
├── Dockerfile              # Multi-stage distroless build
└── README.md
```"""
