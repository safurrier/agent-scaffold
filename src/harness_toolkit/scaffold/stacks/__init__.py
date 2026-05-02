"""Stack registry — maps stack name to Stack instance."""

from __future__ import annotations

from harness_toolkit.scaffold.stacks.go import GoStack
from harness_toolkit.scaffold.stacks.python import PythonStack
from harness_toolkit.scaffold.stacks.rust import RustStack

STACKS: dict[str, PythonStack | GoStack | RustStack] = {
    "python": PythonStack(),
    "go": GoStack(),
    "rust": RustStack(),
}
