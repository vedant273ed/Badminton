"""
PATTERN: Factory Method
────────────────────────
Centralises Segment construction so that validation and defaults
are in one place. Callers never use Segment(...) directly.

Usage:
    seg = SegmentFactory.create(start=100, end=250)
    seg = SegmentFactory.from_label_data(start, end, label_dict)
"""
from badminton_labeler.models.segment import Segment
from badminton_labeler.constants import SHORT_SEGMENT_FRAMES, LONG_SEGMENT_FRAMES


class SegmentValidationError(ValueError):
    pass


class SegmentFactory:
    """Factory for creating and validating Segment objects."""

    @staticmethod
    def create(start: int, end: int, strict: bool = False) -> Segment:
        """
        Create a bare (unlabeled) segment.
        Raises SegmentValidationError if length is out of bounds and strict=True.
        """
        if start > end:
            start, end = end, start
        length = end - start
        if strict:
            if length < SHORT_SEGMENT_FRAMES:
                raise SegmentValidationError(f"Segment too short: {length} frames.")
            if length > LONG_SEGMENT_FRAMES:
                raise SegmentValidationError(f"Segment too long: {length} frames.")
        return Segment(start=start, end=end)

    @staticmethod
    def from_label_data(start: int, end: int, data: dict) -> Segment:
        """Create a fully labeled segment from dialog output dict."""
        seg = SegmentFactory.create(start, end)
        seg.labeled      = True
        seg.shot_type    = data.get("shot_type", "")
        seg.rally_number = data.get("rally_number", 1)
        seg.shot_number  = data.get("shot_number", 1)
        seg.player_id    = data.get("player_id", "P1")
        seg.backhand     = data.get("backhand", 0)
        seg.around_head  = data.get("around_head", 0)
        seg.hit_area     = data.get("hit_area")
        return seg
