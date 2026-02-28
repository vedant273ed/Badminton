from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor
from constants import SHOT_COLORS


class TimelineWidget(QWidget):
    seek_requested = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.total_frames = 1
        self.current_frame = 0
        self.segments = []
        self.markers = []

    def update_state(self, total, current, segments, markers):
        self.total_frames = max(total, 1)
        self.current_frame = current
        self.segments = segments
        self.markers = markers
        self.update()

    def mousePressEvent(self, e):
        ratio = e.x() / max(self.width(), 1)
        frame = int(ratio * self.total_frames)
        self.seek_requested.emit(frame)

    def paintEvent(self, e):
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#1a1a2e"))

        for seg in self.segments:
            x1 = int(seg["start"] / self.total_frames * w)
            x2 = int(seg["end"] / self.total_frames * w)
            color = SHOT_COLORS.get(seg.get("shot_type", ""), "#555")
            p.fillRect(x1, 10, max(x2 - x1, 2), h - 20, QColor(color))

        p.end()