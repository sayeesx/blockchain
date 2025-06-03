from blockchain.transaction import Transaction
from blockchain.chain import Blockchain

def test_blockchain():
    # Initialize blockchain
    chain = Blockchain()
    
    # Create some test transactions
    tx1 = Transaction("Alice", "Bob", 50.0)
    tx2 = Transaction("Bob", "Charlie", 30.0)
    tx3 = Transaction("Charlie", "Alice", 20.0)
    
    # Add transactions
    print("Adding transactions...")
    chain.add_transaction(tx1)
    chain.add_transaction(tx2)
    chain.add_transaction(tx3)
    
    # Mine a block
    print("\nMining block...")
    block = chain.add_block(chain.pending_transactions)
    
    # Print block info
    print("\nBlock mined!")
    print(f"Block hash: {block.hash}")
    print(f"Previous hash: {block.previous_hash}")
    print(f"Nonce: {block.nonce}")
    
    # Verify chain
    print(f"\nChain valid: {chain.is_chain_valid()}")
    print(f"Chain length: {len(chain.chain)}")

if __name__ == "__main__":
    test_blockchain()