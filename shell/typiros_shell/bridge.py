"""Bridge Layer (PRD §6) — the opacity engine.

Routes tool calls to backends, normalises results to one-line text, and
translates every error into natural language before it reaches the chat.
"""

from .backends.device import Device
from .backends.productivity import Productivity
from .backends.telephony import Telephony
from .memory import SessionMemory
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
            return self.telephony.make_call(args["contact"], sim)
        if tool == "end_call":
            return self.telephony.end_call()
        if tool == "send_message":
            sim = args.get("sim") or self.memory.last_sim
            self.memory.last_contact = args["contact"]
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
        raise ValueError(f"unknown tool {tool!r}")

    def strips(self) -> list[str]:
        """Persistent context strips (PRD §9) — max 3."""
        strips = [self.telephony.strip(), self.productivity.strip()]
        return [s for s in strips if s][:3]


def _translate(tool: str, exc: Exception) -> str:
    detail = str(exc)
    if tool in ("make_call", "end_call"):
        return f"Couldn't do that — {detail}."
    if tool == "send_message":
        return f"Couldn't send it — {detail}."
    if tool == "set_setting":
        return f"Couldn't change that — {detail}."
    return f"That didn't work — {detail}."
