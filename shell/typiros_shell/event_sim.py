"""Background event simulator for interactive testing (PRD §9, §19.1).

Pushes sample inbound events to the quiet queue on a daemon thread so
the quiet-indicator increments between REPL turns without any user action.
Toggled at runtime: /sim auto on [interval_secs]  /sim auto off

Not used in the scripted demo (demo.txt uses explicit /sim commands).
"""

import threading
from .notifications import QuietQueue

SAMPLE_EVENTS = [
    ("sms", "Mom", "are you free this weekend?"),
    ("call", "Philip Sharma", "missed call"),
    ("sms", "Lena", "let me know when you're done"),
    ("sms", "Dr Osei", "your appointment is confirmed"),
    ("call", "Unknown", "voicemail left"),
]


class EventSimulator:
    def __init__(self, queue: QuietQueue) -> None:
        self._queue = queue
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._idx = 0

    def start(self, interval: float = 30.0) -> None:
        self.stop()
        self._stop.clear()
        self._thread = threading.Thread(
            target=self._loop, args=(interval,), daemon=True
        )
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()

    def _loop(self, interval: float) -> None:
        while not self._stop.wait(interval):
            kind, source, preview = SAMPLE_EVENTS[self._idx % len(SAMPLE_EVENTS)]
            self._queue.push(kind, source, preview)
            self._idx += 1
