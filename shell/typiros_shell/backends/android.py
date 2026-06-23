"""Mock Android compatibility container (PRD §7 Strategy A, §19.9).

Apps run inside the container with their UI suppressed — the Bridge Layer
dispatches into them the same way it dispatches into native backends. Real
backend (Phase 2+): Waydroid/Anbox bridge with the same method signatures.

Detected is not the same as dispatchable: only apps on the allowlist route
silently. Anything else installed in the container is inert from the chat's
perspective until a deliberate `enable app <name>` (PRD §19.9).
"""

from ..contacts import Contact

INSTALLED_APPS = {"whatsapp", "instagram"}
DEFAULT_ALLOWLIST = {"whatsapp"}
DISPLAY_NAMES = {"whatsapp": "WhatsApp", "instagram": "Instagram"}


class AndroidContainer:
    def __init__(self) -> None:
        self.installed = set(INSTALLED_APPS)
        self.allowlist = set(DEFAULT_ALLOWLIST)
        self.sent_messages: list[dict] = []

    def is_installed(self, app: str) -> bool:
        return app.lower() in self.installed

    def is_allowed(self, app: str) -> bool:
        return app.lower() in self.allowlist

    def enable(self, app: str) -> str:
        app = app.lower()
        if not self.is_installed(app):
            raise RuntimeError(f"{app} isn't installed")
        if self.is_allowed(app):
            return f"{app} is already enabled."
        self.allowlist.add(app)
        return f"Enabled: {app}. It will route silently from now on."

    def send(self, app: str, contact: Contact, body: str) -> str:
        self.sent_messages.append({"app": app, "to": contact, "body": body})
        label = DISPLAY_NAMES.get(app, app.title())
        return f"Sent to {contact.name} — {label}."
