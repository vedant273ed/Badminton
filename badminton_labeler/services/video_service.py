"""
Video Service — wraps all OpenCV operations.
Part of the Service Layer (single responsibility).
"""
from typing import Optional, Tuple
import cv2
import numpy as np

from badminton_labeler.constants import DEFAULT_FPS


class VideoService:
    """Handles video file I/O via OpenCV. No UI dependencies."""

    def __init__(self) -> None:
        self._cap: Optional[cv2.VideoCapture] = None
        self.fps: float = DEFAULT_FPS
        self.total_frames: int = 0
        self.video_path: str = ""

    # ── lifecycle ────────────────────────────────────────────────
    def open(self, path: str) -> bool:
        self.release()
        cap = cv2.VideoCapture(path)
        if not cap.isOpened():
            return False
        self._cap         = cap
        self.video_path   = path
        self.fps          = cap.get(cv2.CAP_PROP_FPS) or DEFAULT_FPS
        self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        return True

    def release(self) -> None:
        if self._cap:
            self._cap.release()
            self._cap = None

    @property
    def is_open(self) -> bool:
        return self._cap is not None and self._cap.isOpened()

    # ── frame access ─────────────────────────────────────────────
    def read_frame(self, n: int) -> Optional[np.ndarray]:
        """Seek to frame n and return RGB numpy array, or None."""
        if not self.is_open:
            return None
        n = max(0, min(n, self.total_frames - 1))
        self._cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = self._cap.read()
        if not ret:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    def read_next_frame(self) -> Tuple[Optional[np.ndarray], int]:
        """Read the next sequential frame. Returns (rgb_array, frame_index)."""
        if not self.is_open:
            return None, 0
        ret, frame = self._cap.read()
        if not ret:
            return None, 0
        idx = int(self._cap.get(cv2.CAP_PROP_POS_FRAMES)) - 1
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), idx

    def seek(self, n: int) -> None:
        """Move the read head to frame n."""
        if self.is_open:
            self._cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, n))
