from typing import List, Dict, Any, Optional
from .block import Block
from .transaction import Transaction
import time
# --- MongoDB helpers import ---
from db import helpers as db_helpers

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Transaction] = []
        self.difficulty = 4
        self.mining_reward = 10.0
        self.create_genesis_block()

    def create_genesis_block(self) -> None:
        """Create the first block in the chain."""
        genesis_block = Block(0, [], "0")
        genesis_block.mine_block(self.difficulty)
        self.chain.append(genesis_block)
        # Store genesis block in MongoDB
        db_helpers.blocks.insert_one(genesis_block.to_dict())

    def get_latest_block(self) -> Block:
        """Return the most recent block."""
        return self.chain[-1]

    def add_block(self, transactions: List[Transaction]) -> Block:
        """Create and add a new block to the chain."""
        block = Block(
            len(self.chain),
            [t.to_dict() for t in transactions],
            self.get_latest_block().hash
        )
        block.mine_block(self.difficulty)
        self.chain.append(block)
        # Store block in MongoDB
        db_helpers.blocks.insert_one(block.to_dict())
        return block

    def add_transaction(self, transaction: Transaction) -> bool:
        """Add a new transaction to pending transactions and MongoDB."""
        if transaction.validate():
            self.pending_transactions.append(transaction)
            # Store transaction in MongoDB
            db_helpers.add_transaction(transaction.sender, transaction.receiver, transaction.amount, {"timestamp": transaction.timestamp})
            return True
        return False

    def mine_pending_transactions(self, miner_address: str) -> Block:
        """
        Mine pending transactions and add reward transaction.
        Update balances in MongoDB.
        """
        # Add mining reward transaction
        reward_transaction = Transaction(
            sender="Network",
            receiver=miner_address,
            amount=self.mining_reward
        )
        self.pending_transactions.append(reward_transaction)
        # Store reward transaction in MongoDB
        db_helpers.add_transaction(reward_transaction.sender, reward_transaction.receiver, reward_transaction.amount, {"timestamp": reward_transaction.timestamp})

        # Create new block
        block = self.add_block(self.pending_transactions)
        # Update balances for all transactions in the block
        for tx in self.pending_transactions:
            # Update sender balance
            if tx.sender != "Network":
                sender_balance = db_helpers.get_balance(tx.sender) or 0.0
                db_helpers.update_balance(tx.sender, sender_balance - tx.amount)
            # Update receiver balance
            receiver_balance = db_helpers.get_balance(tx.receiver) or 0.0
            db_helpers.update_balance(tx.receiver, receiver_balance + tx.amount)
        self.pending_transactions = []
        return block

    def get_balance(self, address: str) -> float:
        """Get balance from MongoDB balances collection."""
        balance = db_helpers.get_balance(address)
        if balance is not None:
            return balance
        # Fallback to in-memory calculation if not found
        balance = 0.0
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] == address:
                    balance -= tx['amount']
                if tx['receiver'] == address:
                    balance += tx['amount']
        return balance

    def is_chain_valid(self) -> bool:
        """Validate the entire blockchain."""
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i-1]

            # Verify current block's hash
            if current.hash != current.calculate_hash():
                return False

            # Verify chain linkage
            if current.previous_hash != previous.hash:
                return False

        return True

    def get_chain_data(self) -> List[Dict[str, Any]]:
        """Return the chain data in dictionary format."""
        return [block.to_dict() for block in self.chain]

    def adjust_difficulty(self) -> None:
        """
        Adjust mining difficulty based on the average time 
        between the last few blocks.
        """
        if len(self.chain) < 10:
            return

        # Calculate average block time for last 10 blocks
        last_block_times = [
            self.chain[i+1].timestamp - self.chain[i].timestamp 
            for i in range(-10, -1)
        ]
        avg_block_time = sum(last_block_times) / len(last_block_times)

        # Target block time is 10 seconds
        if avg_block_time < 8:  # Too fast
            self.difficulty += 1
        elif avg_block_time > 12:  # Too slow
            self.difficulty = max(1, self.difficulty - 1)

    def get_block_by_hash(self, block_hash: str) -> Optional[Dict]:
        """Search for a block by its hash."""
        for block in self.chain:
            if block.hash == block_hash:
                return block.to_dict()
        return None

    def get_transaction_history(self, address: str) -> List[Dict]:
        """Get all transactions for an address."""
        transactions = []
        for block in self.chain:
            for tx in block.transactions:
                if tx['sender'] == address or tx['receiver'] == address:
                    transactions.append({
                        'block_hash': block.hash,
                        'timestamp': block.timestamp,
                        **tx
                    })
        return transactions

    def get_analytics(self) -> Dict:
        """Get chain analytics."""
        return {
            'total_blocks': len(self.chain),
            'average_block_time': self._calculate_avg_block_time(),
            'current_difficulty': self.difficulty,
            'total_transactions': sum(len(block.transactions) for block in self.chain)
        }