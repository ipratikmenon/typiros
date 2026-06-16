"""Bridge Layer (PRD §6) — the opacity engine.

Routes tool calls to backends, normalises results to one-line text, and
translates every error into natural language before it reaches the chat.
"""

import time

from .backends.device import Device
from .backends.productivity import Productivity, _parse_duration
from .backends.telephony import Telephony
from .memory import FocusSession, SessionMemory
from .notifications import QuietQueue


class Bridge:
    def __init__(self, memory: SessionMemory, queue: QuietQueue) -> None:
        self.telephony = Telephony()
        self.device = Device()
        self.productivity = Productivity()
        self.memory = memory
        self.queue = queue

    def dispatch(self, tool: str, args: dict) -> str:
        try:
            return self._route(tool, args)
        except Exception as exc:  # every failure becomes language (PRD §2.5)
            return _translate(tool, exc)

    def _route(self, tool: str, args: dict) -> str:
        if tool == "make_call":
            sim = args.get("sim") or self.memory.last_sim
            self.memory.last_sim = sim
            self.memory.last_contact = args["contact"]
            self.memory.last_dispatch = ("make_call", {**args, "sim": sim})
            return self.telephony.make_call(args["contact"], sim)
        if tool == "end_call":
            return self.telephony.end_call()
        if tool == "send_message":
            sim = args.get("sim") or self.memory.last_sim
            self.memory.last_sim = sim
            self.memory.last_contact = args["contact"]
            self.memory.last_dispatch = ("send_message", {**args, "sim": sim})
            return self.telephony.send_message(
                args["contact"], args.get("channel", "sms"), sim, args["body"]
            )
        if tool == "set_setting":
            return self.device.set_setting(args["key"], args["value"])
        if tool == "set_alarm":
            return self.productivity.set_alarm(args["when"])
        if tool == "create_reminder":
            return self.productivity.create_reminder(args["text"], args.get("when"))
        if tool == "set_timer":
            return self.productivity.set_timer(args["duration"])
        if tool == "show_missed":
            return self.queue.digest()
        if tool == "set_digest_cadence":
            interval_str = args["interval"]
            if interval_str == "off":
                self.memory.digest_interval = None
                return "Digest cadence off."
            secs = _parse_duration(interval_str)
            if secs is None:
                raise ValueError(f"couldn't read a duration from {interval_str!r}")
            self.memory.digest_interval = secs
            self.memory.last_digest_at = time.monotonic()
            return f"Digest every {interval_str}."
        if tool == "start_focus":
            duration_str = args["duration"]
            label = args.get("label") or "focus"
            secs = _parse_duration(duration_str)
            if secs is None:
                raise ValueError(f"couldn't read a duration from {duration_str!r}")
            now = time.monotonic()
            self.memory.focus_session = FocusSession(
                label=label,
                start_at=now,
                end_at=now + secs,
                queue_size_at_start=self.queue.size(),
            )
            return f"Focus on {label} — {duration_str}. Type 'end focus' to stop."
        if tool == "end_focus":
            fs = self.memory.focus_session
            if fs is None:
                return "No focus session active."
            self.memory.focus_session = None
            held = self.queue.drain_from(fs.queue_size_at_start)
            if not held:
                return f"Focus session '{fs.label}' ended — nothing held back."
            lines = [f"Focus session '{fs.label}' ended — {len(held)} held back:"]
            lines += [f"  {n.source} ({n.kind}): {n.preview}" for n in held]
            return "\n".join(lines)
        raise ValueError(f"unknown tool {tool!r}")

    def strips(self) -> list[str]:
        """Persistent context strips (PRD §9) — max 3, focus strip first."""
        strips = [self._focus_strip(), self.telephony.strip(), self.productivity.strip()]
        return [s for s in strips if s][:3]

    def _focus_strip(self) -> str | None:
        fs = self.memory.focus_session
        if fs is None:
            return None
        left = max(0, int(fs.end_at - time.monotonic()))
        return f"[focus] {fs.label} · {left // 60}:{left % 60:02d} left"


def _translate(tool: str, exc: Exception) -> str:
    detail = str(exc)
    if tool in ("make_call", "end_call"):
        return f"Couldn't do that — {detail}."
    if tool == "send_message":
        return f"Couldn't send it — {detail}."
    if tool == "set_setting":
        return f"Couldn't change that — {detail}."
    return f"That didn't work — {detail}."
