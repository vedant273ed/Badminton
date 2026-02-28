"""
PATTERN: Observer (custom signal)
───────────────────────────────────
TimelineWidget emits seek_requested when clicked.
MainWindow (Presenter) listens and responds.
"""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

from badminton_labeler.constants import safe_color


class TimelineWidget(QWidget):
    """Visual scrub bar showing segments and current playhead."""

    seek_requested = pyqtSignal(int)    # PATTERN: Observer

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setFixedHeight(60)
        self.total_frames  = 1
        self.current_frame = 0
        self.segments      = []
        self.markers       = []
        self.setCursor(Qt.PointingHandCursor)

    def update_state(self, total, current, segments, markers) -> None:
        self.total_frames  = max(total, 1)
        self.current_frame = current
        self.segments      = segments
        self.markers       = markers
        self.update()

    def mousePressEvent(self, e) -> None:
        frame = int(e.x() / max(self.width(), 1) * self.total_frames)
        self.seek_requested.emit(frame)

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#1a1a2e"))
        for seg in self.segments:
            x1 = int(seg.start / self.total_frames * w)
            x2 = int(seg.end   / self.total_frames * w)
            p.fillRect(x1, 10, max(x2 - x1, 2), h - 20, QColor(safe_color(seg.shot_type)))
        for m in self.markers:
            x = int(m / self.total_frames * w)
            p.fillRect(x - 1, 0, 3, h, QColor("#f39c12"))
        cx = int(self.current_frame / self.total_frames * w)
        p.fillRect(cx - 1, 0, 2, h, QColor("white"))
        p.end()
