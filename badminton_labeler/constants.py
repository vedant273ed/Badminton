"""
Application-wide constants and configuration.
Single place to change shot types, colors, timing.
"""

SHOT_TYPES = [
    "Short Serve", "Long Serve", "Toss", "Lift", "Dribble",
    "Smash", "Jump Smash", "Tab", "Block", "Drive",
    "Low Drop", "High Drop", "Netkill"
]

SHOT_COLORS = {
    "Short Serve": "#3498db", "Long Serve": "#2980b9",
    "Toss": "#9b59b6",        "Lift": "#8e44ad",
    "Dribble": "#1abc9c",     "Smash": "#e74c3c",
    "Jump Smash": "#c0392b",  "Tab": "#e67e22",
    "Block": "#f39c12",       "Drive": "#27ae60",
    "Low Drop": "#16a085",    "High Drop": "#2ecc71",
    "Netkill": "#d35400"
}

FALLBACK_COLOR_PALETTE = [
    "#e74c3c", "#3498db", "#2ecc71", "#f39c12",
    "#9b59b6", "#1abc9c", "#e67e22", "#95a5a6",
    "#c0392b", "#16a085"
]

SHORT_SEGMENT_FRAMES  = 5
LONG_SEGMENT_FRAMES   = 300
AUTOSAVE_INTERVAL_MS  = 5 * 60 * 1000   # 5 minutes
DEFAULT_FPS           = 30.0
DEFAULT_MATCH_ID      = "M01"
DEFAULT_PLAYER_ID     = "P1"

import os
LAST_SESSION_FILE = os.path.join(
    os.path.expanduser("~"), ".badminton_labeler_last_session.json"
)


def safe_color(shot_type: str) -> str:
    """Return a valid 6-digit hex color for the given shot type."""
    c = SHOT_COLORS.get(shot_type or "", "#555555")
    if len(c) == 4:          # #RGB  →  #RRGGBB
        c = "#" + c[1]*2 + c[2]*2 + c[3]*2
    return c
