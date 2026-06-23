"""Mock Media agent (PRD §16 Phase 2). Real backend: MPRIS/native player API."""

import time


class Media:
    def __init__(self) -> None:
        self.current_track: str | None = None
        self.playing: bool = False
        self._started_at: float = 0.0

    def play(self, track: str) -> str:
        self.current_track = track
        self.playing = True
        self._started_at = time.monotonic()
        return f"Playing — {track}."

    def pause(self) -> str:
        if self.current_track is None:
            raise RuntimeError("nothing is playing")
        if not self.playing:
            return f"Already paused — {self.current_track}."
        self.playing = False
        return f"Paused — {self.current_track}."

    def now_playing(self) -> str:
        if self.current_track is None:
            return "Nothing playing."
        status = "Playing" if self.playing else "Paused"
        return f"{status} — {self.current_track}."

    def strip(self) -> str | None:
        if self.current_track is None:
            return None
        status = "playing" if self.playing else "paused"
        return f"[media] {self.current_track} · {status}"
