"""Web stack implementation."""

from __future__ import annotations

from pathlib import Path

from harness_toolkit.scaffold.config import SCAFFOLD_ROOT, Config
from harness_toolkit.scaffold.templates import copy_tree, render_template


class WebStack:
    def tools_toml(self) -> str:
        return 'python = "3.12"\nuv = "latest"\nnode = "22"\n'

    def adr_notes(self) -> str:
        return """\
The Web stack uses:
- **Vite + React** for the browser app
- **TypeScript** for static checking
- **Cloudflare Workers + Static Assets** for hosting and API routes
- **D1 migrations** for relational app state when persistence is enabled
- **Vitest**, **ESLint**, and **Prettier** for validation"""

    def stack_notes(self) -> str:
        return """\
- Formatter: prettier
- Linter: eslint
- Type checker: tsc --noEmit
- Tests: vitest
- Build: vite build
- Deploy dry-run: wrangler deploy --dry-run"""

    def init_single(self, root: Path, config: Config) -> dict[str, str]:
        stack_dir = SCAFFOLD_ROOT / "stacks" / "web"
        context = _build_context(config, config.name)

        copy_tree(stack_dir / "project", root, context)

        gitignore = SCAFFOLD_ROOT / "templates" / "single" / ".gitignore.web.tmpl"
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
        stack_dir = SCAFFOLD_ROOT / "stacks" / "web"
        context = _build_context(config, mod_name)

        copy_tree(stack_dir / "project", mod_dir, context)

        return {
            "stack_notes": self.stack_notes(),
            "stack_adr_notes": self.adr_notes(),
        }

    def remove_examples(self, root: Path, config: Config) -> None:
        for path in [
            root / "src" / "app" / "ExamplePanel.tsx",
            root / "tests" / "app.test.ts",
        ]:
            if path.exists():
                path.unlink()
        _write_minimal_app(
            root / "src" / "app" / "App.tsx", config.name, config.description
        )

    def remove_module_examples(self, mod_dir: Path) -> None:
        for rel_path in [
            Path("src") / "app" / "ExamplePanel.tsx",
            Path("tests") / "app.test.ts",
        ]:
            path = mod_dir / rel_path
            if path.exists():
                path.unlink()
        _write_minimal_app(mod_dir / "src" / "app" / "App.tsx", mod_dir.name, "")


def _build_context(config: Config, package_name: str) -> dict[str, str]:
    return {
        "project_name": package_name,
        "project_description": config.description,
        "project_stack": config.stack,
        "author_name": config.author_name,
        "author_email": config.author_email,
        "module_name": package_name.replace("-", "_"),
        "web_package_name": package_name,
    }


def _write(src: Path, dst: Path, context: dict[str, str]) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(render_template(src, context))


def _write_minimal_app(path: Path, project_name: str, description: str) -> None:
    path.write_text(
        f"""\
export function App() {{
  return (
    <main className="app-shell">
      <section className="hero">
        <p className="eyebrow">Harness web stack</p>
        <h1>{project_name}</h1>
        <p className="summary">{description or "Ready for implementation."}</p>
      </section>
    </main>
  );
}}
"""
    )


def _single_structure(project_name: str) -> str:
    return f"""\
```
{project_name}/
├── src/                    # React browser app
├── worker/                 # Cloudflare Worker API routes
├── migrations/             # D1 migrations
├── tests/                  # Vitest coverage
├── public/                 # Static assets and seed data
├── .mise.toml              # Task runner config
├── package.json            # Web tooling scripts
├── wrangler.jsonc          # Cloudflare Worker config
└── README.md
```"""
