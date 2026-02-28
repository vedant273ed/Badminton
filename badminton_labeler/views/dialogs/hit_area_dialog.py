"""HitAreaDialog — 4×4 grid for selecting court hit area."""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QPushButton


class HitAreaDialog(QDialog):
    def __init__(self, current=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Hit Area")
        self.setFixedSize(300, 320)
        self.selected = current
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Click to select hit area (1-16):"))
        grid = QGridLayout(); grid.setSpacing(4)
        self.buttons = {}
        ON  = "background:#e74c3c;color:white;font-weight:bold;font-size:16px;border-radius:6px;"
        OFF = "background:#2c3e50;color:white;font-size:16px;border-radius:6px;"
        for i in range(16):
            row, col = divmod(i, 4); num = i + 1
            btn = QPushButton(str(num)); btn.setFixedSize(58, 58); btn.setCheckable(True)
            btn.setStyleSheet(ON if self.selected == num else OFF)
            btn.setChecked(self.selected == num)
            btn.clicked.connect(lambda _, n=num: self._select(n))
            grid.addWidget(btn, row, col); self.buttons[num] = btn
        layout.addLayout(grid)
        ok = QPushButton("Confirm")
        ok.setStyleSheet("background:#27ae60;color:white;padding:8px;border-radius:6px;")
        ok.clicked.connect(self.accept); layout.addWidget(ok)

    def _select(self, num):
        ON  = "background:#e74c3c;color:white;font-weight:bold;font-size:16px;border-radius:6px;"
        OFF = "background:#2c3e50;color:white;font-size:16px;border-radius:6px;"
        for n, b in self.buttons.items():
            b.setChecked(n == num); b.setStyleSheet(ON if n == num else OFF)
        self.selected = num

    def get_area(self): return self.selected
