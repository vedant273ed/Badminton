"""
PATTERN: Composite
────────────────────
SegmentCard is a self-contained, reusable composite widget.
It knows how to render a Segment and emit action signals.
The parent (SegmentsPanel) treats all cards uniformly.

Observer pattern: card emits signals; parent listens.
"""
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import pyqtSignal

from badminton_labeler.models.segment import Segment
from badminton_labeler.constants import safe_color
from badminton_labeler.factories.widget_factory import WidgetFactory


class SegmentCard(QFrame):
    """
    PATTERN: Composite — leaf component.
    A self-contained card widget representing one Segment.
    Emits signals for preview / jump / edit / delete.
    """

    # PATTERN: Observer — signals
    preview_requested = pyqtSignal(int)   # segment index
    jump_requested    = pyqtSignal(int)   # frame number
    edit_requested    = pyqtSignal(int)   # segment index
    delete_requested  = pyqtSignal(int)   # segment index

    def __init__(self, segment: Segment, index: int, parent=None) -> None:
        super().__init__(parent)
        self._segment = segment
        self._index   = index
        self._build()

    def _build(self) -> None:
        color   = safe_color(self._segment.shot_type)
        labeled = self._segment.labeled
        self.setStyleSheet(
            f"background:{color}22;border-left:3px solid {color};"
            f"border-radius:4px;padding:4px;"
        )
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(6, 4, 6, 4)

        # Title row
        status = "✓" if labeled else "…"
        rally  = self._segment.rally_number if labeled else "?"
        shot   = self._segment.shot_number  if labeled else "?"
        stype  = self._segment.shot_type    or "-"
        title  = QLabel(f"{status} R{rally} S{shot}  {stype}")
        title.setStyleSheet(f"color:{color};font-weight:bold;font-size:12px;")
        layout.addWidget(title)

        # Sub-info row
        sub_text = (
            f"Player: {self._segment.player_id}  |  "
            f"{self._segment.start} → {self._segment.end}"
        )
        if labeled:
            sub_text += (
                f"  |  BH:{self._segment.backhand} "
                f"AH:{self._segment.around_head} "
                f"Area:{self._segment.hit_area or '-'}"
            )
        sub = QLabel(sub_text)
        sub.setStyleSheet("color:#aaa;font-size:10px;")
        layout.addWidget(sub)

        # Action buttons
        btn_row = QHBoxLayout()
        for label, clr, signal_fn in [
            ("Preview", "#8e44ad", lambda: self.preview_requested.emit(self._index)),
            ("Jump",    "#16a085", lambda: self.jump_requested.emit(self._segment.start)),
            ("Edit",    "#2980b9", lambda: self.edit_requested.emit(self._index)),
            ("Del",     "#c0392b", lambda: self.delete_requested.emit(self._index)),
        ]:
            btn = WidgetFactory.small_button(label, clr)
            btn.clicked.connect(signal_fn)
            btn_row.addWidget(btn)
        btn_row.addStretch()
        layout.addLayout(btn_row)
