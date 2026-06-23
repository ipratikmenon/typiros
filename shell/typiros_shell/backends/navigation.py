"""Mock Navigation agent (PRD §16 Phase 3). Real backend: maps API or container app."""

import random


class Navigation:
    def __init__(self) -> None:
        self.destination: str | None = None
        self.eta_minutes: int | None = None

    def navigate(self, destination: str) -> str:
        self.destination = destination
        self.eta_minutes = random.randint(5, 45)
        return f"Navigating to {destination} — ETA {self.eta_minutes} min."

    def eta(self) -> str:
        if self.destination is None:
            raise RuntimeError("not navigating anywhere")
        return f"ETA {self.eta_minutes} min to {self.destination}."

    def current_route(self) -> str:
        if self.destination is None:
            return "Not navigating anywhere."
        return f"Navigating to {self.destination} — ETA {self.eta_minutes} min."

    def stop(self) -> str:
        if self.destination is None:
            raise RuntimeError("not navigating anywhere")
        destination = self.destination
        self.destination = None
        self.eta_minutes = None
        return f"Stopped navigating to {destination}."

    def strip(self) -> str | None:
        if self.destination is None:
            return None
        return f"[nav] {self.destination} · ETA {self.eta_minutes} min"
