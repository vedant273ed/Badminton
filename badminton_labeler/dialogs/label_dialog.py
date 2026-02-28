from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QGridLayout,
    QLineEdit, QComboBox, QCheckBox, QPushButton,
    QHBoxLayout, QSpinBox
)

from constants import SHOT_TYPES
from dialogs.hit_area_dialog import HitAreaDialog


class LabelDialog(QDialog):
    def __init__(self, segment, defaults=None, parent=None):
        super().__init__(parent)
        self.segment = segment
        self.hit_area = defaults.get("hit_area") if defaults else None
        self.setWindowTitle(
            f"Label Segment [Frame {segment['start']} → {segment['end']}]"
        )
        self.setMinimumWidth(420)
        self._build_ui(defaults or {})

    def _build_ui(self, d):
        layout = QVBoxLayout(self)

        info = QLabel(
            f"Frames: {self.segment['start']} → {self.segment['end']} "
            f"({self.segment['end'] - self.segment['start']} frames)"
        )
        layout.addWidget(info)

        form = QGridLayout()

        self.rally_spin = QSpinBox()
        self.rally_spin.setRange(1, 9999)
        self.rally_spin.setValue(d.get("rally_number", 1))
        form.addWidget(QLabel("Rally Number:"), 0, 0)
        form.addWidget(self.rally_spin, 0, 1)

        self.player_edit = QLineEdit(str(d.get("player_id", "P1")))
        form.addWidget(QLabel("Player ID:"), 1, 0)
        form.addWidget(self.player_edit, 1, 1)

        self.shot_combo = QComboBox()
        self.shot_combo.addItems(SHOT_TYPES)
        if d.get("shot_type") in SHOT_TYPES:
            self.shot_combo.setCurrentText(d["shot_type"])
        form.addWidget(QLabel("Shot Type:"), 2, 0)
        form.addWidget(self.shot_combo, 2, 1)

        self.backhand_cb = QCheckBox("Yes")
        self.backhand_cb.setChecked(bool(d.get("backhand", False)))
        form.addWidget(QLabel("Backhand:"), 3, 0)
        form.addWidget(self.backhand_cb, 3, 1)

        self.around_cb = QCheckBox("Yes")
        self.around_cb.setChecked(bool(d.get("around_head", False)))
        form.addWidget(QLabel("Around Head:"), 4, 0)
        form.addWidget(self.around_cb, 4, 1)

        hit_btn = QPushButton("Select Grid")
        hit_btn.clicked.connect(self._pick_area)
        form.addWidget(QLabel("Hit Area (1–16):"), 5, 0)
        form.addWidget(hit_btn, 5, 1)

        layout.addLayout(form)

        save = QPushButton("Save")
        save.clicked.connect(self.accept)
        layout.addWidget(save)

    def _pick_area(self):
        dlg = HitAreaDialog(self.hit_area, self)
        if dlg.exec_():
            self.hit_area = dlg.get_area()

    def get_data(self):
        return {
            "rally_number": self.rally_spin.value(),
            "player_id": self.player_edit.text().strip(),
            "shot_type": self.shot_combo.currentText(),
            "backhand": int(self.backhand_cb.isChecked()),
            "around_head": int(self.around_cb.isChecked()),
            "hit_area": self.hit_area,
        }