"""M5 TUI shell — Textual-based chat window (PRD §8, §19).

Replaces the line REPL (main.py) without touching intent/bridge/backends.
Run:  python3 -m typiros_shell --tui

Layout (top → bottom):
  status bar  — title + focus label when active
  strips bar  — [focus] [call] [timer] strips; hidden when none
  chat log    — scrollable history of input/response pairs (1fr)
  chips bar   — disambiguation chips; hidden when no pending choice
  input bar   — single-line text input
"""

import time

from textual import on
from textual.app import App, ComposeResult
from textual.containers import Horizontal
from textual.widgets import Input, RichLog, Static

from . import intent
from .intent import ToolCall
from .main import Shell
from .overlays import OVERLAYS


_POLL_INTERVAL = 0.5  # seconds between strip/indicator refreshes


class TypirApp(App[None]):
    """typirOS chat window as a Textual TUI (PRD §8, §19.4)."""

    # Grayscale-first, e-ink-friendly palette (PRD §19.4).
    # Two variants: dark default, easily inverted for light/e-ink screens.
    CSS = """
    Screen {
        background: #111111;
        color: #e0e0e0;
    }

    #status-bar {
        height: 1;
        background: #e0e0e0;
        color: #111111;
        text-style: bold;
        padding: 0 1;
    }

    #strips {
        height: auto;
        padding: 0 1;
        border-bottom: solid #444444;
        color: #bbbbbb;
        display: none;
    }

    RichLog {
        height: 1fr;
        padding: 0 1;
        scrollbar-size: 1 1;
        scrollbar-color: #444444;
    }

    #chips {
        height: auto;
        padding: 0 1;
        border-top: solid #444444;
        color: #aaaaaa;
        display: none;
    }

    #input-row {
        height: 3;
        border-top: solid #444444;
        padding: 0 1;
        align: left middle;
    }

    #indicator {
        width: auto;
        min-width: 2;
        height: 1;
        color: #888888;
        content-align: left middle;
    }

    Input {
        width: 1fr;
        height: 1;
        border: none;
        padding: 0;
        background: transparent;
        color: #e0e0e0;
    }

    Input:focus {
        border: none;
    }
    """

    # ── lifecycle ────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Static("typirOS 0.1", id="status-bar")
        yield Static("", id="strips")
        yield RichLog(id="chat", markup=False, highlight=False, auto_scroll=True)
        yield Static("", id="chips")
        with Horizontal(id="input-row"):
            yield Static("", id="indicator")
            yield Input(placeholder="type what you want done…")

    def on_mount(self) -> None:
        self.shell = Shell()
        self.query_one(Input).focus()
        self._log("typirOS shell — type what you want done. /help for grammar, /quit to exit.")
        self.set_interval(_POLL_INTERVAL, self._poll)

    # ── input handling ───────────────────────────────────────────────────────

    @on(Input.Submitted)
    def _on_submitted(self, event: Input.Submitted) -> None:
        raw = event.value.strip()
        event.input.clear()
        if not raw:
            return

        self._log(f"> {raw}")

        # Peek the parse to detect a full-screen-overlay command (PRD §8,
        # Phase 3 M15) — Shell.handle stays UI-agnostic and just returns
        # text; pushing a Screen is this layer's decision alone.
        peek = intent.parse(raw)

        response = self.shell.handle(raw)
        if response is None:
            self.exit()
            return
        if response:
            self._log_response(response)

        if isinstance(peek, ToolCall) and peek.tool == "show_overlay":
            if screen_cls := OVERLAYS.get(peek.args["kind"]):
                self.push_screen(screen_cls(response))

        self._refresh_chips()
        self._poll()          # immediate strip / indicator refresh

    # ── periodic polling ─────────────────────────────────────────────────────

    def _poll(self) -> None:
        """Refresh strips, indicator; auto-expire focus; auto-digest."""
        fs = self.shell.memory.focus_session
        if fs is not None and time.monotonic() >= fs.end_at:
            result = self.shell.bridge.dispatch("end_focus", {})
            if result:
                self._log_response(result)
            self._refresh_chips()

        if digest := self.shell._maybe_auto_digest():
            self._log_response(digest)

        # strips
        strips = self.shell.bridge.strips()
        strips_w = self.query_one("#strips", Static)
        if strips:
            strips_w.update("\n".join(strips))
            strips_w.display = True
        else:
            strips_w.display = False

        # quiet indicator (suppressed during focus — PRD §19.2)
        ind_w = self.query_one("#indicator", Static)
        if self.shell.memory.focus_session:
            ind_w.update("")
        else:
            ind = self.shell.queue.indicator()
            ind_w.update(f"{ind} " if ind else "")

        # status bar shows focus label when active
        fs = self.shell.memory.focus_session
        label = f"typirOS 0.1  ·  focus: {fs.label}" if fs else "typirOS 0.1"
        self.query_one("#status-bar", Static).update(label)

    # ── rendering helpers ────────────────────────────────────────────────────

    def _log(self, text: str) -> None:
        self.query_one("#chat", RichLog).write(text)

    def _log_response(self, text: str) -> None:
        chat = self.query_one("#chat", RichLog)
        for line in text.splitlines():
            chat.write(f"  {line}")

    def _refresh_chips(self) -> None:
        chips_w = self.query_one("#chips", Static)
        pending = self.shell.memory.pending
        if pending and pending.options:
            chips = "   ".join(
                f"[{i}] {c.name}" for i, c in enumerate(pending.options, 1)
            )
            chips_w.update(chips)
            chips_w.display = True
        else:
            chips_w.update("")
            chips_w.display = False


def run_tui() -> None:
    TypirApp().run()
