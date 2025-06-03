import hashlib
import time
from typing import List, Dict, Any

class Block:
    def __init__(self, index: int, transactions: List[Dict], previous_hash: str, nonce: int = 0):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self) -> str:
        """Calculate block hash using SHA-256."""
        block_string = (
            f"{self.index}{self.timestamp}{self.transactions}"
            f"{self.previous_hash}{self.nonce}"
        )
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty: int) -> None:
        """Mine block with proof of work."""
        while self.hash[:difficulty] != "0" * difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

    def to_dict(self) -> Dict[str, Any]:
        """Convert block to dictionary format."""
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "hash": self.hash
        }