"""Mock productivity backend: alarms, reminders, timers (PRD §5)."""

import re
import time


class Productivity:
    def __init__(self) -> None:
        self.alarms: list[str] = []
        self.reminders: list[dict] = []
        self._timer_end: float = 0.0
        self._timer_label: str = ""

    def set_alarm(self, when: str) -> str:
        self.alarms.append(when)
        return f"Alarm set — {when}."

    def create_reminder(self, text: str, when: str | None) -> str:
        self.reminders.append({"text": text, "when": when})
        suffix = f" — {when}" if when else ""
        return f"Reminder: {text}{suffix}."

    def set_timer(self, duration: str) -> str:
        secs = _parse_duration(duration)
        if secs is None:
            raise ValueError(f"couldn't read a duration from {duration!r}")
        self._timer_end = time.monotonic() + secs
        self._timer_label = duration
        return f"Timer running — {duration}."

    def strip(self) -> str | None:
        if self._timer_end <= time.monotonic():
            return None
        left = int(self._timer_end - time.monotonic())
        return f"[timer] {self._timer_label} · {left // 60}:{left % 60:02d} left"


def _parse_duration(text: str) -> int | None:
    m = re.search(r"(\d+)\s*(seconds?|secs?|s|minutes?|mins?|m|hours?|hrs?|h)\b", text)
    if not m:
        return None
    n = int(m.group(1))
    unit = m.group(2)[0]
    return n * {"s": 1, "m": 60, "h": 3600}[unit]
