import time
from typing import Optional, Dict, Any

class Transaction:
    def __init__(self, sender: str, receiver: str, amount: float, 
                 timestamp: Optional[float] = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.timestamp = timestamp or time.time()

    def validate(self) -> bool:
        """
        Validate transaction basics.
        Additional validation logic can be added here.
        """
        if not all([self.sender, self.receiver, self.amount]):
            return False
        if self.amount <= 0:
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert transaction to dictionary format."""
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }