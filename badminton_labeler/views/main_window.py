"""
PATTERN: Facade
────────────────
MainWindow is a thin UI shell. It only:
  1. Builds and lays out widgets
  2. Wires signals → presenter methods
  3. Exposes update methods the presenter calls

All logic lives in the Presenter.
MainWindow never imports AppState, services, or commands directly.
"""
import os
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QSlider, QComboBox, QLineEdit, QProgressBar, QGroupBox,
    QScrollArea, QTabWidget, QFrame, QShortcut
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap, QKeySequence

from badminton_labeler.constants import SHOT_TYPES, safe_color
from badminton_labeler.factories.widget_factory import WidgetFactory
from badminton_labeler.views.widgets.timeline_widget import TimelineWidget
from badminton_labeler.views.widgets.stats_panel import StatsPanel
from badminton_labeler.views.widgets.segment_card import SegmentCard


class MainWindow(QMainWindow):
    """
    PATTERN: Facade — pure UI shell.
    Presenter is injected after construction.
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Badminton Dataset Labeler")
        self.resize(1200, 800)
        self.setStyleSheet("background:#0d1117;color:#e0e0e0;")
        self._presenter = None
        self._build_ui()
        self._bind_keys()

    def set_presenter(self, presenter) -> None:
        """Inject presenter (avoids circular import)."""
        self._presenter = presenter

    # ──────────────── Build UI ───────────────────────────────────
    def _build_ui(self) -> None:
        central = QWidget(); self.setCentralWidget(central)
        root = QVBoxLayout(central); root.setSpacing(6); root.setContentsMargins(8, 8, 8, 8)
        root.addLayout(self._build_top_bar())
        mid = QHBoxLayout()
        mid.addLayout(self._build_video_column(), 3)
        mid.addLayout(self._build_right_panel(), 1)
        root.addLayout(mid)
        self.status_bar = QLabel("Open a video to start labeling.")
        self.status_bar.setStyleSheet("color:#95a5a6;font-size:11px;padding:2px;")
        root.addWidget(self.status_bar)

    def _build_top_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.open_btn         = WidgetFactory.button("Open Video",   "#2980b9")
        self.save_session_btn = WidgetFactory.button("Save Session", "#1a6b55")
        self.load_session_btn = WidgetFactory.button("Load Session", "#1a5276")
        self.shot_types_btn   = WidgetFactory.button("+ Shot Types", "#6c3483")
        self.export_btn       = WidgetFactory.button("Export All",   "#27ae60")
        self.help_btn         = WidgetFactory.button("? Help",       "#2471a3")
        self.exit_btn         = WidgetFactory.button("Exit",         "#922b21")
        self.match_id_edit    = QLineEdit("M01")
        self.match_id_edit.setFixedWidth(80)
        self.match_id_edit.setStyleSheet("background:#1e2a3a;color:white;padding:4px;border-radius:4px;")
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True); self.progress_bar.setFormat("Segmented: 0%")
        self.progress_bar.setFixedWidth(160)
        self.progress_bar.setStyleSheet("QProgressBar{background:#1e2a3a;border-radius:4px;}QProgressBar::chunk{background:#27ae60;border-radius:4px;}")
        self.autosave_label = QLabel("Auto-save: --")
        self.autosave_label.setStyleSheet("color:#27ae60;font-size:10px;min-width:130px;")
        for w in [self.open_btn, QLabel("Match:"), self.match_id_edit,
                  self.save_session_btn, self.load_session_btn, self.shot_types_btn]:
            bar.addWidget(w)
        bar.addStretch()
        for w in [self.autosave_label, self.progress_bar, self.export_btn, self.help_btn, self.exit_btn]:
            bar.addWidget(w)
        return bar

    def _build_video_column(self) -> QVBoxLayout:
        col = QVBoxLayout()
        self.video_label = QLabel("Open a video file to begin")
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setStyleSheet("background:#000;border-radius:6px;")
        self.video_label.setMinimumSize(720, 405)
        col.addWidget(self.video_label)
        self.scrub = QSlider(Qt.Horizontal)
        self.scrub.setStyleSheet(
            "QSlider::handle:horizontal{background:#3498db;width:12px;border-radius:6px;}"
            "QSlider::groove:horizontal{background:#1e2a3a;height:6px;border-radius:3px;}"
            "QSlider::sub-page:horizontal{background:#3498db;border-radius:3px;}")
        col.addWidget(self.scrub)
        self.timeline = TimelineWidget()
        col.addWidget(self.timeline)
        ctrl = QHBoxLayout()
        self.play_btn    = WidgetFactory.button("Play", "#3498db")
        self.frame_label = QLabel("Frame: 0 / 0"); self.frame_label.setStyleSheet("font-size:13px;")
        self.speed_combo = QComboBox(); self.speed_combo.addItems(["0.25x", "0.5x", "1x", "2x"])
        self.speed_combo.setCurrentIndex(2)
        self.speed_combo.setStyleSheet("background:#1e2a3a;color:white;padding:4px;")
        self.mark_btn  = WidgetFactory.button("Mark [Enter]",        "#e67e22")
        self.label_btn = WidgetFactory.button("Label [Shift+Enter]", "#9b59b6")
        for w in [self.play_btn, self.frame_label, QLabel("Speed:"), self.speed_combo]:
            ctrl.addWidget(w)
        ctrl.addStretch()
        ctrl.addWidget(self.mark_btn); ctrl.addWidget(self.label_btn)
        col.addLayout(ctrl)
        return col

    def _build_right_panel(self) -> QVBoxLayout:
        col = QVBoxLayout(); col.setSpacing(6)
        self.marker_status = WidgetFactory.status_label("Markers: none")
        col.addWidget(self.marker_status)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(
            "QTabWidget::pane{border:1px solid #2c3e50;border-radius:4px;}"
            "QTabBar::tab{background:#1e2a3a;color:#aaa;padding:6px 10px;border-radius:3px;margin-right:2px;font-size:11px;}"
            "QTabBar::tab:selected{background:#2c3e50;color:white;}")
        self._build_segments_tab()
        self._build_stats_tab()
        self._build_rallies_tab()
        col.addWidget(self.tabs, 1)
        act = QHBoxLayout()
        self.del_marker_btn = WidgetFactory.button("Del Marker [Del]", "#c0392b")
        self.undo_btn = WidgetFactory.button("Undo [Ctrl+Z]", "#7f8c8d")
        self.redo_btn = WidgetFactory.button("Redo [Ctrl+Y]", "#7f8c8d")
        act.addWidget(self.del_marker_btn)
        act.addWidget(self.undo_btn); act.addWidget(self.redo_btn)
        col.addLayout(act)
        return col

    def _build_segments_tab(self) -> None:
        tab = QWidget(); stl = QVBoxLayout(tab); stl.setSpacing(4); stl.setContentsMargins(4, 4, 4, 4)
        fbox = QGroupBox("Filter")
        fbox.setStyleSheet("QGroupBox{color:#95a5a6;border:1px solid #2c3e50;border-radius:6px;margin-top:6px;}QGroupBox::title{padding:0 4px;}")
        from PyQt5.QtWidgets import QGridLayout
        fl = QGridLayout(fbox); fl.setSpacing(4)
        fl.addWidget(QLabel("Shot:"), 0, 0)
        self.filter_shot_combo = QComboBox(); self.filter_shot_combo.addItems(["All"] + SHOT_TYPES)
        self.filter_shot_combo.setStyleSheet("background:#1e2a3a;color:white;padding:3px;")
        fl.addWidget(self.filter_shot_combo, 0, 1, 1, 2)
        clr = WidgetFactory.small_button("Clear", "#555")
        fl.addWidget(clr, 0, 3)
        stl.addWidget(fbox)
        self.seg_count_lbl = QLabel("0 segments"); self.seg_count_lbl.setStyleSheet("color:#95a5a6;font-size:10px;padding:2px 4px;")
        stl.addWidget(self.seg_count_lbl)
        self.seg_scroll = QScrollArea(); self.seg_scroll.setWidgetResizable(True); self.seg_scroll.setStyleSheet("background:#0d1117;border:none;")
        self.seg_inner = QWidget(); self.seg_inner_layout = QVBoxLayout(self.seg_inner); self.seg_inner_layout.setAlignment(Qt.AlignTop)
        self.seg_scroll.setWidget(self.seg_inner)
        stl.addWidget(self.seg_scroll)
        self.tabs.addTab(tab, "Segments")
        clr.clicked.connect(lambda: self.filter_shot_combo.setCurrentIndex(0))

    def _build_stats_tab(self) -> None:
        tab = QWidget(); sl = QVBoxLayout(tab); sl.setContentsMargins(6, 6, 6, 6)
        self.stats_panel = StatsPanel(); sl.addWidget(self.stats_panel)
        self.stats_summary = QLabel("No data yet."); self.stats_summary.setWordWrap(True)
        self.stats_summary.setStyleSheet("font-size:11px;color:#aaa;padding:4px;")
        sl.addWidget(self.stats_summary); sl.addStretch()
        self.tabs.addTab(tab, "Stats")

    def _build_rallies_tab(self) -> None:
        tab = QWidget(); rl = QVBoxLayout(tab); rl.setContentsMargins(6, 6, 6, 6)
        self.rally_label = QLabel("No segments yet"); self.rally_label.setWordWrap(True)
        self.rally_label.setStyleSheet("font-size:11px;")
        rl.addWidget(self.rally_label); rl.addStretch()
        self.tabs.addTab(tab, "Rallies")

    # ──────────────── Key bindings → presenter ───────────────────
    def _bind_keys(self) -> None:
        def _p(method):
            return lambda: getattr(self._presenter, method)() if self._presenter else None
        QShortcut(QKeySequence("Space"),        self, _p("toggle_play"))
        QShortcut(QKeySequence("Right"),        self, lambda: self._presenter.step(1)   if self._presenter else None)
        QShortcut(QKeySequence("Left"),         self, lambda: self._presenter.step(-1)  if self._presenter else None)
        QShortcut(QKeySequence("Shift+Right"),  self, lambda: self._presenter.step(30)  if self._presenter else None)
        QShortcut(QKeySequence("Shift+Left"),   self, lambda: self._presenter.step(-30) if self._presenter else None)
        QShortcut(QKeySequence("Return"),       self, _p("mark_frame"))
        QShortcut(QKeySequence("Shift+Return"), self, _p("label_segment"))
        QShortcut(QKeySequence("Delete"),       self, _p("delete_marker"))
        QShortcut(QKeySequence("Ctrl+Z"),       self, _p("undo"))
        QShortcut(QKeySequence("Ctrl+Y"),       self, _p("redo"))
        QShortcut(QKeySequence("Ctrl+Shift+Z"), self, _p("redo"))
        QShortcut(QKeySequence("Ctrl+S"),       self, _p("export_all"))
        QShortcut(QKeySequence("["),            self, _p("prev_segment"))
        QShortcut(QKeySequence("]"),            self, _p("next_segment"))
        QShortcut(QKeySequence("?"),            self, _p("show_shortcuts"))

    # ──────────────── Update methods (called by Presenter) ───────
    def display_frame(self, rgb_array) -> None:
        import numpy as np
        h, w, ch = rgb_array.shape
        img = QImage(bytes(rgb_array.data), w, h, ch * w, QImage.Format_RGB888)
        pix = QPixmap.fromImage(img).scaled(
            self.video_label.width(), self.video_label.height(),
            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(pix)

    def set_frame_label(self, current: int, total: int) -> None:
        self.frame_label.setText(f"Frame: {current} / {total - 1}")
        self.scrub.setValue(current)

    def set_status(self, text: str) -> None:
        self.status_bar.setText(text)

    def set_marker_status(self, text: str) -> None:
        self.marker_status.setText(text)

    def set_autosave_label(self, text: str) -> None:
        self.autosave_label.setText(text)

    def set_progress(self, pct: int) -> None:
        self.progress_bar.setValue(pct)
        self.progress_bar.setFormat(f"Segmented: {pct}%")

    def set_play_button(self, playing: bool) -> None:
        self.play_btn.setText("Pause" if playing else "Play")

    def set_undo_redo_enabled(self, can_undo: bool, can_redo: bool) -> None:
        self.undo_btn.setEnabled(can_undo)
        self.redo_btn.setEnabled(can_redo)

    def refresh_segments(self, segments, filter_shot: str = "All") -> None:
        """Re-render segment cards using the Composite pattern."""
        while self.seg_inner_layout.count():
            item = self.seg_inner_layout.takeAt(0)
            if item.widget(): item.widget().setParent(None)
        visible = 0
        for idx, seg in enumerate(segments):
            if filter_shot != "All" and seg.shot_type != filter_shot:
                continue
            visible += 1
            card = SegmentCard(seg, idx)
            card.preview_requested.connect(lambda i: self._presenter.preview_segment(i) if self._presenter else None)
            card.jump_requested.connect(lambda f: self._presenter.seek(f) if self._presenter else None)
            card.edit_requested.connect(lambda i: self._presenter.edit_segment(i) if self._presenter else None)
            card.delete_requested.connect(lambda i: self._presenter.delete_segment(i) if self._presenter else None)
            self.seg_inner_layout.addWidget(card)
        total = len(segments)
        self.seg_count_lbl.setText(f"{visible} of {total} shown" if visible != total else f"{total} segment(s)")

    def refresh_rallies(self, segments) -> None:
        rallies = {}
        for s in segments:
            r = s.rally_number if s.labeled else "?"
            rallies[r] = rallies.get(r, 0) + 1
        newline = chr(10)
        self.rally_label.setText(
            newline.join(f"Rally {r}: {c} shot(s)" for r, c in sorted(rallies.items(), key=lambda x: str(x[0])))
            if rallies else "No segments yet"
        )

    def refresh_stats(self, segments) -> None:
        self.stats_panel.update_stats(segments)
        labeled = [s for s in segments if s.labeled]
        if not labeled:
            self.stats_summary.setText("No labeled segments yet.")
            return
        total = len(labeled); counts = {}; players = {}
        for s in labeled:
            counts[s.shot_type]  = counts.get(s.shot_type, 0) + 1
            players[s.player_id] = players.get(s.player_id, 0) + 1
        top3        = ", ".join(f"{t}({c})" for t, c in sorted(counts.items(), key=lambda x: -x[1])[:3])
        rally_count = len(set(s.rally_number for s in labeled))
        player_str  = ", ".join(f"{p}:{c}" for p, c in sorted(players.items()))
        self.stats_summary.setText(
            f"Total: {total}  |  Rallies: {rally_count}\n"
            f"Top shots: {top3}\nPlayers: {player_str}"
        )

    def update_timeline(self, total, current, segments, markers) -> None:
        self.timeline.update_state(total, current, segments, markers)
        self.scrub.setMaximum(max(total - 1, 1))
