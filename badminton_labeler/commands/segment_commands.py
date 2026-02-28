"""
PATTERN: Command (Concrete Commands)
──────────────────────────────────────
Concrete command objects for segment operations.
Each stores the data needed to undo/redo cleanly.
"""
import copy
from badminton_labeler.commands.base_command import BaseCommand
from badminton_labeler.app_state import AppState
from badminton_labeler.models.segment import Segment


class AddSegmentCommand(BaseCommand):
    """Command: add a new segment."""

    def __init__(self, segment: Segment) -> None:
        self._segment = segment

    def execute(self) -> None:
        AppState.instance().session.segments.append(self._segment)

    def undo(self) -> None:
        segs = AppState.instance().session.segments
        if self._segment in segs:
            segs.remove(self._segment)


class DeleteSegmentCommand(BaseCommand):
    """Command: delete a segment at a given index."""

    def __init__(self, index: int) -> None:
        self._index = index
        self._deleted: Segment | None = None

    def execute(self) -> None:
        segs = AppState.instance().session.segments
        if 0 <= self._index < len(segs):
            self._deleted = segs.pop(self._index)

    def undo(self) -> None:
        if self._deleted is not None:
            AppState.instance().session.segments.insert(self._index, self._deleted)


class EditSegmentCommand(BaseCommand):
    """Command: edit an existing segment (stores before/after state)."""

    def __init__(self, index: int, new_data: dict) -> None:
        self._index = index
        self._new_data = new_data
        self._old_data: dict | None = None

    def execute(self) -> None:
        segs = AppState.instance().session.segments
        if 0 <= self._index < len(segs):
            self._old_data = segs[self._index].to_dict()
            for k, v in self._new_data.items():
                setattr(segs[self._index], k, v)

    def undo(self) -> None:
        if self._old_data is None:
            return
        segs = AppState.instance().session.segments
        if 0 <= self._index < len(segs):
            for k, v in self._old_data.items():
                setattr(segs[self._index], k, v)


class CommandHistory:
    """
    PATTERN: Command — History Manager
    Manages undo/redo stacks. Used by the Presenter.
    """

    def __init__(self) -> None:
        self._undo_stack: list[BaseCommand] = []
        self._redo_stack: list[BaseCommand] = []

    def execute(self, command: BaseCommand) -> None:
        command.execute()
        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> bool:
        if not self._undo_stack:
            return False
        cmd = self._undo_stack.pop()
        cmd.undo()
        self._redo_stack.append(cmd)
        return True

    def redo(self) -> bool:
        if not self._redo_stack:
            return False
        cmd = self._redo_stack.pop()
        cmd.redo()
        self._undo_stack.append(cmd)
        return True

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)
