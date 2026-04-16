from __future__ import annotations

from pathlib import Path

from scripts.plan_contract import (
    adr_dir,
    checklist_has_meaningful_items,
    file_has_meaningful_content,
    ledger_path,
    resolve_plan_artifact_path,
    validation_has_commands,
)


def test_ledger_path_prefers_generated_layout(tmp_path: Path) -> None:
    generated = tmp_path / "docs" / "explanation" / "decision-ledger.md"
    legacy = tmp_path / "docs" / "decision-ledger.md"
    generated.parent.mkdir(parents=True)
    legacy.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text("# generated\n")
    legacy.write_text("# legacy\n")

    assert ledger_path(tmp_path) == generated


def test_ledger_path_falls_back_to_legacy_layout(tmp_path: Path) -> None:
    legacy = tmp_path / "docs" / "decision-ledger.md"
    legacy.parent.mkdir(parents=True)
    legacy.write_text("# legacy\n")

    assert ledger_path(tmp_path) == legacy


def test_adr_dir_prefers_generated_layout(tmp_path: Path) -> None:
    generated = tmp_path / "docs" / "explanation" / "decisions"
    legacy = tmp_path / "docs" / "decisions"
    generated.mkdir(parents=True)
    legacy.mkdir(parents=True, exist_ok=True)

    assert adr_dir(tmp_path) == generated


def test_adr_dir_falls_back_to_legacy_layout(tmp_path: Path) -> None:
    legacy = tmp_path / "docs" / "decisions"
    legacy.mkdir(parents=True)

    assert adr_dir(tmp_path) == legacy


def test_file_has_meaningful_content_ignores_placeholder_checklist(
    tmp_path: Path,
) -> None:
    path = tmp_path / "TODO.md"
    path.write_text(
        "# TODO\n\n- [ ] Replace this placeholder with the actual slice tasks\n"
    )

    assert file_has_meaningful_content(path) is False


def test_file_has_meaningful_content_accepts_real_checklist_item(
    tmp_path: Path,
) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("# TODO\n\n- [ ] Add plan-check validation coverage\n")

    assert file_has_meaningful_content(path) is True


def test_checklist_has_meaningful_items_rejects_prose_only_todo(tmp_path: Path) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("# TODO\n\nExplain the work in prose without checkboxes.\n")

    assert checklist_has_meaningful_items(path) is False


def test_checklist_has_meaningful_items_accepts_real_task(tmp_path: Path) -> None:
    path = tmp_path / "TODO.md"
    path.write_text("# TODO\n\n- [ ] Add a real review artifact\n")

    assert checklist_has_meaningful_items(path) is True


def test_validation_has_commands_rejects_non_command_code_fence(tmp_path: Path) -> None:
    path = tmp_path / "VALIDATION.md"
    path.write_text("# Validation\n\n```text\nstill need to test this\n```\n")

    assert validation_has_commands(path) is False


def test_validation_has_commands_rejects_prose_mentions(tmp_path: Path) -> None:
    path = tmp_path / "VALIDATION.md"
    path.write_text("# Validation\n\nRemember to run mise run check before handoff.\n")

    assert validation_has_commands(path) is False


def test_validation_has_commands_accepts_shell_commands_in_fence(
    tmp_path: Path,
) -> None:
    path = tmp_path / "VALIDATION.md"
    path.write_text(
        "# Validation\n\n```bash\n$ mise run check\n$ uv run pytest -q\n```\n"
    )

    assert validation_has_commands(path) is True


def test_resolve_plan_artifact_path_accepts_plan_local_paths(tmp_path: Path) -> None:
    plan_dir = tmp_path / ".ai" / "plans" / "2026-04-12-123456-demo"
    target = plan_dir / "artifacts" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok\n")

    assert (
        resolve_plan_artifact_path(plan_dir, "artifacts/report.md") == target.resolve()
    )


def test_resolve_plan_artifact_path_rejects_parent_escape(tmp_path: Path) -> None:
    plan_dir = tmp_path / ".ai" / "plans" / "2026-04-12-123456-demo"
    plan_dir.mkdir(parents=True)
    (tmp_path / "README.md").write_text("root\n")

    assert resolve_plan_artifact_path(plan_dir, "../../../README.md") is None
