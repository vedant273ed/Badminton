"""
PATTERN: Factory Method (UI widgets)
──────────────────────────────────────
Centralised factory for styled QPushButton and QLabel creation.
Prevents duplicated stylesheet strings across the view layer.
"""
from PyQt5.QtWidgets import QPushButton, QLabel, QFrame


class WidgetFactory:
    """Creates consistently styled Qt widgets."""

    @staticmethod
    def button(
        text: str,
        color: str = "#555555",
        height: int = 30,
        bold: bool = True,
    ) -> QPushButton:
        weight = "bold" if bold else "normal"
        btn = QPushButton(text)
        btn.setStyleSheet(
            f"background:{color};color:white;padding:6px 12px;"
            f"border-radius:5px;font-weight:{weight};"
        )
        if height:
            btn.setFixedHeight(height)
        return btn

    @staticmethod
    def small_button(text: str, color: str = "#555555") -> QPushButton:
        btn = QPushButton(text)
        btn.setFixedHeight(22)
        btn.setStyleSheet(
            f"background:{color};color:white;font-size:10px;"
            f"border-radius:3px;padding:0 6px;"
        )
        return btn

    @staticmethod
    def status_label(text: str = "") -> QLabel:
        lbl = QLabel(text)
        lbl.setStyleSheet(
            "background:#1e2a3a;padding:8px;border-radius:6px;font-size:12px;"
        )
        lbl.setWordWrap(True)
        return lbl

    @staticmethod
    def separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color:#2c3e50;")
        return sep
