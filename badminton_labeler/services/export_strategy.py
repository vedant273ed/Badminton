"""
PATTERN: Strategy
──────────────────
Export behaviour is encapsulated behind an interface.
Swap CSV ↔ JSON ↔ MP4 without changing the caller.

Usage:
    exporter = ExportContext(strategy=CSVExportStrategy())
    exporter.export(segments, output_dir, match_id, fps, video_path)
"""
import csv
import json
import os
import subprocess
from abc import ABC, abstractmethod
from typing import List

from badminton_labeler.models.segment import Segment


class ExportStrategy(ABC):
    """Abstract export strategy interface."""

    @abstractmethod
    def export(
        self,
        segments: List[Segment],
        output_dir: str,
        match_id: str,
        fps: float,
        video_path: str,
    ) -> int:
        """Returns number of items exported."""


# ── Concrete Strategy 1: CSV ──────────────────────────────────────
class CSVExportStrategy(ExportStrategy):
    """Exports labeled segments to a CSV metadata file."""

    def export(self, segments, output_dir, match_id, fps, video_path) -> int:
        rows = [self._seg_to_row(s, match_id) for s in segments if s.labeled]
        if not rows:
            return 0
        csv_path = os.path.join(output_dir, f"{match_id}_dataset.csv")
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
        return len(rows)

    @staticmethod
    def _seg_to_row(s: Segment, match_id: str) -> dict:
        r = str(s.rally_number).zfill(3)
        sh = str(s.shot_number).zfill(2)
        pid = (s.player_id or "P?").replace(" ", "")
        st  = (s.shot_type or "Unknown").replace(" ", "")
        return {
            "filename":     f"{match_id}_R{r}_S{sh}_{pid}_{st}_BH{s.backhand}_AH{s.around_head}_{s.hit_area or 0}.mp4",
            "match_id":     match_id,
            "rally_number": s.rally_number,
            "shot_number":  s.shot_number,
            "player_id":    s.player_id,
            "shot_type":    s.shot_type,
            "backhand":     s.backhand,
            "around_head":  s.around_head,
            "hit_area":     s.hit_area or 0,
            "frame_start":  s.start,
            "frame_end":    s.end,
        }


# ── Concrete Strategy 2: JSON ─────────────────────────────────────
class JSONExportStrategy(ExportStrategy):
    """Exports all segments (including unlabeled) to a JSON file."""

    def export(self, segments, output_dir, match_id, fps, video_path) -> int:
        data = [s.to_dict() for s in segments]
        path = os.path.join(output_dir, f"{match_id}_segments.json")
        with open(path, "w") as f:
            json.dump(data, f, indent=2)
        return len(data)


# ── Concrete Strategy 3: MP4 clips via ffmpeg ─────────────────────
class MP4ExportStrategy(ExportStrategy):
    """Cuts individual MP4 clip files using ffmpeg."""

    def export(self, segments, output_dir, match_id, fps, video_path) -> int:
        exported = 0
        for s in segments:
            if not s.labeled:
                continue
            r   = str(s.rally_number).zfill(3)
            sh  = str(s.shot_number).zfill(2)
            pid = (s.player_id or "P?").replace(" ", "")
            st  = (s.shot_type or "Unknown").replace(" ", "")
            fname = f"{match_id}_R{r}_S{sh}_{pid}_{st}_BH{s.backhand}_AH{s.around_head}_{s.hit_area or 0}.mp4"
            out   = os.path.join(output_dir, fname)
            t_s   = s.start / fps
            t_d   = s.length / fps
            cmd   = ["ffmpeg", "-y", "-ss", str(t_s), "-i", video_path,
                     "-t", str(t_d), "-c:v", "libx264", "-c:a", "aac", out]
            try:
                subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                exported += 1
            except (FileNotFoundError, subprocess.CalledProcessError):
                pass
        return exported


# ── Context ───────────────────────────────────────────────────────
class ExportContext:
    """
    PATTERN: Strategy — Context
    Holds a reference to the current strategy and delegates to it.
    Strategy can be swapped at runtime.
    """

    def __init__(self, strategy: ExportStrategy) -> None:
        self._strategy = strategy

    def set_strategy(self, strategy: ExportStrategy) -> None:
        self._strategy = strategy

    def export(self, segments, output_dir, match_id, fps, video_path) -> int:
        return self._strategy.export(segments, output_dir, match_id, fps, video_path)
