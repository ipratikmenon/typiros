"""Quiet notification queue (PRD §19.1) — pull, not push.

Inbound events queue silently. The only surface is a status indicator;
the user pulls with "what did I miss" or /missed.
"""

from dataclasses import dataclass


@dataclass
class Notification:
    kind: str      # "sms", "call", ...
    source: str
    preview: str


class QuietQueue:
    def __init__(self) -> None:
        self._items: list[Notification] = []

    def push(self, kind: str, source: str, preview: str) -> None:
        self._items.append(Notification(kind, source, preview))

    def size(self) -> int:
        return len(self._items)

    def drain_from(self, idx: int) -> list[Notification]:
        """Remove and return items from index idx onward; earlier items stay."""
        held, self._items = self._items[idx:], self._items[:idx]
        return held

    def indicator(self) -> str:
        return f"•{len(self._items)}" if self._items else ""

    def drain(self) -> list[Notification]:
        items, self._items = self._items, []
        return items

    def digest(self) -> str:
        items = self.drain()
        if not items:
            return "Nothing waiting — all clear."
        lines = [f"While you were focused — {len(items)} waiting:"]
        lines += [f"  {n.source} ({n.kind}): {n.preview}" for n in items]
        return "\n".join(lines)
