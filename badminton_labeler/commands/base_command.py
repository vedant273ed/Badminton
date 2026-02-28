"""
PATTERN: Command (Abstract Base)
─────────────────────────────────
Every user action that should be undoable is a Command object.
Stores enough data to both execute() and undo() the action.
"""
from abc import ABC, abstractmethod


class BaseCommand(ABC):
    """Abstract command — all undoable actions inherit from this."""

    @abstractmethod
    def execute(self) -> None:
        """Perform the action."""

    @abstractmethod
    def undo(self) -> None:
        """Reverse the action."""

    def redo(self) -> None:
        """Default: redo == execute again."""
        self.execute()
