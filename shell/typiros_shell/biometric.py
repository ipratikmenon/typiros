"""Mock Biometric Gate (PRD §15). Real backend: fingerprint/face sensor.

No biometric hardware in this sandbox — a typed passphrase challenge stands
in for a fingerprint/face prompt. One unlock per session per domain: once a
domain (e.g. "finance") is confirmed, further sensitive actions in that
domain dispatch silently for the rest of the session, mirroring how a real
phone only re-prompts biometrics occasionally, not on every tap.
"""

PASSPHRASE = "1234"


class BiometricGate:
    def __init__(self) -> None:
        self.unlocked: set[str] = set()

    def is_unlocked(self, domain: str) -> bool:
        return domain in self.unlocked

    def confirm(self, domain: str, passphrase: str) -> bool:
        if passphrase.strip() != PASSPHRASE:
            return False
        self.unlocked.add(domain)
        return True
