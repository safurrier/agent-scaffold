"""Unit tests for WebStack."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit


def test_tools_toml_has_node_python_and_uv() -> None:
    from harness_toolkit.scaffold.stacks.web import WebStack

    tools = WebStack().tools_toml()
    assert 'python = "3.12"' in tools
    assert 'uv = "latest"' in tools
    assert 'node = "22"' in tools


def test_adr_notes_mentions_key_tools() -> None:
    from harness_toolkit.scaffold.stacks.web import WebStack

    notes = WebStack().adr_notes()
    assert "Vite" in notes
    assert "TypeScript" in notes
    assert "Cloudflare Workers" in notes
    assert "D1" in notes
    assert "Vitest" in notes


def test_stack_notes_mentions_key_tools() -> None:
    from harness_toolkit.scaffold.stacks.web import WebStack

    notes = WebStack().stack_notes()
    assert "prettier" in notes
    assert "eslint" in notes
    assert "tsc --noEmit" in notes
    assert "vitest" in notes
    assert "wrangler deploy --dry-run" in notes


def test_remove_examples_rewrites_app_without_example_import(tmp_path: Path) -> None:
    from harness_toolkit.scaffold.config import Config
    from harness_toolkit.scaffold.stacks.web import WebStack

    app_dir = tmp_path / "src" / "app"
    tests_dir = tmp_path / "tests"
    app_dir.mkdir(parents=True)
    tests_dir.mkdir()
    (app_dir / "App.tsx").write_text(
        'import { ExamplePanel } from "./ExamplePanel";\n'
        "export function App() { return <ExamplePanel />; }\n"
    )
    (app_dir / "ExamplePanel.tsx").write_text(
        "export function ExamplePanel() { return null; }\n"
    )
    (tests_dir / "app.test.ts").write_text("export {};\n")

    config = Config(
        name="webprobe",
        description="A generated web app",
        shape="single",
        stack="web",
    )
    WebStack().remove_examples(tmp_path, config)

    app = (app_dir / "App.tsx").read_text()
    assert "ExamplePanel" not in app
    assert "webprobe" in app
    assert not (app_dir / "ExamplePanel.tsx").exists()
    assert not (tests_dir / "app.test.ts").exists()
