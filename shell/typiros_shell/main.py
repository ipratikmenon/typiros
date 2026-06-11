"""The chat window — the entire UI (PRD §8), rendered as a line REPL.

Grayscale, text-only, no chrome (PRD §19.4). Strips render as a header
line; the quiet-queue indicator sits in the prompt. M5 swaps this layer
for a TUI without touching intent/bridge/backends.
"""

import sys

from . import intent
from .bridge import Bridge
from .contacts import Contact
from .intent import Clarify, Quit, Say, ToolCall
from .memory import Pending, SessionMemory
from .notifications import QuietQueue


class Shell:
    def __init__(self) -> None:
        self.memory = SessionMemory()
        self.queue = QuietQueue()
        self.bridge = Bridge(self.memory, self.queue)
        self.echo_input = not sys.stdin.isatty()

    # ----- one turn of the single loop (PRD §3) -----

    def handle(self, raw: str) -> str | None:
        """Returns response text, or None to quit."""
        if raw.startswith("/sim "):           # dev-only: simulate inbound event
            return self._simulate(raw[5:])

        if self.memory.pending:
            resolved = self._fill_pending(raw)
            if resolved is not None:
                return resolved

        result = intent.parse(raw)
        if isinstance(result, Quit):
            return None
        if isinstance(result, Say):
            return result.text
        if isinstance(result, Clarify):
            self.memory.pending = result.pending
            return self._render_clarify(result)
        if isinstance(result, ToolCall):
            return self.bridge.dispatch(result.tool, result.args)
        return ""

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
            return self.bridge.dispatch(pending.tool, pending.args)

        if pending.missing == "body":
            self.memory.pending = None
            pending.args["body"] = text
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
        kind, _, rest = spec.partition(" ")
        source, _, preview = rest.partition(":")
        self.queue.push(kind, source.strip().title(), preview.strip())
        return ""  # quiet by design — only the indicator changes (PRD §19.1)

    # ----- rendering -----

    def prompt(self) -> str:
        indicator = self.queue.indicator()
        return f"{indicator} > " if indicator else "> "

    def header(self) -> str:
        strips = self.bridge.strips()
        return "\n".join(f"  {s}" for s in strips)


def run() -> None:
    shell = Shell()
    print("typirOS shell 0.1 — type what you want done. /help for grammar, /quit to exit.")
    while True:
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
