from fastapi import FastAPI, HTTPException
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ml.fraud_detection import FraudDetector
from ml.difficulty_model import DifficultyAdjuster
from typing import List, Dict, Any
import uvicorn

app = FastAPI(title="SmartChain API")
blockchain = Blockchain()
fraud_detector = FraudDetector()
difficulty_adjuster = DifficultyAdjuster()

@app.post("/add_transaction")
async def add_transaction(sender: str, receiver: str, amount: float) -> Dict[str, Any]:
    """Add a new transaction to the pending list."""
    transaction = Transaction(sender, receiver, amount)
    if blockchain.add_transaction(transaction):
        return {"message": "Transaction added successfully"}
    raise HTTPException(status_code=400, message="Invalid transaction")

@app.post("/mine_block")
async def mine_block() -> Dict[str, Any]:
    """Mine a new block with pending transactions."""
    if not blockchain.pending_transactions:
        raise HTTPException(status_code=400, detail="No pending transactions")
    
    block = blockchain.add_block(blockchain.pending_transactions)
    blockchain.pending_transactions = []
    
    return block.to_dict()

@app.get("/get_chain")
async def get_chain() -> Dict[str, Any]:
    """Get the full blockchain."""
    return {
        "chain": blockchain.get_chain_data(),
        "length": len(blockchain.chain)
    }

@app.post("/detect_fraud")
async def detect_fraud(transactions: List[Dict[str, Any]]) -> Dict[str, List[bool]]:
    """Detect potentially fraudulent transactions."""
    results = fraud_detector.detect_anomalies(transactions)
    return {"fraud_flags": results}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)