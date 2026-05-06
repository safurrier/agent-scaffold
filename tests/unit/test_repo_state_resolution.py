from __future__ import annotations

from pathlib import Path

import pytest

from harness_toolkit.kit.local import resolve_local_state
from harness_toolkit.kit.state.repo import git_root, repo_key, scope_key
from tests.support.hk2_repo import git_init

pytestmark = pytest.mark.unit


def test_shared_repo_identity_matches_hk2_state(tmp_path: Path) -> None:
    repo = git_init(tmp_path / "repo")
    module = repo / "pkg" / "feature"
    module.mkdir(parents=True)
    root = git_root(module)
    scope = scope_key(root, module)
    key = repo_key(root)
    hk2 = resolve_local_state(module)
    assert root == repo.resolve()
    assert scope == "pkg-feature"
    assert hk2.target_root == root
    assert hk2.target_scope == module.resolve()
    assert hk2.scope == scope
    assert hk2.repo_key == key


def test_shared_scope_key_uses_root_scope_for_repo_root(tmp_path: Path) -> None:
    repo = git_init(tmp_path / "repo")

    assert scope_key(repo, repo) == "root"
