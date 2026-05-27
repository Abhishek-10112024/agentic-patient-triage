import os
import json
import shutil
from datetime import datetime


RECORDINGS_DIR = "data/recordings"
RESPONSES_DIR = "data/responses"


def make_session_id() -> str:
    """Generate a unique session ID based on the current timestamp."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def save_recording(tmp_path: str, session_id: str) -> str:
    """Persist the WAV recording under data/recordings/ using the session ID.
    Only call this after a successful analysis so we never orphan recordings."""
    os.makedirs(RECORDINGS_DIR, exist_ok=True)
    dest = os.path.join(RECORDINGS_DIR, f"session_{session_id}_recording.wav")
    shutil.copy2(tmp_path, dest)
    return dest


def get_response_audio_path(session_id: str) -> str:
    """Return the canonical path where the TTS audio should be saved."""
    os.makedirs(RESPONSES_DIR, exist_ok=True)
    return os.path.join(RESPONSES_DIR, f"session_{session_id}_response.mp3")


def save_response(response: dict, session_id: str) -> str:
    """Persist the JSON triage result under data/responses/ using the session ID."""
    os.makedirs(RESPONSES_DIR, exist_ok=True)
    dest = os.path.join(RESPONSES_DIR, f"session_{session_id}_response.json")
    with open(dest, "w") as f:
        json.dump(response, f, indent=4)
    return dest
