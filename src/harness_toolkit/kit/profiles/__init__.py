"""Built-in and custom profile/check DSL for portable agent workflows.

Profiles describe named verification loops. They intentionally do not execute
those loops; agents should run the suggested commands directly so raw output stays
visible in the normal agent shell loop.
"""

from harness_toolkit.kit.profiles.applicability import (
    _matched_paths,
    _matches_pattern,
    checks_view,
)
from harness_toolkit.kit.profiles.builtins import BUILTIN_PROFILES, loaded_builtins
from harness_toolkit.kit.profiles.catalog import ProfileCatalog
from harness_toolkit.kit.profiles.config import (
    default_config_path,
    load_config_profiles,
    load_harness_config,
)
from harness_toolkit.kit.profiles.guidance import PROFILE_SELECTION_GUIDANCE
from harness_toolkit.kit.profiles.loading import (
    get_loaded_profile,
    get_profile,
    load_profile_catalog,
    profile_names,
)
from harness_toolkit.kit.profiles.models import (
    BUILTIN_PRESETS,
    VALID_RUN_FROM,
    CheckDefinition,
    HarnessConfig,
    LoadedProfile,
    ProfileCheckView,
    ProfileError,
    ProfileName,
    ProfileResolution,
    ProfileSuggestion,
    ReviewDefinition,
    RunFrom,
    TargetBinding,
    WorkflowProfile,
)
from harness_toolkit.kit.profiles.parser import (
    load_profile_file,
    normalize_config_path,
    parse_profile_data,
)
from harness_toolkit.kit.profiles.resolution import resolve_profile
from harness_toolkit.kit.profiles.serialization import (
    checks_to_json,
    profile_to_json,
    profiles_to_json,
    resolution_to_json,
)
from harness_toolkit.kit.profiles.templates import profile_template
from harness_toolkit.kit.profiles.validation import (
    validate_item_name,
    validate_profile_name,
)

__all__ = [
    "PROFILE_SELECTION_GUIDANCE",
    "BUILTIN_PRESETS",
    "BUILTIN_PROFILES",
    "VALID_RUN_FROM",
    "CheckDefinition",
    "HarnessConfig",
    "LoadedProfile",
    "ProfileCatalog",
    "ProfileCheckView",
    "ProfileError",
    "ProfileName",
    "ProfileResolution",
    "ProfileSuggestion",
    "ReviewDefinition",
    "RunFrom",
    "TargetBinding",
    "WorkflowProfile",
    "_matched_paths",
    "_matches_pattern",
    "checks_to_json",
    "checks_view",
    "default_config_path",
    "get_loaded_profile",
    "get_profile",
    "load_config_profiles",
    "loaded_builtins",
    "load_harness_config",
    "load_profile_catalog",
    "load_profile_file",
    "normalize_config_path",
    "parse_profile_data",
    "profile_names",
    "profile_template",
    "profile_to_json",
    "profiles_to_json",
    "resolution_to_json",
    "resolve_profile",
    "validate_item_name",
    "validate_profile_name",
]
