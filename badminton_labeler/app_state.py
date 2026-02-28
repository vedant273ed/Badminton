"""
PATTERN: Singleton
─────────────────
AppState is the single, shared source of truth for the whole app.
Only one instance ever exists — all layers read/write through it.

Usage:
    state = AppState.instance()
    state.session.segments.append(seg)
"""
from __future__ import annotations
from typing import Optional

from badminton_labeler.models.session import SessionModel


class AppState:
    """Singleton holding all runtime application state."""

    _instance: Optional["AppState"] = None

    def __init__(self) -> None:
        if AppState._instance is not None:
            raise RuntimeError("Use AppState.instance() — do not instantiate directly.")
        self.session: SessionModel = SessionModel()
        self.video_path: str = ""
        self.total_frames: int = 0
        self.current_frame: int = 0
        self.fps: float = 30.0
        self.playing: bool = False
        self.markers: list = []        # pending start/end markers
        self.autosave_path: str = ""

    @classmethod
    def instance(cls) -> "AppState":
        if cls._instance is None:
            cls._instance = AppState()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """For testing — wipes the singleton."""
        cls._instance = None
