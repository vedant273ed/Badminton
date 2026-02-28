"""
PATTERN: MVP — Presenter (the brain)
──────────────────────────────────────
MainPresenter owns all business logic.
It reads/writes AppState, calls Services, fires Commands,
and tells the View (MainWindow) what to display.

The View never calls services or state directly.
"""
import datetime
import os
from typing import Optional

from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QFileDialog, QMessageBox, QApplication

from badminton_labeler.app_state import AppState
from badminton_labeler.commands.segment_commands import (
    AddSegmentCommand, DeleteSegmentCommand, EditSegmentCommand, CommandHistory
)
from badminton_labeler.constants import (
    SHOT_TYPES, AUTOSAVE_INTERVAL_MS, SHORT_SEGMENT_FRAMES, LONG_SEGMENT_FRAMES, safe_color
)
from badminton_labeler.factories.segment_factory import SegmentFactory, SegmentValidationError
from badminton_labeler.models.segment import Segment
from badminton_labeler.services.export_strategy import (
    ExportContext, CSVExportStrategy, MP4ExportStrategy
)
from badminton_labeler.services.session_service import SessionService
from badminton_labeler.services.video_service import VideoService
from badminton_labeler.state_machine.marker_fsm import MarkerFSM
from badminton_labeler.views.dialogs.label_dialog import LabelDialog
from badminton_labeler.views.dialogs.mini_player_dialog import MiniPlayerDialog
from badminton_labeler.views.dialogs.shortcuts_dialog import ShortcutsDialog


class MainPresenter:
    """
    PATTERN: MVP Presenter
    Central coordinator between View, State, Services, Commands.
    """

    def __init__(self, view) -> None:
        self._view           = view
        self._state          = AppState.instance()
        self._video          = VideoService()
        self._session_svc    = SessionService()
        self._history        = CommandHistory()
        self._export_context = ExportContext(strategy=CSVExportStrategy())

        # PATTERN: State — marker FSM
        self._marker_fsm = MarkerFSM(
            on_segment_ready=self._on_segment_ready,
            on_status_change=lambda msg: self._view.set_marker_status(msg),
        )

        # Playback timer
        self._play_timer = QTimer()
        self._play_timer.setTimerType(Qt.PreciseTimer)
        self._play_timer.timeout.connect(self._next_frame)

        # Autosave timer
        self._autosave_timer = QTimer()
        self._autosave_timer.timeout.connect(self._autosave)
        self._autosave_timer.start(AUTOSAVE_INTERVAL_MS)

        self._wire_view_signals()
        QTimer.singleShot(200, self._check_autorestore)

    # ──────────────── Signal wiring ──────────────────────────────
    def _wire_view_signals(self) -> None:
        v = self._view
        v.open_btn.clicked.connect(self.open_video)
        v.save_session_btn.clicked.connect(self.save_session)
        v.load_session_btn.clicked.connect(self.load_session)
        v.export_btn.clicked.connect(self.export_all)
        v.help_btn.clicked.connect(self.show_shortcuts)
        v.exit_btn.clicked.connect(self.confirm_exit)
        v.play_btn.clicked.connect(self.toggle_play)
        v.mark_btn.clicked.connect(self.mark_frame)
        v.label_btn.clicked.connect(self.label_segment)
        v.del_marker_btn.clicked.connect(self.delete_marker)
        v.undo_btn.clicked.connect(self.undo)
        v.redo_btn.clicked.connect(self.redo)
        v.timeline.seek_requested.connect(self.seek)
        v.scrub.sliderPressed.connect(lambda: self._play_timer.stop())
        v.scrub.sliderReleased.connect(lambda: self.seek(v.scrub.value()))
        v.speed_combo.currentIndexChanged.connect(self._update_timer)
        v.match_id_edit.textChanged.connect(lambda t: setattr(self._state.session, "match_id", t))
        v.filter_shot_combo.currentTextChanged.connect(lambda _: self._refresh_all())

    # ──────────────── Video ──────────────────────────────────────
    def open_video(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self._view, "Open Video", "", "Video Files (*.mp4 *.avi *.mov *.mkv)"
        )
        if not path: return
        if not self._video.open(path):
            QMessageBox.critical(self._view, "Error", f"Cannot open video:\n{path}"); return
        self._state.video_path   = path
        self._state.fps          = self._video.fps
        self._state.total_frames = self._video.total_frames
        self._state.current_frame = 0
        self._state.session.video_path = path
        self._state.autosave_path = os.path.splitext(path)[0] + "_autosave.json"
        self._view.scrub.setMaximum(max(self._video.total_frames - 1, 1))
        self._show_frame(0)
        self._view.setWindowTitle(
            f"Badminton Labeler  {os.path.basename(path)}  [{self._video.fps:.1f} FPS]"
        )
        self._view.set_status(
            f"Loaded: {os.path.basename(path)}  |  {self._video.total_frames} frames  |  {self._video.fps:.1f} FPS"
        )

    def _show_frame(self, n: int) -> None:
        rgb = self._video.read_frame(n)
        if rgb is None: return
        self._state.current_frame = n
        self._view.display_frame(rgb)
        self._view.set_frame_label(n, self._state.total_frames)
        self._view.update_timeline(
            self._state.total_frames, n,
            self._state.session.segments, self._state.markers
        )

    def _next_frame(self) -> None:
        if self._state.current_frame >= self._state.total_frames - 1:
            self.toggle_play(); return
        rgb, idx = self._video.read_next_frame()
        if rgb is None: self.toggle_play(); return
        self._state.current_frame = idx
        self._view.display_frame(rgb)
        self._view.set_frame_label(idx, self._state.total_frames)
        self._view.update_timeline(
            self._state.total_frames, idx,
            self._state.session.segments, self._state.markers
        )

    def toggle_play(self) -> None:
        if not self._video.is_open: return
        self._state.playing = not self._state.playing
        self._view.set_play_button(self._state.playing)
        if self._state.playing:
            self._video.seek(self._state.current_frame)
            self._update_timer()
        else:
            self._play_timer.stop()

    def _update_timer(self) -> None:
        if not self._state.playing: return
        speeds   = [0.25, 0.5, 1.0, 2.0]
        interval = max(int(1000 / (self._state.fps * speeds[self._view.speed_combo.currentIndex()])), 1)
        self._play_timer.start(interval)

    def step(self, delta: int) -> None:
        if self._state.playing: self.toggle_play()
        self._show_frame(self._state.current_frame + delta)

    def seek(self, frame: int) -> None:
        if self._state.playing: self.toggle_play()
        self._show_frame(frame)

    # ──────────────── Segmentation ───────────────────────────────
    def mark_frame(self) -> None:
        if not self._video.is_open: return
        self._marker_fsm.mark(self._state.current_frame)

    def _on_segment_ready(self, start: int, end: int) -> None:
        """Called by MarkerFSM when both marks are placed."""
        length = end - start
        # Warn for short/long — but still allow
        if length < SHORT_SEGMENT_FRAMES:
            if QMessageBox.question(
                self._view, "Short Segment", f"{length} frames only — continue?",
                QMessageBox.Yes | QMessageBox.No
            ) != QMessageBox.Yes:
                return
        if length > LONG_SEGMENT_FRAMES:
            if QMessageBox.question(
                self._view, "Long Segment", f"{length} frames — continue?",
                QMessageBox.Yes | QMessageBox.No
            ) != QMessageBox.Yes:
                return
        seg = SegmentFactory.create(start, end)
        cmd = AddSegmentCommand(seg)
        self._history.execute(cmd)
        self._refresh_all()
        self._view.set_status(f"Segment created: {start} to {end}  ({length} frames)")

    def delete_marker(self) -> None:
        self._marker_fsm.cancel()

    def label_segment(self) -> None:
        unlabeled = [s for s in self._state.session.segments if not s.labeled]
        if not unlabeled: self._view.set_status("No unlabeled segments."); return
        seg = unlabeled[-1]; idx = self._state.session.segments.index(seg)
        dlg = LabelDialog(seg, {
            "rally_number": self._state.session.last_rally,
            "player_id":    self._state.session.last_player,
            "shot_type":    self._state.session.last_shot_type,
        }, self._view)
        if not dlg.exec_(): return
        data = dlg.get_data(); rally = data["rally_number"]
        self._state.session.shot_counters.setdefault(rally, 0)
        self._state.session.shot_counters[rally] += 1
        data["shot_number"] = self._state.session.shot_counters[rally]
        data["labeled"]     = True
        cmd = EditSegmentCommand(idx, data)
        self._history.execute(cmd)
        self._state.session.last_rally      = rally
        self._state.session.last_player     = data["player_id"]
        self._state.session.last_shot_type  = data["shot_type"]
        self._refresh_all()
        self._view.set_status(f"Labeled: Rally {rally} Shot {data['shot_number']}  {data['shot_type']} by {data['player_id']}")

    def edit_segment(self, idx: int) -> None:
        segs = self._state.session.segments
        if not (0 <= idx < len(segs)): return
        seg = segs[idx]
        dlg = LabelDialog(seg, {
            "rally_number": seg.rally_number, "player_id": seg.player_id,
            "shot_type":    seg.shot_type,    "backhand":  seg.backhand,
            "around_head":  seg.around_head,  "hit_area":  seg.hit_area,
        }, self._view)
        if not dlg.exec_(): return
        data = dlg.get_data(); data["labeled"] = True
        cmd = EditSegmentCommand(idx, data)
        self._history.execute(cmd)
        self._refresh_all()

    def delete_segment(self, idx: int) -> None:
        cmd = DeleteSegmentCommand(idx)
        self._history.execute(cmd)
        self._refresh_all()
        self._view.set_status(f"Segment {idx + 1} deleted.")

    def preview_segment(self, idx: int) -> None:
        segs = self._state.session.segments
        if not self._state.video_path or not (0 <= idx < len(segs)): return
        if self._state.playing: self.toggle_play()
        MiniPlayerDialog(self._state.video_path, segs[idx], self._state.fps, self._view).exec_()

    def prev_segment(self) -> None:
        segs = self._state.session.segments
        if not segs: return
        c = [s for s in segs if s.start < self._state.current_frame]
        self.seek((max(c, key=lambda s: s.start) if c else max(segs, key=lambda s: s.start)).start)

    def next_segment(self) -> None:
        segs = self._state.session.segments
        if not segs: return
        c = [s for s in segs if s.start > self._state.current_frame]
        self.seek((min(c, key=lambda s: s.start) if c else min(segs, key=lambda s: s.start)).start)

    # ──────────────── Undo / Redo ────────────────────────────────
    def undo(self) -> None:
        if self._history.undo(): self._refresh_all(); self._view.set_status("Undo applied.")
        else: self._view.set_status("Nothing to undo.")

    def redo(self) -> None:
        if self._history.redo(): self._refresh_all(); self._view.set_status("Redo applied.")
        else: self._view.set_status("Nothing to redo.")

    # ──────────────── Session / Export ───────────────────────────
    def save_session(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self._view, "Save Session", "session.json", "JSON (*.json)")
        if not path: return
        try:
            self._session_svc.save(self._state.session, path)
            self._view.set_status(f"Session saved: {path}")
        except Exception as ex:
            QMessageBox.critical(self._view, "Save Error", str(ex))

    def load_session(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self._view, "Load Session", "", "JSON (*.json)")
        if not path: return
        try:
            sess = self._session_svc.load(path)
            self._state.session = sess
            self._view.match_id_edit.setText(sess.match_id)
            self._refresh_all()
            self._view.set_status(f"Session loaded: {len(sess.segments)} segments")
        except Exception as ex:
            QMessageBox.critical(self._view, "Load Error", str(ex))

    def export_all(self) -> None:
        segs = self._state.session.segments
        if not segs: QMessageBox.information(self._view, "Nothing to export", "No segments yet."); return
        out_dir = QFileDialog.getExistingDirectory(self._view, "Select Export Folder")
        if not out_dir: return
        mid = self._state.session.match_id
        # PATTERN: Strategy — use both CSV and MP4 strategies
        csv_count = ExportContext(CSVExportStrategy()).export(segs, out_dir, mid, self._state.fps, self._state.video_path)
        mp4_count = ExportContext(MP4ExportStrategy()).export(segs, out_dir, mid, self._state.fps, self._state.video_path)
        QMessageBox.information(self._view, "Export Complete",
            f"Exported {csv_count} CSV rows, {mp4_count} MP4 clips to:\n{out_dir}")
        self._view.set_status(f"Export complete  {mp4_count} clips  {csv_count} CSV rows.")

    def _autosave(self) -> None:
        if not self._state.session.segments or not self._state.autosave_path: return
        try:
            self._session_svc.save(self._state.session, self._state.autosave_path)
            self._view.set_autosave_label(f"Auto-saved {datetime.datetime.now().strftime('%H:%M:%S')}")
        except Exception:
            self._view.set_autosave_label("Auto-save failed")

    # ──────────────── Restore / misc ─────────────────────────────
    def _check_autorestore(self) -> None:
        sess = self._session_svc.load_last_session()
        if not sess or not sess.segments: return
        n = len(sess.segments)
        r = QMessageBox.question(
            self._view, "Restore Last Session?",
            f"Match: {sess.match_id}  |  {n} segments\nSaved: {sess.saved_at}\n\nRestore?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes
        )
        if r == QMessageBox.Yes:
            self._state.session = sess
            self._view.match_id_edit.setText(sess.match_id)
            self._refresh_all()
            self._view.set_status(f"Session restored ({n} segments)")

    def show_shortcuts(self) -> None:
        ShortcutsDialog(self._view).exec_()

    def confirm_exit(self) -> None:
        segs = self._state.session.segments
        unlabeled = [s for s in segs if not s.labeled]
        msg = "Are you sure you want to exit?"
        if segs:
            msg += f"\n\n{len(segs) - len(unlabeled)} labeled, {len(unlabeled)} unlabeled.\n\nTip: Save Session first."
        if QMessageBox.question(self._view, "Exit", msg, QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self._view.close()

    # ──────────────── Refresh ────────────────────────────────────
    def _refresh_all(self) -> None:
        segs   = self._state.session.segments
        fshot  = self._view.filter_shot_combo.currentText()
        self._view.refresh_segments(segs, fshot)
        self._view.refresh_rallies(segs)
        self._view.refresh_stats(segs)
        self._view.update_timeline(
            self._state.total_frames, self._state.current_frame,
            segs, self._state.markers
        )
        self._update_progress()
        self._view.set_undo_redo_enabled(self._history.can_undo, self._history.can_redo)

    def _update_progress(self) -> None:
        if not self._state.total_frames: return
        covered = set()
        for s in self._state.session.segments:
            covered.update(range(s.start, s.end))
        pct = min(int(len(covered) / self._state.total_frames * 100), 100)
        self._view.set_progress(pct)
