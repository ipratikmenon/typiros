"""User memory layer (PRD §13) — permanent, on-device store for contact
SIM preferences, the app allowlist (PRD §19.9), and user-defined macros.
Session memory (`memory.py`) is RAM-only and resets every run; this layer
survives process restarts.

PRD §13 specifies an *encrypted* local DB. The on-disk file is AES-256-GCM
ciphertext (`crypto_store.py`, Phase 4 M18) for any non-`:memory:` path;
scripted/piped runs keep using a plain in-memory sqlite db, same as before.
"""

import sqlite3
from pathlib import Path

from .crypto_store import EncryptedSqliteFile, load_or_create_key

DEFAULT_DB_PATH = Path(__file__).resolve().parent / "user_memory.db"
DEFAULT_KEY_PATH = Path(__file__).resolve().parent / "user_memory.key"

SCHEMA = """
CREATE TABLE IF NOT EXISTS sim_preference (
    contact TEXT PRIMARY KEY,
    sim TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS enabled_apps (
    app TEXT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS macros (
    trigger TEXT PRIMARY KEY,
    actions TEXT NOT NULL
);
"""

_ACTION_SEP = "\x1f"


class UserMemory:
    def __init__(
        self,
        db_path: Path | str = DEFAULT_DB_PATH,
        key_path: Path | str = DEFAULT_KEY_PATH,
    ) -> None:
        self._enc = None
        if str(db_path) == ":memory:":
            self.conn = sqlite3.connect(db_path)
        else:
            key = load_or_create_key(Path(key_path))
            self._enc = EncryptedSqliteFile(Path(db_path), key)
            self.conn = sqlite3.connect(self._enc.tmp_path)
        self.conn.executescript(SCHEMA)
        self.conn.commit()
        self._persist()

    def _persist(self) -> None:
        if self._enc is not None:
            self._enc.flush()

    # ----- SIM preference (PRD §11: "no, secondary" — the OS remembers) -----

    def get_sim_preference(self, contact: str) -> str | None:
        row = self.conn.execute(
            "SELECT sim FROM sim_preference WHERE contact = ?", (contact,)
        ).fetchone()
        return row[0] if row else None

    def set_sim_preference(self, contact: str, sim: str) -> None:
        self.conn.execute(
            "INSERT INTO sim_preference (contact, sim) VALUES (?, ?) "
            "ON CONFLICT(contact) DO UPDATE SET sim = excluded.sim",
            (contact, sim),
        )
        self.conn.commit()
        self._persist()

    # ----- app allowlist (PRD §19.9) -----

    def enabled_apps(self) -> set[str]:
        rows = self.conn.execute("SELECT app FROM enabled_apps").fetchall()
        return {r[0] for r in rows}

    def enable_app(self, app: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO enabled_apps (app) VALUES (?)", (app,))
        self.conn.commit()
        self._persist()

    # ----- macros (PRD §19.3) -----

    def macros(self) -> dict[str, list[str]]:
        rows = self.conn.execute("SELECT trigger, actions FROM macros").fetchall()
        return {trigger: actions.split(_ACTION_SEP) for trigger, actions in rows}

    def set_macro(self, trigger: str, actions: list[str]) -> None:
        self.conn.execute(
            "INSERT INTO macros (trigger, actions) VALUES (?, ?) "
            "ON CONFLICT(trigger) DO UPDATE SET actions = excluded.actions",
            (trigger, _ACTION_SEP.join(actions)),
        )
        self.conn.commit()
        self._persist()

    def close(self) -> None:
        self.conn.close()
        if self._enc is not None:
            self._enc.cleanup()
