"""Contact store and entity resolution (PRD §11).

One match: act immediately. Two or more: surface max-2 chips.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Contact:
    name: str
    number: str


# Mock contact database. Real backend: system contacts provider (Phase 1 M4).
CONTACTS = [
    Contact("Philip Sharma", "+91-98100-11223"),
    Contact("Philip D'Souza", "+91-98200-44556"),
    Contact("Lena Fischer", "+49-151-7788990"),
    Contact("Mom", "+91-98300-77889"),
]


def resolve(words: list[str]) -> tuple[list[Contact], list[str]]:
    """Match a contact from the leading words; longest name span wins.

    Returns (matches, remaining_words). An unambiguous 2-word match beats
    an ambiguous 1-word match so "philip sharma hey" splits correctly.
    """
    for span in (2, 1):
        if len(words) < span:
            continue
        candidate = " ".join(words[:span]).lower().rstrip(",:")
        matches = [c for c in CONTACTS if _matches(c, candidate)]
        if len(matches) == 1:
            return matches, words[span:]
        if matches and span == 1:
            return matches[:2], words[span:]  # max 2 chips, PRD §11
    return [], words


def find(name: str) -> Contact | None:
    """Look up a contact by full name or first name (for inbound events)."""
    low = name.lower()
    for c in CONTACTS:
        full = c.name.lower()
        if full == low or full.split()[0] == low:
            return c
    return None


def _matches(contact: Contact, candidate: str) -> bool:
    full = contact.name.lower()
    if full.startswith(candidate):
        return True
    name_parts = full.split()
    cand_parts = candidate.split()
    return len(cand_parts) <= len(name_parts) and all(
        part.startswith(cand) for cand, part in zip(cand_parts, name_parts)
    )
