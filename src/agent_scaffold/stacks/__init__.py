"""Stack registry — maps stack name to Stack instance."""

from __future__ import annotations

from agent_scaffold.stacks.go import GoStack
from agent_scaffold.stacks.python import PythonStack

STACKS: dict[str, PythonStack | GoStack] = {
    "python": PythonStack(),
    "go": GoStack(),
}
