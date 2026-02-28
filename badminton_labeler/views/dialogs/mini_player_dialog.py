"""MiniPlayerDialog — looping clip preview window."""
import cv2
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QSlider, QHBoxLayout, QPushButton, QComboBox
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap


class MiniPlayerDialog(QDialog):
    def __init__(self, video_path, seg, fps, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Preview  R{seg.rally_number} S{seg.shot_number}  {seg.shot_type}")
        self.setFixedSize(500, 400); self.setStyleSheet("background:#0d1117;color:white;")
        self.start_frame = seg.start; self.end_frame = seg.end
        self.fps = max(fps, 1); self.current = self.start_frame
        self.loop = True; self.playing = True
        self.cap = cv2.VideoCapture(video_path)
        layout = QVBoxLayout(self); layout.setSpacing(4)
        self.display = QLabel(); self.display.setAlignment(Qt.AlignCenter)
        self.display.setStyleSheet("background:#000;border-radius:4px;"); self.display.setMinimumHeight(280)
        layout.addWidget(self.display)
        self.mini_scrub = QSlider(Qt.Horizontal)
        self.mini_scrub.setMinimum(self.start_frame); self.mini_scrub.setMaximum(self.end_frame)
        self.mini_scrub.sliderMoved.connect(self._scrub); layout.addWidget(self.mini_scrub)
        self.frame_lbl = QLabel(f"Frame: {self.start_frame}"); layout.addWidget(self.frame_lbl)
        ctrl = QHBoxLayout()
        self.play_btn = QPushButton("Pause")
        self.play_btn.setStyleSheet("background:#e67e22;color:white;padding:5px 12px;border-radius:4px;font-weight:bold;")
        self.play_btn.clicked.connect(self._toggle)
        self.loop_btn = QPushButton("Loop: ON"); self.loop_btn.setCheckable(True); self.loop_btn.setChecked(True)
        self.loop_btn.setStyleSheet("background:#2c3e50;color:white;padding:5px 10px;border-radius:4px;")
        self.loop_btn.toggled.connect(lambda on: (setattr(self, "loop", on), self.loop_btn.setText("Loop: ON" if on else "Loop: OFF")))
        self.spd = QComboBox(); self.spd.addItems(["0.25x", "0.5x", "1x", "2x"]); self.spd.setCurrentIndex(2)
        self.spd.setStyleSheet("background:#1e2a3a;color:white;padding:3px;")
        self.spd.currentIndexChanged.connect(self._update_speed)
        close_btn = QPushButton("Close"); close_btn.setStyleSheet("background:#922b21;color:white;padding:5px 12px;border-radius:4px;font-weight:bold;")
        close_btn.clicked.connect(self.close)
        total_f = self.end_frame - self.start_frame
        ctrl.addWidget(self.play_btn); ctrl.addWidget(self.loop_btn)
        ctrl.addWidget(QLabel("Speed:")); ctrl.addWidget(self.spd); ctrl.addStretch()
        ctrl.addWidget(QLabel(f"{total_f}f  {total_f / self.fps:.2f}s")); ctrl.addWidget(close_btn)
        layout.addLayout(ctrl)
        self.ptimer = QTimer(); self.ptimer.timeout.connect(self._advance)
        self._update_speed(); self._show(self.start_frame)

    def _toggle(self):
        self.playing = not self.playing; self.play_btn.setText("Pause" if self.playing else "Play")
        if self.playing: self._update_speed()
        else: self.ptimer.stop()

    def _update_speed(self):
        if self.playing: self.ptimer.start(int(1000 / (self.fps * [0.25, 0.5, 1.0, 2.0][self.spd.currentIndex()])))

    def _advance(self):
        if self.current >= self.end_frame:
            if self.loop: self.current = self.start_frame
            else: self.ptimer.stop(); self.playing = False; self.play_btn.setText("Play"); return
        self._show(self.current); self.current += 1

    def _scrub(self, val): self.current = val; self._show(val)

    def _show(self, n):
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, n); ret, frame = self.cap.read()
        if not ret: return
        self.mini_scrub.setValue(n); self.frame_lbl.setText(f"Frame: {n}  (+{n - self.start_frame})")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); h, w, ch = rgb.shape
        img = QImage(bytes(rgb.data), w, h, ch * w, QImage.Format_RGB888)
        self.display.setPixmap(QPixmap.fromImage(img).scaled(self.display.width(), self.display.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def closeEvent(self, e): self.ptimer.stop(); self.cap.release(); e.accept()
