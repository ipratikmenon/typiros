"""Full-screen overlays (PRD §8 "Full-Screen Overlays", §9) — TUI only.

Some responses spawn a full-screen overlay that collapses back to chat.
This prototype has no photo gallery, map renderer, or video player, so
each overlay is a placeholder screen showing the same text the line REPL
would print inline. The single dismiss gesture (PRD §8: "swipe down or
back tap") is Esc in this terminal — the chat (and anything running, like
an active call or timer — strips keep ticking via the app's own poll
loop) is never interrupted by the overlay.
"""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.widgets import Static


class OverlayScreen(Screen):
    title_text = "Overlay"

    BINDINGS = [Binding("escape", "dismiss_overlay", "Back to chat")]

    CSS = """
    OverlayScreen {
        background: #111111;
        color: #e0e0e0;
        align: center middle;
    }
    #overlay-body {
        border: solid #444444;
        padding: 2 4;
    }
    #overlay-hint {
        dock: bottom;
        height: 1;
        color: #888888;
        content-align: center middle;
    }
    """

    def __init__(self, body: str) -> None:
        super().__init__()
        self.body = body

    def compose(self) -> ComposeResult:
        yield Static(f"{self.title_text}\n\n{self.body}", id="overlay-body")
        yield Static("Esc — back to chat", id="overlay-hint")

    def action_dismiss_overlay(self) -> None:
        self.app.pop_screen()


class MediaOverlay(OverlayScreen):
    title_text = "Media"


class MapsOverlay(OverlayScreen):
    title_text = "Maps"


class PhotosOverlay(OverlayScreen):
    title_text = "Photos"


OVERLAYS = {"media": MediaOverlay, "maps": MapsOverlay, "photos": PhotosOverlay}
