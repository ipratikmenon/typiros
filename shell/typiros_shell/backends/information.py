"""Mock Information agent (PRD §16 Phase 3 M11). Real backend: weather/search API.

A small canned subset graduates here out of the Tier 2 stub (PRD §18) — the
exact "off-grammar input becomes a real grammar match once it's common
enough" lifecycle the Tier 2 stub exists to surface. Anything outside this
subset still escalates to tier2.py unchanged.
"""

import datetime

CANNED_WEATHER = {
    "paris": "Sunny, 22°C",
    "london": "Cloudy, 16°C",
    "new york": "Rainy, 18°C",
    "tokyo": "Clear, 25°C",
}

CANNED_FACTS = {
    "capital of france": "Paris.",
    "capital of japan": "Tokyo.",
    "capital of italy": "Rome.",
    "largest planet": "Jupiter.",
}


class Information:
    def weather(self, city: str) -> str:
        canned = CANNED_WEATHER.get(city.lower())
        if canned:
            return f"{canned} in {city.title()}."
        return f"Mild, 20°C in {city.title()} (mock data)."

    def fact(self, query: str) -> str:
        answer = CANNED_FACTS.get(query.lower().strip())
        if answer is None:
            raise ValueError(f"no canned answer for {query!r} yet")
        return answer

    def time(self) -> str:
        return f"It's {datetime.datetime.now():%-I:%M %p}."
