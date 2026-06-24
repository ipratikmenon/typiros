"""Episodic memory layer (PRD §13) — a rolling, summarised log of past
interactions ("relationship context"), distinct from the permanent User
memory layer (`user_memory.py`, contact prefs/macros/allowlist) and the
RAM-only Session memory (`memory.py`).

PRD §13 specifies an *encrypted* local DB with a 90-day rolling window.
The prototype uses a plain stdlib `sqlite3` file (encryption is a Phase 4
hardening concern, not modeled here) and prunes rows older than 90 days
on every write so the table never grows unbounded.

Scope decision: only contact-tied actions are logged — calls, messages,
payments — since "relationship context" is the PRD's framing for this
layer. Pure lookups (balance, weather, show_missed, overlay views) don't
add relationship context and are left out, same way `last_dispatch`
(session memory, for "no, primary" corrections) only tracks the same
narrow set of actions.
"""

import sqlite3
import time
from pathlib import Path

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "episodic_memory.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS episodes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts REAL NOT NULL,
    contact TEXT NOT NULL,
    summary TEXT NOT NULL
);
"""

ROLLING_WINDOW_SECS = 90 * 86400


class EpisodicMemory:
    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH) -> None:
        self.conn = sqlite3.connect(db_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def log(self, contact: str, summary: str) -> None:
        now = time.time()
        self.conn.execute(
            "INSERT INTO episodes (ts, contact, summary) VALUES (?, ?, ?)",
            (now, contact, summary),
        )
        self.conn.execute(
            "DELETE FROM episodes WHERE ts < ?", (now - ROLLING_WINDOW_SECS,)
        )
        self.conn.commit()

    def recent(self, contact: str | None = None, limit: int = 5) -> list[tuple[float, str, str]]:
        if contact is None:
            rows = self.conn.execute(
                "SELECT ts, contact, summary FROM episodes ORDER BY ts DESC LIMIT ?",
                (limit,),
            ).fetchall()
        else:
            rows = self.conn.execute(
                "SELECT ts, contact, summary FROM episodes WHERE contact = ? "
                "ORDER BY ts DESC LIMIT ?",
                (contact, limit),
            ).fetchall()
        return rows

    def close(self) -> None:
        self.conn.close()
