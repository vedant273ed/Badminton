"""
PATTERN: State (Finite State Machine)
───────────────────────────────────────
Replaces the original `if len(markers) == 1 / >= 2` chains
with a clean FSM. The marker workflow has exactly 2 states:
  IDLE       → waiting for first mark
  MARK_START → start marked, waiting for end mark

Transitions are explicit and extensible.
"""
from enum import Enum, auto
from typing import Callable, Optional


class MarkerState(Enum):
    IDLE       = auto()   # no pending markers
    MARK_START = auto()   # start frame marked, waiting for end


class MarkerFSM:
    """
    Finite State Machine for the mark-start → mark-end workflow.

    on_segment_ready(start, end) is called when both marks are set.
    on_status_change(message)    is called on every state transition.
    """

    def __init__(
        self,
        on_segment_ready: Callable[[int, int], None],
        on_status_change: Callable[[str], None],
    ) -> None:
        self._state = MarkerState.IDLE
        self._start_frame: Optional[int] = None
        self._on_segment_ready = on_segment_ready
        self._on_status_change = on_status_change

    # ── public API ───────────────────────────────────────────────
    @property
    def state(self) -> MarkerState:
        return self._state

    @property
    def start_frame(self) -> Optional[int]:
        return self._start_frame

    def mark(self, frame: int) -> None:
        """Called when the user presses Enter on the current frame."""
        if self._state == MarkerState.IDLE:
            self._transition_to_mark_start(frame)
        elif self._state == MarkerState.MARK_START:
            self._transition_to_idle_with_segment(frame)

    def cancel(self) -> None:
        """Called when the user presses Delete."""
        if self._state == MarkerState.MARK_START:
            removed = self._start_frame
            self._start_frame = None
            self._state = MarkerState.IDLE
            self._on_status_change(f"Marker cancelled (was frame {removed}).")

    def reset(self) -> None:
        self._state = MarkerState.IDLE
        self._start_frame = None
        self._on_status_change("Markers: none.")

    # ── private transitions ───────────────────────────────────────
    def _transition_to_mark_start(self, frame: int) -> None:
        self._start_frame = frame
        self._state = MarkerState.MARK_START
        self._on_status_change(
            f"Start marked: Frame {frame}\n\nNavigate to end frame, press Enter again."
        )

    def _transition_to_idle_with_segment(self, end_frame: int) -> None:
        start = self._start_frame
        end   = end_frame
        if start > end:
            start, end = end, start          # swap if marked backwards
        self._start_frame = None
        self._state = MarkerState.IDLE
        self._on_status_change(
            f"Segment: {start} → {end}\n\nPress Shift+Enter to label."
        )
        self._on_segment_ready(start, end)
