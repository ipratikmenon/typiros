"""Tier 2 stub (PRD §18) — off-grammar input escalates here instead of
failing in language (PRD §19.7's "everything else waits" applies to
notifications, not to language the user typed and got no parse for).

Routing reads the real agents/*.yaml manifests that will back live
`ant beta:agents`/`ant beta:sessions` calls (PRD §18), picking the
best-matching System Agent by keyword overlap with its "You handle ..."
line. No subprocess, no API call, no credentials required — every response
is a canned echo tagged `[tier2-stub]` so the two-model routing shape is
provable in a sandbox that can't reach the real Tier 2 backend yet.
"""

import re
from dataclasses import dataclass
from pathlib import Path

AGENTS_DIR = Path(__file__).resolve().parents[2] / "agents"

NAME_RE = re.compile(r"^name:\s*(\S+)", re.MULTILINE)
HANDLES_RE = re.compile(r"You (?:handle|dispatch)\s+(.+?)\.", re.IGNORECASE)
STOPWORDS = {"the", "and", "all", "to", "for"}

DEFAULT_AGENT = "typiros-information"


@dataclass
class AgentManifest:
    name: str
    keywords: set[str]


def _load_manifests() -> list[AgentManifest]:
    manifests = []
    if not AGENTS_DIR.is_dir():
        return manifests
    for path in sorted(AGENTS_DIR.glob("*.yaml")):
        text = path.read_text()
        name_m = NAME_RE.search(text)
        if not name_m:
            continue
        keywords: set[str] = set()
        if handles_m := HANDLES_RE.search(text):
            for word in re.split(r"[,\s]+", handles_m.group(1).lower()):
                word = word.strip(".")
                if word and word not in STOPWORDS:
                    keywords.add(word)
        manifests.append(AgentManifest(name_m.group(1), keywords))
    return manifests


def route(text: str) -> str:
    """Pick the best-matching agent manifest by keyword overlap and return
    a stub response — the same shape a real ant session result would take
    once the Bridge Layer parses it back into one line."""
    words = set(re.findall(r"[a-z']+", text.lower()))
    best_agent, best_score = DEFAULT_AGENT, 0
    for manifest in _load_manifests():
        score = len(words & manifest.keywords)
        if score > best_score:
            best_agent, best_score = manifest.name, score
    return f'[tier2-stub] {best_agent} would handle: "{text.strip()}"'
