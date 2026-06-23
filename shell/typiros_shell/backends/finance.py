"""Mock Finance agent (PRD §16 Phase 3 M13). Real backend: banking/payments API.

Gated by the Biometric Gate (biometric.py) ahead of dispatch — the Bridge
Layer checks the gate before any Finance tool call reaches this backend.
"""

from ..contacts import Contact


class Finance:
    def __init__(self) -> None:
        self._balance = 1240.50

    def balance(self) -> str:
        return f"Balance: ${self._balance:,.2f}."

    def send_payment(self, contact: Contact, amount: float) -> str:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self._balance:
            raise ValueError("insufficient balance")
        self._balance -= amount
        return f"Sent ${amount:,.2f} to {contact.name}."
