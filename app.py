from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from ml.fraud_detection import FraudDetector
from ml.difficulty_model import DifficultyAdjuster
from typing import List, Dict, Any, Set
import uvicorn

app = FastAPI(title="SmartChain API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For production, use your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

blockchain = Blockchain()
fraud_detector = FraudDetector()
difficulty_adjuster = DifficultyAdjuster()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

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

@app.get("/block/{block_hash}")
async def get_block(block_hash: str) -> Dict[str, Any]:
    """Get block details by hash."""
    block = blockchain.get_block_by_hash(block_hash)
    if not block:
        raise HTTPException(status_code=404, detail="Block not found")
    return block

@app.get("/address/{address}")
async def get_address_info(address: str) -> Dict[str, Any]:
    """Get address details and transaction history."""
    return {
        'balance': blockchain.get_balance(address),
        'transactions': blockchain.get_transaction_history(address)
    }

@app.get("/analytics")
async def get_analytics() -> Dict[str, Any]:
    """Get blockchain analytics."""
    return blockchain.get_analytics()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.broadcast(f"Message: {data}")
    except:
        await manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)