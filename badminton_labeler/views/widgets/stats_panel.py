"""Stats panel — paints a horizontal bar chart of shot type counts."""
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QColor, QFont

from badminton_labeler.constants import safe_color


class StatsPanel(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.counts: dict = {}
        self.setMinimumHeight(180)

    def update_stats(self, segments) -> None:
        self.counts = {}
        for s in segments:
            if s.labeled and s.shot_type:
                self.counts[s.shot_type] = self.counts.get(s.shot_type, 0) + 1
        self.update()

    def paintEvent(self, e) -> None:
        p = QPainter(self)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor("#0d1117"))
        if not self.counts:
            p.setPen(QColor("#555"))
            p.setFont(QFont("Arial", 9))
            p.drawText(0, 0, w, h, Qt.AlignCenter, "No labeled segments yet")
            p.end()
            return
        total = sum(self.counts.values())
        mx    = max(self.counts.values(), default=1)
        items = sorted(self.counts.items(), key=lambda x: -x[1])
        bar_h = max(14, (h - 10) // max(len(items), 1))
        p.setFont(QFont("Arial", 8))
        for i, (shot, count) in enumerate(items):
            y  = 5 + i * bar_h
            bw = int((count / mx) * (w - 115))
            p.fillRect(82, y + 2, w - 115, bar_h - 5, QColor("#1e2a3a"))
            p.fillRect(82, y + 2, bw,      bar_h - 5, QColor(safe_color(shot)))
            label = shot[:11] + "..." if len(shot) > 12 else shot
            p.setPen(QColor("#ccc"))
            p.drawText(0, y, 80, bar_h, Qt.AlignRight | Qt.AlignVCenter, label)
            p.setPen(QColor("#aaa"))
            p.drawText(w - 32, y, 32, bar_h, Qt.AlignRight | Qt.AlignVCenter,
                       f"{count} {int(count / total * 100)}%")
        p.end()
