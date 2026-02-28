"""LabelDialog — form for entering shot metadata."""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QGridLayout, QLabel, QLineEdit,
    QComboBox, QCheckBox, QHBoxLayout, QPushButton, QSpinBox
)
from badminton_labeler.constants import SHOT_TYPES
from badminton_labeler.views.dialogs.hit_area_dialog import HitAreaDialog


class LabelDialog(QDialog):
    def __init__(self, segment, defaults=None, parent=None):
        super().__init__(parent)
        d = defaults or {}
        self.setWindowTitle(f"Label Segment  [{segment.start} to {segment.end}]")
        self.setMinimumWidth(420)
        self.hit_area = d.get("hit_area")
        self._build(segment, d)

    def _build(self, seg, d):
        layout = QVBoxLayout(self); layout.setSpacing(10)
        layout.addWidget(QLabel(f"Frames: {seg.start} → {seg.end}  ({seg.length} frames)"))
        form = QGridLayout(); form.setColumnMinimumWidth(0, 130)

        def row(lbl, w, r): form.addWidget(QLabel(lbl), r, 0); form.addWidget(w, r, 1)

        self.rally_spin = QSpinBox(); self.rally_spin.setRange(1, 9999)
        self.rally_spin.setValue(d.get("rally_number", 1)); row("Rally Number:", self.rally_spin, 0)

        self.player_edit = QLineEdit(str(d.get("player_id", "P1"))); row("Player ID:", self.player_edit, 1)

        self.shot_combo = QComboBox(); self.shot_combo.addItems(SHOT_TYPES)
        if d.get("shot_type") in SHOT_TYPES: self.shot_combo.setCurrentText(d["shot_type"])
        row("Shot Type:", self.shot_combo, 2)

        self.bh_cb = QCheckBox("Yes"); self.bh_cb.setChecked(bool(d.get("backhand", False)))
        row("Backhand:", self.bh_cb, 3)
        self.ah_cb = QCheckBox("Yes"); self.ah_cb.setChecked(bool(d.get("around_head", False)))
        row("Around Head:", self.ah_cb, 4)

        hit_row = QHBoxLayout()
        self.hit_lbl = QLabel(str(self.hit_area) if self.hit_area else "-")
        self.hit_lbl.setStyleSheet("background:#2c3e50;color:white;padding:6px 14px;border-radius:4px;font-size:15px;")
        pick = QPushButton("Select Grid")
        pick.setStyleSheet("background:#8e44ad;color:white;padding:6px;border-radius:4px;")
        pick.clicked.connect(self._pick)
        hit_row.addWidget(self.hit_lbl); hit_row.addWidget(pick)
        form.addWidget(QLabel("Hit Area (1-16):"), 5, 0); form.addLayout(hit_row, 5, 1)
        layout.addLayout(form)

        btns = QHBoxLayout()
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        save   = QPushButton("Save");   save.setDefault(True)
        save.setStyleSheet("background:#27ae60;color:white;padding:8px 18px;border-radius:6px;font-weight:bold;")
        save.clicked.connect(self.accept)
        btns.addWidget(cancel); btns.addStretch(); btns.addWidget(save)
        layout.addLayout(btns)

    def _pick(self):
        dlg = HitAreaDialog(self.hit_area, self)
        if dlg.exec_(): self.hit_area = dlg.get_area(); self.hit_lbl.setText(str(self.hit_area) if self.hit_area else "-")

    def get_data(self):
        return {
            "rally_number": self.rally_spin.value(),
            "player_id":    self.player_edit.text().strip(),
            "shot_type":    self.shot_combo.currentText(),
            "backhand":     int(self.bh_cb.isChecked()),
            "around_head":  int(self.ah_cb.isChecked()),
            "hit_area":     self.hit_area,
        }
