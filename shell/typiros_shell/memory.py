"""Session memory layer (PRD §13). RAM-only, lives until shell exit."""

from dataclasses import dataclass, field

from .contacts import Contact


@dataclass
class Pending:
    """A half-built tool call waiting for one piece of user input."""

    tool: str
    args: dict
    missing: str            # "contact" or "body"
    options: list[Contact] = field(default_factory=list)


@dataclass
class SessionMemory:
    last_contact: Contact | None = None
    last_sim: str = "Primary"
    last_dispatch: tuple[str, dict] | None = None
    last_raw: str | None = None
    macros: dict[str, list[str]] = field(default_factory=dict)
    pending: Pending | None = None
