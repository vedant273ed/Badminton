"""
Session model — serialisable snapshot of all app state.
"""
import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from badminton_labeler.models.segment import Segment
from badminton_labeler.constants import DEFAULT_MATCH_ID, DEFAULT_PLAYER_ID, SHOT_TYPES


@dataclass
class SessionModel:
    match_id: str = DEFAULT_MATCH_ID
    video_path: str = ""
    segments: List[Segment] = field(default_factory=list)
    shot_counters: Dict[int, int] = field(default_factory=dict)
    last_rally: int = 1
    last_player: str = DEFAULT_PLAYER_ID
    last_shot_type: str = SHOT_TYPES[0]
    saved_at: str = ""

    def to_dict(self) -> dict:
        return {
            "match_id":      self.match_id,
            "video_path":    self.video_path,
            "segments":      [s.to_dict() for s in self.segments],
            "shot_counters": {str(k): v for k, v in self.shot_counters.items()},
            "last_rally":    self.last_rally,
            "last_player":   self.last_player,
            "last_shot_type":self.last_shot_type,
            "saved_at":      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def from_dict(d: dict) -> "SessionModel":
        raw_sc = d.get("shot_counters", {})
        shot_counters = {
            int(k) if str(k).isdigit() else k: v
            for k, v in raw_sc.items()
        }
        return SessionModel(
            match_id=d.get("match_id", DEFAULT_MATCH_ID),
            video_path=d.get("video_path", ""),
            segments=[Segment.from_dict(s) for s in d.get("segments", [])],
            shot_counters=shot_counters,
            last_rally=d.get("last_rally", 1),
            last_player=d.get("last_player", DEFAULT_PLAYER_ID),
            last_shot_type=d.get("last_shot_type", SHOT_TYPES[0]),
            saved_at=d.get("saved_at", ""),
        )
