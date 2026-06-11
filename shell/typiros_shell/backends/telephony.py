"""Mock telephony backend. Signatures match PRD §5 tool manifest so the
real backend (ModemManager/ofono, Phase 1 M4) is a drop-in swap."""

import time

from ..contacts import Contact


class Telephony:
    def __init__(self) -> None:
        self.active_call: tuple[Contact, str] | None = None
        self._call_started: float = 0.0
        self.sent_messages: list[dict] = []

    def make_call(self, contact: Contact, sim: str) -> str:
        if self.active_call:
            raise RuntimeError(f"already on a call with {self.active_call[0].name}")
        self.active_call = (contact, sim)
        self._call_started = time.monotonic()
        return f"Calling {contact.name} — {sim}."

    def end_call(self) -> str:
        if not self.active_call:
            raise RuntimeError("no active call")
        contact, _sim = self.active_call
        elapsed = self.call_elapsed()
        self.active_call = None
        return f"Call ended — {contact.name}, {elapsed}."

    def send_message(self, contact: Contact, channel: str, sim: str, body: str) -> str:
        self.sent_messages.append(
            {"to": contact, "channel": channel, "sim": sim, "body": body}
        )
        via = channel.upper() if channel == "sms" else channel.title()
        return f"Sent to {contact.name} — {via} ({sim})."

    def call_elapsed(self) -> str:
        secs = int(time.monotonic() - self._call_started)
        return f"{secs // 60}:{secs % 60:02d}"

    def strip(self) -> str | None:
        if not self.active_call:
            return None
        contact, sim = self.active_call
        return f"[call] {contact.name} · {sim} · {self.call_elapsed()}"
