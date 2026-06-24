"""Keyboard System (PRD §14) — four selectable input modes; Adaptive switches
automatically from physical-context signals.

This terminal prototype has no physical keyboard, mic, accelerometer, or
ambient-mic hardware, so each mode is mocked at the behavior level rather
than as an on-screen layout:

- **Compact** relies on "aggressive AI word prediction" (PRD §14). Mocked
  here as abbreviation expansion reusing `tier2.py`'s keyword-overlap
  scorer (WIF-015) against a small canned set of full commands, instead of
  a second "closest match" implementation.
- **Standard** is the existing default — full grammar, no change.
- **Voice First** has no mic; `/voice <text>` in the shell is the
  transcription-proxy entry point a real mic button would call.
- **Adaptive** reuses already-mocked state where it exists (the telephony
  backend's `active_call`, the device backend's `dnd` setting) and only
  mocks the two signals with no existing equivalent — `driving` and
  `motion` — via `/sim sensor <signal> on/off`.
"""

from enum import Enum

from . import tier2

COMPACT_EXPANSIONS = {
    "call lena": {"cl", "call", "lena"},
    "message mom take it easy": {"mm", "message", "mom"},
    "what did i miss": {"wdim", "miss", "missed", "digest"},
    "set a timer for 10 minutes": {"timer", "set", "10", "minutes"},
}


class KeyboardMode(str, Enum):
    COMPACT = "compact"
    STANDARD = "standard"
    VOICE_FIRST = "voice_first"
    ADAPTIVE = "adaptive"


class Keyboard:
    def __init__(self) -> None:
        self.mode = KeyboardMode.STANDARD
        self.sensors = {"driving": False, "motion": False}

    def set_mode(self, name: str) -> str:
        key = name.strip().lower().replace(" ", "_")
        try:
            mode = KeyboardMode(key)
        except ValueError:
            raise ValueError(f"no keyboard mode called {name!r}")
        self.mode = mode
        label = mode.value.replace("_", " ").title()
        return f"Keyboard mode: {label}."

    def set_sensor(self, signal: str, on: bool) -> None:
        if signal not in self.sensors:
            raise ValueError(f"no sensor called {signal!r}")
        self.sensors[signal] = on

    def expand_compact(self, text: str) -> str | None:
        """Compact mode only — None means fall through to normal grammar."""
        if self.mode != KeyboardMode.COMPACT:
            return None
        words = tier2.tokenize(text)
        label, score = tier2.best_match(words, COMPACT_EXPANSIONS)
        return label if score > 0 else None

    def adaptive_input(self, active_call: bool, dnd: bool) -> str:
        """PRD §14's context table, in priority order (most overriding first)."""
        if active_call:
            return "keyboard only"
        if self.sensors["driving"]:
            return "voice only, keyboard locked"
        if self.sensors["motion"]:
            return "keyboard"
        if dnd:
            return "keyboard default"
        return "voice nudge"

    def strip(self, active_call: bool, dnd: bool) -> str | None:
        if self.mode == KeyboardMode.ADAPTIVE:
            return f"[keyboard] adaptive · {self.adaptive_input(active_call, dnd)}"
        if self.mode != KeyboardMode.STANDARD:
            return f"[keyboard] {self.mode.value.replace('_', ' ')}"
        return None
