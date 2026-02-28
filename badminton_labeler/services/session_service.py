"""
Session Service — save and load SessionModel to/from JSON.
Part of the Service Layer.
"""
import json
import os
from typing import Optional

from badminton_labeler.models.session import SessionModel
from badminton_labeler.constants import LAST_SESSION_FILE


class SessionService:
    """Handles serialisation of application sessions."""

    def save(self, session: SessionModel, path: str) -> None:
        """Write session to a JSON file."""
        with open(path, "w") as f:
            json.dump(session.to_dict(), f, indent=2)
        self._write_last_session(session)

    def load(self, path: str) -> SessionModel:
        """Load a session from a JSON file."""
        with open(path) as f:
            data = json.load(f)
        return SessionModel.from_dict(data)

    def load_last_session(self) -> Optional[SessionModel]:
        """Load the most recent auto-saved session, or None."""
        if not os.path.exists(LAST_SESSION_FILE):
            return None
        try:
            return self.load(LAST_SESSION_FILE)
        except Exception:
            return None

    def _write_last_session(self, session: SessionModel) -> None:
        try:
            with open(LAST_SESSION_FILE, "w") as f:
                json.dump(session.to_dict(), f, indent=2)
        except Exception:
            pass
