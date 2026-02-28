"""
Segment model — pure data, no UI dependency.
"""
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Segment:
    """Represents one labeled shot segment in the video."""
    start: int
    end: int
    labeled: bool = False
    shot_type: str = ""
    rally_number: int = 1
    shot_number: int = 0
    player_id: str = "P1"
    backhand: int = 0
    around_head: int = 0
    hit_area: Optional[int] = None

    # ── helpers ──────────────────────────────────────────
    @property
    def length(self) -> int:
        return self.end - self.start

    def to_dict(self) -> dict:
        return {
            "start":        self.start,
            "end":          self.end,
            "labeled":      self.labeled,
            "shot_type":    self.shot_type,
            "rally_number": self.rally_number,
            "shot_number":  self.shot_number,
            "player_id":    self.player_id,
            "backhand":     self.backhand,
            "around_head":  self.around_head,
            "hit_area":     self.hit_area,
        }

    @staticmethod
    def from_dict(d: dict) -> "Segment":
        return Segment(
            start=d.get("start", 0),
            end=d.get("end", 0),
            labeled=d.get("labeled", False),
            shot_type=d.get("shot_type", ""),
            rally_number=d.get("rally_number", 1),
            shot_number=d.get("shot_number", 0),
            player_id=d.get("player_id", "P1"),
            backhand=d.get("backhand", 0),
            around_head=d.get("around_head", 0),
            hit_area=d.get("hit_area"),
        )
