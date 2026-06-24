"""Encryption-at-rest for the User and Episodic memory sqlite files (PRD
§15, Phase 4 M18). Python's stdlib has no AES primitive, so this is the
project's first dependency outside the standard library: `cryptography`,
for real AES-256-GCM — not a placeholder cipher.

`sqlite3` can't write directly into ciphertext (that's what SQLCipher does
at the page level, and there's no pure-Python build of it here) — so the
working file lives in a private temp path for the life of the process, and
only the encrypted bytes ever touch the path callers asked for. On open(),
the on-disk file (if any) is decrypted into the temp path; every write
flushes the temp file's bytes back to disk as fresh ciphertext, so a crash
mid-session loses nothing more than a crash would have lost against a
plain sqlite file.
"""

import os
import tempfile
from pathlib import Path

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

_NONCE_LEN = 12


def load_or_create_key(key_path: Path) -> bytes:
    if key_path.exists():
        return key_path.read_bytes()
    key = AESGCM.generate_key(bit_length=256)
    key_path.write_bytes(key)
    os.chmod(key_path, 0o600)
    return key


class EncryptedSqliteFile:
    """Hands out a plaintext temp path for sqlite3 to open, while the
    real on-disk path stays AES-256-GCM ciphertext between flushes."""

    def __init__(self, enc_path: Path, key: bytes) -> None:
        self.enc_path = Path(enc_path)
        self.aesgcm = AESGCM(key)
        fd, tmp_name = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        os.chmod(tmp_name, 0o600)
        self.tmp_path = Path(tmp_name)
        if self.enc_path.exists():
            self.tmp_path.write_bytes(self._decrypt(self.enc_path.read_bytes()))

    def _decrypt(self, blob: bytes) -> bytes:
        nonce, ciphertext = blob[:_NONCE_LEN], blob[_NONCE_LEN:]
        return self.aesgcm.decrypt(nonce, ciphertext, None)

    def _encrypt(self, data: bytes) -> bytes:
        nonce = os.urandom(_NONCE_LEN)
        return nonce + self.aesgcm.encrypt(nonce, data, None)

    def flush(self) -> None:
        self.enc_path.write_bytes(self._encrypt(self.tmp_path.read_bytes()))

    def cleanup(self) -> None:
        self.tmp_path.unlink(missing_ok=True)
