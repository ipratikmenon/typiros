"""The chat window — the entire UI (PRD §8), rendered as a line REPL.

Grayscale, text-only, no chrome (PRD §19.4). Strips render as a header
line; the quiet-queue indicator sits in the prompt. M5 swaps this layer
for a TUI without touching intent/bridge/backends.
"""

import re
import sys
import time

from . import contacts, intent, tier2
from .bridge import SENSITIVE_TOOLS, Bridge
from .contacts import Contact
from .episodic_memory import DEFAULT_DB_PATH as DEFAULT_EPISODIC_DB_PATH
from .episodic_memory import EpisodicMemory
from .event_sim import EventSimulator
from .intent import Clarify, Escalate, Quit, Say, ToolCall
from .memory import Pending, SessionMemory
from .notifications import QuietQueue
from .user_memory import DEFAULT_DB_PATH, UserMemory

CORRECTION_RE = re.compile(r"no,?\s+(primary|secondary|whatsapp)\.?", re.IGNORECASE)
MACRO_DEF_RE = re.compile(r"when i type (\S+),\s*(.+)", re.IGNORECASE)


class Shell:
    def __init__(self) -> None:
        self.memory = SessionMemory()
        self.queue = QuietQueue()
        self.echo_input = not sys.stdin.isatty()
        # Scripted/piped runs (demo.txt, tests) stay ephemeral so they're
        # reproducible; interactive runs persist to the User memory layer.
        db_path = ":memory:" if self.echo_input else DEFAULT_DB_PATH
        self.user_memory = UserMemory(db_path)
        self.memory.macros.update(self.user_memory.macros())
        episodic_db_path = ":memory:" if self.echo_input else DEFAULT_EPISODIC_DB_PATH
        self.episodic_memory = EpisodicMemory(episodic_db_path)
        self.bridge = Bridge(self.memory, self.queue, self.user_memory, self.episodic_memory)
        self.sim = EventSimulator(self.queue)

    # ----- one turn of the single loop (PRD §3) -----

    def handle(self, raw: str) -> str | None:
        """Returns response text, or None to quit."""
        if raw.startswith("/sim "):           # dev-only: simulate inbound event
            return self._simulate(raw[5:])
        if raw.startswith("/voice "):          # mic-button proxy (PRD §14 Voice First)
            return self.handle(raw[len("/voice "):])

        if self.memory.pending:
            resolved = self._fill_pending(raw)
            if resolved is not None:
                return resolved

        stripped = raw.strip()
        low = stripped.lower()

        if low in ("again", "/again"):
            return self._recall()
        if low in ("edit", "/edit"):
            return self._show_last()
        if m := CORRECTION_RE.fullmatch(stripped):
            return self._correct(m.group(1))
        if m := MACRO_DEF_RE.fullmatch(stripped.rstrip(".")):
            return self._define_macro(m.group(1).lower(), m.group(2))
        if low in self.memory.macros:
            return self._run_macro(low)

        text = intent.resolve_pronouns(stripped, self.memory.last_contact)
        result = intent.parse(text)
        if isinstance(result, Escalate) and (expanded := self.bridge.keyboard.expand_compact(text)):
            result = intent.parse(expanded)
        if isinstance(result, Quit):
            return None
        if isinstance(result, Say):
            return result.text
        if isinstance(result, Escalate):
            return tier2.route(result.text)
        if isinstance(result, Clarify):
            self.memory.pending = result.pending
            return self._render_clarify(result)
        if isinstance(result, ToolCall):
            self.memory.last_raw = stripped
            return self._dispatch(result.tool, result.args)
        return ""

    # ----- Biometric Gate (PRD §15): sensitive tools pause for a passphrase -----

    def _dispatch(self, tool: str, args: dict) -> str:
        domain = SENSITIVE_TOOLS.get(tool)
        if domain and not self.bridge.biometric.is_unlocked(domain):
            self.memory.pending = Pending(tool, args, "biometric")
            return "Confirm with your passphrase to continue:"
        return self.bridge.dispatch(tool, args)

    # ----- correction flow (PRD §11: "No, Secondary." OS remembers) -----

    def _correct(self, value: str) -> str:
        # Routed through _dispatch(), not bridge.dispatch() directly, so a
        # corrected redispatch still passes the Biometric Gate (PRD §15) if
        # last_dispatch ever tracks a sensitive tool — it doesn't today
        # (make_call/send_message only), but this keeps the gate uniform
        # regardless of entry point rather than relying on that staying true.
        if not self.memory.last_dispatch:
            return "Nothing to correct yet."
        tool, args = self.memory.last_dispatch
        low = value.lower()
        if low == "whatsapp":
            if tool != "send_message":
                return "Can't switch that to WhatsApp."
            return self._dispatch(tool, {**args, "channel": "whatsapp"})
        new_sim = value.title()
        if tool == "make_call":
            self._dispatch("end_call", {})  # hang up before redialling
        result = self._dispatch(tool, {**args, "sim": new_sim})
        self.user_memory.set_sim_preference(args["contact"].name, new_sim)
        return result

    # ----- macros (PRD §19.3: "when I type X, do A and B") -----

    def _define_macro(self, trigger: str, action_text: str) -> str:
        parts = [p.strip() for p in re.split(r"\band\b", action_text, flags=re.IGNORECASE) if p.strip()]
        for part in parts:
            if not isinstance(intent.parse(part), ToolCall):
                return f'I can only macro things I already understand — "{part}" isn\'t on-grammar yet.'
        self.memory.macros[trigger] = parts
        self.user_memory.set_macro(trigger, parts)
        plural = "s" if len(parts) != 1 else ""
        return f'Got it — typing "{trigger}" will now do {len(parts)} thing{plural}.'

    def _run_macro(self, trigger: str) -> str:
        responses = [self.handle(part) or "" for part in self.memory.macros[trigger]]
        self.memory.last_raw = trigger
        return "\n".join(r for r in responses if r)

    # ----- recall / edit last command (PRD §19.3) -----

    def _recall(self) -> str:
        if not self.memory.last_raw:
            return "Nothing to repeat yet."
        return self.handle(self.memory.last_raw) or ""

    def _show_last(self) -> str:
        if not self.memory.last_raw:
            return "Nothing to edit yet."
        return f'Last: "{self.memory.last_raw}" — retype with changes.'

    # ----- pending-slot filling (disambiguation chips, message body) -----

    def _fill_pending(self, raw: str) -> str | None:
        pending = self.memory.pending
        assert pending is not None
        text = raw.strip()

        if pending.missing == "contact":
            choice = self._pick_option(text, pending.options)
            if choice is None:
                self.memory.pending = None
                return None  # not a chip answer — fall through, parse as new command
            pending.args["contact"] = choice
            if pending.tool == "send_message" and "body" not in pending.args:
                pending.missing = "body"
                return "What should it say?"
            self.memory.pending = None
            return self._dispatch(pending.tool, pending.args)

        if pending.missing == "body":
            self.memory.pending = None
            pending.args["body"] = text
            return self._dispatch(pending.tool, pending.args)

        if pending.missing == "biometric":
            domain = SENSITIVE_TOOLS[pending.tool]
            if not self.bridge.biometric.confirm(domain, text):
                return "That didn't match — try again."
            self.memory.pending = None
            return self.bridge.dispatch(pending.tool, pending.args)

        self.memory.pending = None
        return None

    @staticmethod
    def _pick_option(text: str, options: list[Contact]) -> Contact | None:
        if text in ("1", "2") and int(text) <= len(options):
            return options[int(text) - 1]
        low = text.lower()
        named = [c for c in options if low in c.name.lower()]
        return named[0] if len(named) == 1 else None

    @staticmethod
    def _render_clarify(result: Clarify) -> str:
        if result.options:
            chips = "   ".join(
                f"[{i}] {c.name}" for i, c in enumerate(result.options, 1)
            )
            return f"{result.question}\n  {chips}"
        return result.question

    def _simulate(self, spec: str) -> str:
        low = spec.strip().lower()
        if low.startswith("auto"):
            rest = low[len("auto"):].strip()
            if rest == "off":
                self.sim.stop()
            else:
                rest = rest.lstrip("on").strip()
                try:
                    interval = float(rest) if rest else 30.0
                except ValueError:
                    interval = 30.0
                self.sim.start(interval)
            return ""
        if low.startswith("sensor"):
            rest = low[len("sensor"):].strip()
            signal, _, state = rest.rpartition(" ")
            try:
                self.bridge.keyboard.set_sensor(signal, state == "on")
            except ValueError as exc:
                return f"Couldn't simulate that — {exc}."
            return ""
        kind, _, rest = spec.partition(" ")
        source, _, preview = rest.partition(":")
        name = source.strip().title()
        self.queue.push(kind, name, preview.strip())
        if contact := contacts.find(name):
            self.memory.last_contact = contact  # enables "call them back" (PRD §13)
        return ""  # quiet by design — only the indicator changes (PRD §19.1)

    # ----- rendering -----

    def _maybe_auto_digest(self) -> str | None:
        if self.memory.digest_interval is None:
            return None
        if (time.monotonic() - self.memory.last_digest_at) < self.memory.digest_interval:
            return None
        self.memory.last_digest_at = time.monotonic()
        items = self.queue.drain()
        if not items:
            return None  # nothing to surface; reset timer silently
        lines = [f"[auto-digest] {len(items)} waiting:"]
        lines += [f"  {n.source} ({n.kind}): {n.preview}" for n in items]
        return "\n".join(lines)

    def prompt(self) -> str:
        indicator = "" if self.memory.focus_session else self.queue.indicator()
        return f"{indicator} > " if indicator else "> "

    def header(self) -> str:
        strips = self.bridge.strips()
        return "\n".join(f"  {s}" for s in strips)


def run() -> None:
    shell = Shell()
    print("typirOS shell 0.1 — type what you want done. /help for grammar, /quit to exit.")
    while True:
        # auto-expire focus session when its timer runs out
        fs = shell.memory.focus_session
        if fs is not None and time.monotonic() >= fs.end_at:
            if result := shell.bridge.dispatch("end_focus", {}):
                print(result)
        # auto-surface digest when cadence interval has elapsed
        if digest := shell._maybe_auto_digest():
            print(f"\n{digest}")
        if header := shell.header():
            print(header)
        try:
            raw = input(shell.prompt())
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if shell.echo_input:
            print(raw)
        if not raw.strip():
            continue
        response = shell.handle(raw)
        if response is None:
            break
        if response:
            print(response)
    print("typirOS shell closed.")
