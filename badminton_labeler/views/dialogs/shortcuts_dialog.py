"""Keyboard shortcuts reference dialog."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QScrollArea, QWidget, QGridLayout, QPushButton


SHORTCUTS = [
    ("Playback", None),
    ("Space", "Play / Pause"),
    ("Right / Left", "Step 1 frame"),
    ("Shift+Right/Left", "Step 30 frames"),
    ("Segmentation", None),
    ("Enter", "Mark start / end frame"),
    ("Shift+Enter", "Label last unlabeled segment"),
    ("Delete", "Delete last pending marker"),
    ("[", "Jump to previous segment"),
    ("]", "Jump to next segment"),
    ("Editing", None),
    ("Ctrl+Z", "Undo"),
    ("Ctrl+Y / Ctrl+Shift+Z", "Redo"),
    ("File", None),
    ("Ctrl+S", "Export all clips"),
    ("?", "This shortcuts dialog"),
]


class ShortcutsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Keyboard Shortcuts"); self.setFixedSize(420, 460)
        self.setStyleSheet("background:#0d1117;color:#e0e0e0;")
        layout = QVBoxLayout(self); layout.setSpacing(0)
        title = QLabel("  Keyboard Shortcuts")
        title.setStyleSheet("background:#1e2a3a;color:#3498db;font-size:14px;font-weight:bold;padding:10px;border-radius:4px;")
        layout.addWidget(title)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setStyleSheet("background:#0d1117;border:none;")
        inner = QWidget(); inner.setStyleSheet("background:#0d1117;"); grid = QGridLayout(inner)
        grid.setSpacing(0); grid.setContentsMargins(8, 4, 8, 4)
        for ri, (key, val) in enumerate(SHORTCUTS):
            if val is None:
                lbl = QLabel(f"  {key}"); lbl.setStyleSheet("background:#1e2a3a;color:#e67e22;font-weight:bold;font-size:11px;padding:5px 6px;border-radius:3px;")
                grid.addWidget(lbl, ri, 0, 1, 2)
            else:
                kl = QLabel(f"  {key}"); kl.setStyleSheet("background:#2c3e50;color:#3498db;font-family:monospace;font-size:11px;padding:4px 8px;border-radius:3px;")
                vl = QLabel(val); vl.setStyleSheet("color:#ccc;font-size:11px;padding:4px 8px;")
                grid.addWidget(kl, ri, 0); grid.addWidget(vl, ri, 1)
        scroll.setWidget(inner); layout.addWidget(scroll)
        cb = QPushButton("Close"); cb.setStyleSheet("background:#2980b9;color:white;padding:8px;border-radius:4px;font-weight:bold;")
        cb.clicked.connect(self.accept); layout.addWidget(cb)
