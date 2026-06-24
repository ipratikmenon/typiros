"""Encryption-at-rest for the User and Episodic memory sqlite files (PRD
§15, Phase 4 M18). Python's stdlib has no AES primitive, so this is the
project's first dependency outside the standard library: `cryptography`,
for real AES-256-GCM — not a placeholder cipher.

`sqlite3` can't write directly into ciphertext (that's what SQLCipher does
at the page level, and there's no pure-Python build of it here), but its
stdlib `Connection.serialize()`/`deserialize()` (3.11+) move a whole
database to/from an in-memory bytes object — so the working connection is
opened against `:memory:` and plaintext never touches disk at all. On
open(), the on-disk ciphertext (if any) is decrypted straight into the
in-memory connection. Every write serializes the in-memory connection and
re-encrypts it back to disk. A first pass of this (M16 security-audit
review) decrypted into a private temp *file* instead — fixed here because
an unclean kill (SIGKILL, OOM) would have left that temp file's plaintext
sitting on disk indefinitely.
"""

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_LEN = 12


def load_or_create_key(key_path) -> bytes:
    if key_path.exists():
        return key_path.read_bytes()
    key = AESGCM.generate_key(bit_length=256)
    key_path.write_bytes(key)
    os.chmod(key_path, 0o600)
    return key


class EncryptedSqliteDB:
    """Owns an in-memory sqlite3 connection whose bytes are AES-256-GCM
    ciphertext at `enc_path` between flushes. Plaintext lives only in
    process memory, never on disk."""

    def __init__(self, enc_path, key: bytes) -> None:
        import sqlite3

        self.enc_path = enc_path
        self.aesgcm = AESGCM(key)
        self.conn = sqlite3.connect(":memory:")
        if self.enc_path.exists():
            self.conn.deserialize(self._decrypt(self.enc_path.read_bytes()))

    def _decrypt(self, blob: bytes) -> bytes:
        nonce, ciphertext = blob[:_NONCE_LEN], blob[_NONCE_LEN:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def _encrypt(self, data: bytes) -> bytes:
        nonce = os.urandom(_NONCE_LEN)
        return nonce + self.aesgcm.encrypt(nonce, data, None)

    def flush(self) -> None:
        self.enc_path.write_bytes(self._encrypt(self.conn.serialize()))
