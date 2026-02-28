from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QGridLayout, QPushButton
from PyQt5.QtCore import Qt


class HitAreaDialog(QDialog):
    def __init__(self, current=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Hit Area")
        self.setFixedSize(300, 320)
        self.selected = current
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(
            "Click to select hit area (1–16):\n"
            "(Top = net side, Bottom = back court)"
        ))

        grid = QGridLayout()
        grid.setSpacing(4)
        self.buttons = {}

        for i in range(16):
            row, col = divmod(i, 4)
            num = i + 1
            btn = QPushButton(str(num))
            btn.setFixedSize(58, 58)
            btn.setCheckable(True)

            if self.selected == num:
                btn.setChecked(True)
                btn.setStyleSheet(
                    "background:#e74c3c;color:white;"
                    "font-weight:bold;font-size:16px;border-radius:6px;"
                )
            else:
                btn.setStyleSheet(
                    "background:#2c3e50;color:white;"
                    "font-size:16px;border-radius:6px;"
                )

            btn.clicked.connect(lambda _, n=num, b=btn: self._select(n, b))
            grid.addWidget(btn, row, col)
            self.buttons[num] = btn

        layout.addLayout(grid)

        ok = QPushButton("Confirm")
        ok.setStyleSheet(
            "background:#27ae60;color:white;"
            "padding:8px;border-radius:6px;"
        )
        ok.clicked.connect(self.accept)
        layout.addWidget(ok)

    def _select(self, num, btn):
        for b in self.buttons.values():
            b.setChecked(False)
            b.setStyleSheet(
                "background:#2c3e50;color:white;"
                "font-size:16px;border-radius:6px;"
            )
        btn.setChecked(True)
        btn.setStyleSheet(
            "background:#e74c3c;color:white;"
            "font-weight:bold;font-size:16px;border-radius:6px;"
        )
        self.selected = num

    def get_area(self):
        return self.selected