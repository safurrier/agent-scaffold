"""Stack registry — maps stack name to Stack instance."""

from __future__ import annotations

from agent_scaffold.stacks.go import GoStack
from agent_scaffold.stacks.python import PythonStack
from agent_scaffold.stacks.rust import RustStack

STACKS: dict[str, PythonStack | GoStack | RustStack] = {
    "python": PythonStack(),
    "go": GoStack(),
    "rust": RustStack(),
}
