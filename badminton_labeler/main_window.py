from operator import index, sub

from constants import *
from dialogs.label_dialog import LabelDialog
from widgets.timeline_widget import TimelineWidget
import os
import cv2
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSlider, QFileDialog, QDialog, QLineEdit,
    QComboBox, QCheckBox, QGridLayout, QMessageBox, QFrame,
    QScrollArea, QSizePolicy, QInputDialog, QShortcut, QProgressBar,
    QGroupBox, QSpinBox
)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QRect
from PyQt5.QtGui import QImage, QPixmap, QKeySequence, QPainter, QColor, QFont

class BadmintonLabeler(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Badminton Dataset Labeler")
        self.resize(1100, 750)
        self.setStyleSheet("background:#0d1117;color:#e0e0e0;")

        # State
        self.cap = None
        self.total_frames = 0
        self.current_frame = 0
        self.playing = False
        self.video_path = None
        self.match_id = "M01"

        self.selected_segment_index = None

        self.markers = []          # pending start/end markers (max 2 at a time)
        self.segments = []         # list of segment dicts
        self.undo_stack = []       # for ctrl+z

        self.last_rally = 1
        self.last_player = "P1"
        self.last_shot_type = SHOT_TYPES[0]
        self.shot_counters = {}    # rally_number -> shot count

        self.timer = QTimer()
        self.timer.timeout.connect(self._next_frame)

        self._build_ui()
        self._bind_keys()

    # ── UI ──────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setSpacing(6)
        root.setContentsMargins(8, 8, 8, 8)

        # Top bar
        top = QHBoxLayout()
        self.open_btn = self._btn("📂 Open Video", self._open_video, "#2980b9")
        self.match_id_edit = QLineEdit(self.match_id)
        self.match_id_edit.setFixedWidth(80)
        self.match_id_edit.setPlaceholderText("Match ID")
        self.match_id_edit.setStyleSheet("background:#1e2a3a;color:white;padding:4px;border-radius:4px;")
        self.match_id_edit.textChanged.connect(lambda t: setattr(self, "match_id", t))
        self.export_btn = self._btn("💾 Export All", self._export_all, "#27ae60")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("Segmented: 0%")
        self.progress_bar.setStyleSheet("QProgressBar{background:#1e2a3a;border-radius:4px;height:20px;}"
                                        "QProgressBar::chunk{background:#27ae60;border-radius:4px;}")
        top.addWidget(self.open_btn)
        top.addWidget(QLabel("Match ID:"))
        top.addWidget(self.match_id_edit)
        top.addStretch()
        top.addWidget(self.progress_bar)
        top.addWidget(self.export_btn)
        root.addLayout(top)

        # Main area
        mid = QHBoxLayout()

        # Video
        video_col = QVBoxLayout()
        self.video_label = QLabel("Open a video file to begin")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background:#000;border-radius:6px;")
        self.video_label.setMinimumSize(720, 405)
        video_col.addWidget(self.video_label)

        # Scrub slider
        self.scrub = QSlider(Qt.Horizontal)
        self.scrub.setStyleSheet("QSlider::handle:horizontal{background:#3498db;width:12px;border-radius:6px;}"
                                 "QSlider::groove:horizontal{background:#1e2a3a;height:6px;border-radius:3px;}"
                                 "QSlider::sub-page:horizontal{background:#3498db;border-radius:3px;}")
        self.scrub.sliderMoved.connect(self._seek)
        video_col.addWidget(self.scrub)

        # Timeline
        self.timeline = TimelineWidget()
        self.timeline.seek_requested.connect(self._seek)
        video_col.addWidget(self.timeline)

        # Controls
        ctrl = QHBoxLayout()
        self.play_btn = self._btn("▶ Play", self._toggle_play, "#3498db")
        self.frame_label = QLabel("Frame: 0 / 0")
        self.frame_label.setStyleSheet("font-size:13px;")
        self.speed_combo = QComboBox()
        self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x"])
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.setStyleSheet("background:#1e2a3a;color:white;padding:4px;")
        self.speed_combo.currentIndexChanged.connect(self._update_speed)
        self.mark_btn = self._btn("⏺ Mark [Enter]", self._mark_frame, "#e67e22")
        self.label_btn = self._btn("🏷 Label [Shift+Enter]", self._label_segment, "#9b59b6")
        ctrl.addWidget(self.play_btn)
        ctrl.addWidget(self.frame_label)
        ctrl.addWidget(QLabel("Speed:"))
        ctrl.addWidget(self.speed_combo)
        ctrl.addStretch()
        ctrl.addWidget(self.mark_btn)
        ctrl.addWidget(self.label_btn)
        video_col.addLayout(ctrl)

        mid.addLayout(video_col, 3)

        # Right panel
        right = QVBoxLayout()
        right.setSpacing(6)

        # Marker status
        self.marker_status = QLabel("Markers: none")
        self.marker_status.setStyleSheet(
            "background:#1e2a3a;padding:8px;border-radius:6px;font-size:12px;")
        self.marker_status.setWordWrap(True)
        right.addWidget(self.marker_status)

        # Rally summary
        rally_box = QGroupBox("Rally Summary")
        rally_box.setStyleSheet("QGroupBox{color:#95a5a6;border:1px solid #2c3e50;border-radius:6px;margin-top:8px;}"
                                "QGroupBox::title{padding:0 4px;}")
        rally_layout = QVBoxLayout(rally_box)
        self.rally_label = QLabel("No segments yet")
        self.rally_label.setWordWrap(True)
        self.rally_label.setStyleSheet("font-size:11px;")
        rally_layout.addWidget(self.rally_label)
        right.addWidget(rally_box)

        # Segments list
        seg_box = QGroupBox("Segments")
        seg_box.setStyleSheet("QGroupBox{color:#95a5a6;border:1px solid #2c3e50;border-radius:6px;margin-top:8px;}"
                              "QGroupBox::title{padding:0 4px;}")
        seg_layout = QVBoxLayout(seg_box)
        self.seg_scroll = QScrollArea()
        self.seg_scroll.setWidgetResizable(True)
        self.seg_scroll.setStyleSheet("background:#0d1117;border:none;")
        self.seg_inner = QWidget()
        self.seg_inner_layout = QVBoxLayout(self.seg_inner)
        self.seg_inner_layout.setAlignment(Qt.AlignTop)
        self.seg_scroll.setWidget(self.seg_inner)
        seg_layout.addWidget(self.seg_scroll)
        right.addWidget(seg_box, 1)

        # Delete marker button
        del_marker_btn = self._btn("❌ Delete Last Marker [Del]", self._delete_marker, "#c0392b")
        right.addWidget(del_marker_btn)

        mid.addLayout(right, 1)
        root.addLayout(mid)

        # Status bar
        self.status = QLabel("Open a video to start labeling.")
        self.status.setStyleSheet("color:#95a5a6;font-size:11px;padding:2px;")
        root.addWidget(self.status)

    def _btn(self, text, fn, color="#555"):
        b = QPushButton(text)
        b.clicked.connect(fn)
        b.setStyleSheet(
            f"background:{color};color:white;padding:7px 14px;"
            f"border-radius:5px;font-weight:bold;")
        return b

    # ── Key Bindings ────────────────────────────
    def _bind_keys(self):
        QShortcut(QKeySequence("Space"), self, self._toggle_play)
        QShortcut(QKeySequence("Right"), self, lambda: self._step(1))
        QShortcut(QKeySequence("Left"), self, lambda: self._step(-1))
        QShortcut(QKeySequence("Shift+Right"), self, lambda: self._step(30))
        QShortcut(QKeySequence("Shift+Left"), self, lambda: self._step(-30))
        QShortcut(QKeySequence("Return"), self, self._mark_frame)
        QShortcut(QKeySequence("Shift+Return"), self, self._label_segment)
        QShortcut(QKeySequence("Delete"), self, self._delete_marker)
        QShortcut(QKeySequence("Ctrl+Z"), self, self._undo)
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, self._redo)
        QShortcut(QKeySequence("Ctrl+S"), self, self._export_all)
        QShortcut(QKeySequence("Backspace"), self, self._delete_selected_segment)
    
    # ── Video ───────────────────────────────────
    def _open_video(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if not path:
            return
        self.video_path = path
        self.cap = cv2.VideoCapture(path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.current_frame = 0
        self.scrub.setMaximum(self.total_frames - 1)
        self._show_frame(0)
        self.setWindowTitle(f"Badminton Labeler — {os.path.basename(path)}")
        self.status.setText(f"Loaded: {path}  |  {self.total_frames} frames")

    def _show_frame(self, n):
        if not self.cap:
            return
        n = max(0, min(n, self.total_frames - 1))
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, n)
        ret, frame = self.cap.read()
        if not ret:
            return
        self.current_frame = n
        self.scrub.setValue(n)
        self.frame_label.setText(f"Frame: {n} / {self.total_frames - 1}")
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb.shape
        img = QImage(rgb.data, w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.video_label.setPixmap(pix)
        self._update_timeline()

    def _next_frame(self):
        self._show_frame(self.current_frame + 1)

    def _toggle_play(self):
        if not self.cap:
            return
        self.playing = not self.playing
        if self.playing:
            self.play_btn.setText("⏸ Pause")
            self._update_speed()
        else:
            self.play_btn.setText("▶ Play")
            self.timer.stop()

    def _update_speed(self):
        speeds = [0.25, 0.5, 1.0, 2.0]
        fps = self.cap.get(cv2.CAP_PROP_FPS) if self.cap else 30
        idx = self.speed_combo.currentIndex()
        interval = int(1000 / (fps * speeds[idx]))
        if self.playing:
            self.timer.start(interval)

    def _step(self, delta):
        if self.playing:
            self._toggle_play()
        self._show_frame(self.current_frame + delta)

    def _seek(self, frame):
        if self.playing:
            self._toggle_play()
        self._show_frame(frame)

    # ── Segmentation ────────────────────────────
    def _mark_frame(self):
        if not self.cap:
            return
        f = self.current_frame
        self.markers.append(f)
        self._save_undo()

        if len(self.markers) == 1:
            self.marker_status.setText(f"✅ Start marked: Frame {f}\n\nNavigate to end frame, press Enter again.")
            self.status.setText(f"Start marker set at frame {f}")
        elif len(self.markers) >= 2:
            start, end = sorted(self.markers[:2])
            self.markers = []
            length = end - start

            if length < SHORT_SEGMENT_FRAMES:
                QMessageBox.warning(self, "Short Segment",
                    f"Segment is only {length} frames — that's very short!\nContinue anyway?")
            if length > LONG_SEGMENT_FRAMES:
                QMessageBox.warning(self, "Long Segment",
                    f"Segment is {length} frames — that's quite long!\nContinue anyway?")

            seg = {"start": start, "end": end, "shot_type": "", "labeled": False}
            self.segments.append(seg)
            self.marker_status.setText("Markers: none\n\nPress Shift+Enter to label last segment.")
            self.status.setText(f"Segment created: {start} → {end} ({length} frames)")
            self._refresh_segments()
            self._update_timeline()
            self._update_progress()
    def _label_segment(self):
        if not self.segments:
            self.status.setText("No segments to label.")
            return

        # Priority 1: selected segment
        if self.selected_segment_index is not None:
            if 0 <= self.selected_segment_index < len(self.segments):
                seg = self.segments[self.selected_segment_index]
            else:
                self.status.setText("Invalid selected segment.")
                return
        else:
            # Priority 2: last unlabeled segment
            unlabeled_indices = [
                i for i, s in enumerate(self.segments)
                if not s.get("labeled")
            ]
            if not unlabeled_indices:
                self.status.setText("No unlabeled segments.")
                return
            idx = unlabeled_indices[-1]
            seg = self.segments[idx]
            self.selected_segment_index = idx

        defaults = {
            "rally_number": self.last_rally,
            "player_id": self.last_player,
            "shot_type": self.last_shot_type,
        }

        dlg = LabelDialog(seg, defaults, self)
        if not dlg.exec_():
            return

        data = dlg.get_data()
        rally = data["rally_number"]

        # Safe shot counter rebuild
        if rally not in self.shot_counters:
            self.shot_counters[rally] = 0

        self.shot_counters[rally] += 1

        seg.update(data)
        seg["shot_number"] = self.shot_counters[rally]
        seg["labeled"] = True

        self.last_rally = rally
        self.last_player = data["player_id"]
        self.last_shot_type = data["shot_type"]

        self._refresh_segments()
        self._update_timeline()
        self._update_progress()

        self.status.setText(
            f"Labeled: Rally {rally}, Shot {seg['shot_number']}, "
            f"{data['shot_type']} by {data['player_id']}"
        )
    def _delete_marker(self):
        if self.markers:
            removed = self.markers.pop()
            self.marker_status.setText(f"Marker removed: {removed}")
            self._update_timeline()
        else:
            self.status.setText("No pending markers to delete.")
    def _delete_segment(self, index):
        if index < 0 or index >= len(self.segments):
            return

        self._save_undo()

        deleted = self.segments.pop(index)

        # Fix selection safely
        if self.selected_segment_index is not None:
            if index == self.selected_segment_index:
                self.selected_segment_index = None
            elif index < self.selected_segment_index:
                self.selected_segment_index -= 1

        self._recalculate_shot_numbers()

        self._refresh_segments()
        self._update_timeline()
        self._update_progress()

        self.status.setText(
            f"Deleted segment {deleted.get('start')} → {deleted.get('end')}"
        )
    def _recalculate_shot_numbers(self):
        shot_counters = {}

        for seg in self.segments:
            if not seg.get("labeled"):
                continue

            rally = seg.get("rally_number")
            if rally is None:
                continue

            shot_counters[rally] = shot_counters.get(rally, 0) + 1
            seg["shot_number"] = shot_counters[rally]

        self.shot_counters = shot_counters

    # ── Undo ────────────────────────────────────
    def _save_undo(self):
        import copy
        self.undo_stack.append({
            "segments": copy.deepcopy(self.segments),
            "markers": list(self.markers),
            "shot_counters": dict(self.shot_counters)
        })

    def _undo(self):
        if not self.undo_stack:
            self.status.setText("Nothing to undo.")
            return
        state = self.undo_stack.pop()
        self.segments = state["segments"]
        self.markers = state["markers"]
        self.shot_counters = state["shot_counters"]
        self._refresh_segments()
        self._update_timeline()
        self._update_progress()
        self.status.setText("Undo applied.")

    def _redo(self):
        self.status.setText("Redo not yet implemented — use undo carefully.")

    # ── UI Refresh ──────────────────────────────
    def _update_timeline(self):
        self.timeline.update_state(
            self.total_frames, self.current_frame,
            self.segments, self.markers
        )

    def _update_progress(self):
        if not self.total_frames:
            return
        covered = sum(
            (s.get("end", 0) - s.get("start", 0))
            for s in self.segments
            if s.get("start") is not None and s.get("end") is not None
        )
        pct = min(int(covered / self.total_frames * 100), 100)
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Segmented: {pct}%")

    def _refresh_segments(self):
        # Clear
        for i in reversed(range(self.seg_inner_layout.count())):
            w = self.seg_inner_layout.itemAt(i).widget()
            if w:
                w.deleteLater()

        for idx, seg in enumerate(self.segments):
            color = SHOT_COLORS.get(seg.get("shot_type", ""), "#555")
            labeled = seg.get("labeled", False)
            shot_type = seg.get("shot_type", "—")
            rally = seg.get("rally_number", "?")
            shot_n = seg.get("shot_number", "?")
            pid = seg.get("player_id", "?")

            card = QFrame()
            border = "3px solid #f39c12" if idx == self.selected_segment_index else "none"

            card.setStyleSheet(
                f"""
                background:{color}22;
                border-left:3px solid {color};
                border:{border};
                border-radius:4px;
                padding:4px;
                """
            )

            cl = QVBoxLayout(card)
            cl.setSpacing(2)
            cl.setContentsMargins(6, 4, 6, 4)

            title = QLabel(
                f"{'✅' if labeled else '⏳'} R{rally} S{shot_n} — {shot_type}"
            )
            title.setStyleSheet(
                f"color:{color};font-weight:bold;font-size:12px;"
            )

            sub = QLabel(
                f"Player: {pid}  |  {seg.get('start')}→{seg.get('end')}"
                + (f"  |  BH:{seg.get('backhand',0)} "
                f"AH:{seg.get('around_head',0)} "
                f"Area:{seg.get('hit_area','—')}"
                if labeled else "")
            )
            sub.setStyleSheet("color:#aaa;font-size:10px;")

            delete_btn = QPushButton("Delete")
            delete_btn.setStyleSheet(
                "background:#c0392b;color:white;"
                "font-size:10px;padding:3px;border-radius:3px;"
            )
            delete_btn.clicked.connect(
                lambda _, i=idx: self._delete_segment(i)
            )

            # Selection click
            card.mousePressEvent = lambda e, i=idx: self._select_segment(i)

            cl.addWidget(title)
            cl.addWidget(sub)
            cl.addWidget(delete_btn)

            self.seg_inner_layout.addWidget(card)
        # Rally summary
        rallies = {}
        for s in self.segments:
            r = s.get("rally_number", "?")
            rallies[r] = rallies.get(r, 0) + 1
        if rallies:
            txt = "\n".join(f"Rally {r}: {c} shot(s)" for r, c in sorted(rallies.items()))
            self.rally_label.setText(txt)
        else:
            self.rally_label.setText("No segments yet")
    
    def _select_segment(self, index):
        if 0 <= index < len(self.segments):
            self.selected_segment_index = index
            self._refresh_segments()
    
    def _delete_selected_segment(self):
        if self.selected_segment_index is None:
            self.status.setText("No segment selected.")
            return

        self._delete_segment(self.selected_segment_index)

    # ── Export ──────────────────────────────────
    def _export_all(self):
        import pandas as pd

        labeled = [s for s in self.segments if s.get("labeled")]

        if not labeled:
            QMessageBox.information(self, "Nothing to export", "No labeled segments.")
            return

        out_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save CSV",
            f"{self.match_id}_dataset.csv",
            "CSV Files (*.csv)"
        )

        if not out_path:
            return

        rows = []
        for seg in labeled:
            rows.append({
                "match_id": self.match_id,
                "rally_number": seg.get("rally_number"),
                "shot_number": seg.get("shot_number"),
                "player_id": seg.get("player_id"),
                "shot_type": seg.get("shot_type"),
                "backhand": seg.get("backhand", 0),
                "around_head": seg.get("around_head", 0),
                "hit_area": seg.get("hit_area"),
                "frame_start": seg.get("start"),
                "frame_end": seg.get("end"),
            })

        try:
            pd.DataFrame(rows).to_csv(out_path, index=False)
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", str(e))
            return

        QMessageBox.information(self, "Done", "CSV saved successfully.")

    def closeEvent(self, e):
        if self.cap:
            self.cap.release()
        e.accept()
