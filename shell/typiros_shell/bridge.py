"""Bridge Layer (PRD §6) — the opacity engine.

Routes tool calls to backends, normalises results to one-line text, and
translates every error into natural language before it reaches the chat.
"""

import time

from .backends.android import AndroidContainer
from .backends.device import Device
from .backends.files import Files
from .backends.finance import Finance
from .backends.information import Information
from .backends.media import Media
from .backends.navigation import Navigation
from .backends.productivity import Productivity, _parse_duration
from .backends.telephony import Telephony
from .biometric import BiometricGate
from .episodic_memory import EpisodicMemory
from .keyboard import Keyboard
from .memory import FocusSession, SessionMemory
from .notifications import QuietQueue
from .user_memory import UserMemory

# Tool → Biometric Gate domain (PRD §15). Checked by the Shell before
# dispatch so a pending biometric challenge can pause the turn.
SENSITIVE_TOOLS = {"send_payment": "finance"}


class Bridge:
    def __init__(
        self,
        memory: SessionMemory,
        queue: QuietQueue,
        user_memory: UserMemory,
        episodic_memory: EpisodicMemory,
    ) -> None:
        self.telephony = Telephony()
        self.device = Device()
        self.productivity = Productivity()
        self.android = AndroidContainer()
        self.media = Media()
        self.navigation = Navigation()
        self.information = Information()
        self.files = Files()
        self.finance = Finance()
        self.biometric = BiometricGate()
        self.keyboard = Keyboard()
        self.memory = memory
        self.queue = queue
        self.user_memory = user_memory
        self.episodic_memory = episodic_memory
        self.android.allowlist |= self.user_memory.enabled_apps()

    def dispatch(self, tool: str, args: dict) -> str:
        try:
            return self._route(tool, args)
        except Exception as exc:  # every failure becomes language (PRD §2.5)
            return _translate(tool, exc)

    def _route(self, tool: str, args: dict) -> str:
        if tool == "make_call":
            contact = args["contact"]
            sim = (
                args.get("sim")
                or self.user_memory.get_sim_preference(contact.name)
                or self.memory.last_sim
            )
            self.memory.last_sim = sim
            self.memory.last_contact = contact
            self.memory.last_dispatch = ("make_call", {**args, "sim": sim})
            result = self.telephony.make_call(contact, sim)
            self.episodic_memory.log(contact.name, result)
            return result
        if tool == "end_call":
            contact = self.telephony.active_call[0] if self.telephony.active_call else None
            result = self.telephony.end_call()
            if contact:
                self.episodic_memory.log(contact.name, result)
            return result
        if tool == "send_message":
            channel = args.get("channel", "sms")
            self.memory.last_contact = args["contact"]
            if self.android.is_installed(channel):
                if not self.android.is_allowed(channel):
                    raise PermissionError(
                        f"{channel} isn't enabled yet — try `enable app {channel}`"
                    )
                self.memory.last_dispatch = ("send_message", {**args, "sim": self.memory.last_sim})
                result = self.android.send(channel, args["contact"], args["body"])
                self.episodic_memory.log(args["contact"].name, result)
                return result
            sim = (
                args.get("sim")
                or self.user_memory.get_sim_preference(args["contact"].name)
                or self.memory.last_sim
            )
            self.memory.last_sim = sim
            self.memory.last_dispatch = ("send_message", {**args, "sim": sim})
            result = self.telephony.send_message(args["contact"], channel, sim, args["body"])
            self.episodic_memory.log(args["contact"].name, result)
            return result
        if tool == "enable_app":
            result = self.android.enable(args["app"])
            self.user_memory.enable_app(args["app"].lower())
            return result
        if tool == "play_track":
            return self.media.play(args["track"])
        if tool == "pause_media":
            return self.media.pause()
        if tool == "now_playing":
            return self.media.now_playing()
        if tool == "navigate":
            return self.navigation.navigate(args["destination"])
        if tool == "nav_eta":
            return self.navigation.eta()
        if tool == "current_route":
            return self.navigation.current_route()
        if tool == "stop_navigation":
            return self.navigation.stop()
        if tool == "get_weather":
            return self.information.weather(args["city"])
        if tool == "get_time":
            return self.information.time()
        if tool == "get_fact":
            return self.information.fact(args["query"])
        if tool == "find_file":
            return self.files.find_file(args["query"])
        if tool == "recent_files":
            return self.files.recent_files()
        if tool == "balance":
            return self.finance.balance()
        if tool == "send_payment":
            result = self.finance.send_payment(args["contact"], args["amount"])
            self.episodic_memory.log(args["contact"].name, result)
            return result
        if tool == "set_keyboard_mode":
            return self.keyboard.set_mode(args["name"])
        if tool == "episode_history":
            return self._episode_history(args.get("contact"))
        if tool == "show_overlay":
            return self._overlay_content(args["kind"])
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
        """Persistent context strips (PRD §9) — max 3, priority order."""
        strips = [
            self._focus_strip(),
            self.telephony.strip(),
            self.productivity.strip(),
            self.media.strip(),
            self.navigation.strip(),
            self.keyboard.strip(
                active_call=bool(self.telephony.active_call),
                dnd=self.device.settings["dnd"] == "on",
            ),
        ]
        return [s for s in strips if s][:3]

    def _focus_strip(self) -> str | None:
        fs = self.memory.focus_session
        if fs is None:
            return None
        left = max(0, int(fs.end_at - time.monotonic()))
        return f"[focus] {fs.label} · {left // 60}:{left % 60:02d} left"

    # ----- episodic memory (PRD §13, Phase 3 M15) -----

    def _episode_history(self, contact) -> str:
        name = contact.name if contact else None
        rows = self.episodic_memory.recent(name)
        if not rows:
            return f"No history with {name} yet." if name else "No history yet."
        header = f"History with {name}:" if name else "Recent history:"
        lines = [header]
        lines += [f"  {c} — {s}" for _ts, c, s in rows]
        return "\n".join(lines)

    # ----- full-screen overlays (PRD §8, Phase 3 M15; TUI only) -----

    def _overlay_content(self, kind: str) -> str:
        if kind == "media":
            return self.media.now_playing()
        if kind == "maps":
            return self.navigation.current_route()
        if kind == "photos":
            return "128 photos · 3 albums (Camera Roll, Screenshots, Favorites)."
        raise ValueError(f"no overlay called {kind!r}")


def _translate(tool: str, exc: Exception) -> str:
    detail = str(exc)
    if tool in ("make_call", "end_call"):
        return f"Couldn't do that — {detail}."
    if tool == "send_message":
        return f"Couldn't send it — {detail}."
    if tool == "set_setting":
        return f"Couldn't change that — {detail}."
    if tool == "enable_app":
        return f"Couldn't enable that — {detail}."
    if tool in ("play_track", "pause_media", "now_playing"):
        return f"Couldn't do that — {detail}."
    if tool in ("navigate", "nav_eta", "current_route", "stop_navigation"):
        return f"Couldn't do that — {detail}."
    if tool in ("get_weather", "get_time", "get_fact"):
        return f"Don't have that yet — {detail}."
    if tool in ("find_file", "recent_files"):
        return f"Couldn't find that — {detail}."
    if tool in ("balance", "send_payment"):
        return f"Couldn't do that — {detail}."
    if tool == "set_keyboard_mode":
        return f"Couldn't switch that — {detail}."
    if tool == "episode_history":
        return f"Couldn't pull that up — {detail}."
    if tool == "show_overlay":
        return f"Couldn't show that — {detail}."
    return f"That didn't work — {detail}."
