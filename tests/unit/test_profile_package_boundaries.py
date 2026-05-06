from __future__ import annotations

import pytest

from harness_toolkit.kit.profiles import CheckDefinition, ProfileCatalog
from harness_toolkit.kit.profiles.models import WorkflowProfile

pytestmark = pytest.mark.unit


def test_profile_package_reexports_models_and_catalog() -> None:
    catalog = ProfileCatalog.load()
    profile = catalog.get("generic")

    assert isinstance(profile, WorkflowProfile)
    assert isinstance(profile.checks[0], CheckDefinition)
