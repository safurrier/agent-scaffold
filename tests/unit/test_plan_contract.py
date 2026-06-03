from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

SKILL_CLI_SRC = (
    Path(__file__).resolve().parents[2]
    / "templates"
    / ".agent"
    / "skills"
    / "slice-workflow"
    / "cli"
    / "src"
)
sys.path.insert(0, str(SKILL_CLI_SRC))

pytestmark = pytest.mark.integration

from slice_workflow_cli.contract import (  # noqa: E402
    PlanContractError,
    adr_dir,
    changed_plan_dir_names,
    checklist_has_meaningful_items,
    file_has_meaningful_content,
    git_changed_paths,
    git_path_is_ignored,
    git_path_is_tracked,
    is_placeholder_value,
    ledger_path,
    parse_artifact_manifest,
    resolve_plan_artifact_path,
    resolve_repo_path,
    strip_changed_plan_paths,
    strip_plan_local_changes,
    validation_has_commands,
)
from slice_workflow_cli.contract import git as contract_git  # noqa: E402


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


def test_validation_has_commands_accepts_mise_flags(tmp_path: Path) -> None:
    path = tmp_path / "VALIDATION.md"
    path.write_text("# Validation\n\n- `mise -q run slice-status -- --json` passed\n")

    assert validation_has_commands(path) is True


def test_placeholder_values_include_pending() -> None:
    assert is_placeholder_value("pending") is True


def test_resolve_plan_artifact_path_accepts_plan_local_paths(tmp_path: Path) -> None:
    plan_dir = tmp_path / ".ai" / "plans" / "2026-04-12-123456-demo"
    target = plan_dir / "artifacts" / "report.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok\n")

    assert (
        resolve_plan_artifact_path(plan_dir, "artifacts/report.md") == target.resolve()
    )


def test_parse_artifact_manifest_ignores_unknown_keys(tmp_path: Path) -> None:
    manifest = tmp_path / "manifest.yaml"
    manifest.write_text(
        "\n".join(
            [
                "artifacts:",
                "  - type: report",
                "    path: artifacts/report.md",
                "    note: validation summary",
                "    sha256: future-field",
                "",
            ]
        )
    )

    entries = parse_artifact_manifest(manifest)

    assert len(entries) == 1
    assert entries[0].type == "report"
    assert entries[0].path == "artifacts/report.md"
    assert entries[0].note == "validation summary"


def test_resolve_plan_artifact_path_rejects_parent_escape(tmp_path: Path) -> None:
    plan_dir = tmp_path / ".ai" / "plans" / "2026-04-12-123456-demo"
    plan_dir.mkdir(parents=True)
    (tmp_path / "README.md").write_text("root\n")

    assert resolve_plan_artifact_path(plan_dir, "../../../README.md") is None


def test_resolve_repo_path_accepts_repo_local_paths(tmp_path: Path) -> None:
    target = tmp_path / "docs" / "reference" / "task-contract.md"
    target.parent.mkdir(parents=True)
    target.write_text("ok\n")

    assert (
        resolve_repo_path(tmp_path, "docs/reference/task-contract.md")
        == target.resolve()
    )


def test_resolve_repo_path_rejects_parent_escape(tmp_path: Path) -> None:
    outside = tmp_path.parent / "outside.md"
    outside.write_text("outside\n")

    assert resolve_repo_path(tmp_path, "../outside.md") is None


def test_git_changed_paths_raises_when_git_is_unavailable(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(contract_git.shutil, "which", lambda name: None)

    with pytest.raises(PlanContractError, match="git executable not found"):
        git_changed_paths(tmp_path)


def test_strip_plan_local_changes_ignores_nested_bootstrap_lockfiles() -> None:
    paths = [
        "Cargo.lock",
        "apps/svc-a/Cargo.lock",
        "apps/svc-b/go.sum",
        "apps/api/uv.lock",
        "src/lib.rs",
    ]

    assert strip_plan_local_changes(paths, None) == ["src/lib.rs"]


def test_strip_plan_local_changes_uses_explicit_repo_root(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    plan_dir = root / ".ai" / "plans" / "2026-04-30-120000-demo"
    plan_dir.mkdir(parents=True)

    paths = [
        ".ai/plans/2026-04-30-120000-demo/META.yaml",
        ".ai/plans/2026-04-30-120000-demo/TODO.md",
        "src/lib.rs",
    ]

    assert strip_plan_local_changes(paths, plan_dir, root) == ["src/lib.rs"]


def test_changed_plan_dir_names_finds_timestamped_plan_dirs() -> None:
    paths = [
        ".ai/plans/2026-04-29-134035-harden-sync-contract-ci/META.yaml",
        ".ai/plans/2026-04-29-134035-harden-sync-contract-ci/VALIDATION.md",
        ".ai/plans/_templates/META.yaml",
        "src/harness_toolkit/scaffold/cli.py",
    ]

    assert changed_plan_dir_names(paths) == [
        "2026-04-29-134035-harden-sync-contract-ci"
    ]


def test_strip_changed_plan_paths_keeps_lockfile_only_branch_changes() -> None:
    paths = ["apps/svc-a/Cargo.lock", "go.sum"]

    assert strip_changed_plan_paths(paths, [], Path(".")) == paths


def test_git_path_is_ignored_detects_ignored_artifact(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    (tmp_path / ".gitignore").write_text("artifacts/raw/\n")
    ignored = tmp_path / "artifacts" / "raw" / "review.md"
    ignored.parent.mkdir(parents=True)
    ignored.write_text("ignored\n")
    committed = tmp_path / "artifacts" / "summary.md"
    committed.write_text("committable\n")

    assert git_path_is_ignored(tmp_path, ignored) is True
    assert git_path_is_ignored(tmp_path, committed) is False


def test_git_path_is_tracked_requires_index_entry(tmp_path: Path) -> None:
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    artifact = tmp_path / "artifacts" / "summary.md"
    artifact.parent.mkdir()
    artifact.write_text("summary\n")

    assert git_path_is_tracked(tmp_path, artifact) is False

    subprocess.run(
        ["git", "add", "artifacts/summary.md"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )

    assert git_path_is_tracked(tmp_path, artifact) is True
