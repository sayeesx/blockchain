from fastapi import FastAPI, HTTPException, WebSocket, Body
from fastapi.middleware.cors import CORSMiddleware
from blockchain.chain import Blockchain
from blockchain.transaction import Transaction
from blockchain.token import miznet_token
from blockchain.marketplace import Marketplace
from ml.fraud_detection import FraudDetector
from ml.difficulty_model import DifficultyAdjuster
from db.helpers import transfer_token, get_token, get_balance as get_token_balance, create_token, log_fraud_alert
from typing import List, Dict, Any, Set
from pydantic import BaseModel, Field
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
marketplace = Marketplace()

# --- Pydantic Models for Validation ---
class TokenTransferRequest(BaseModel):
    sender: str = Field(..., example="alice")
    receiver: str = Field(..., example="bob")
    amount: float = Field(..., gt=0, example=100)

class TokenBalanceResponse(BaseModel):
    address: str
    balance: float

class MarketplaceListRequest(BaseModel):
    seller: str = Field(..., example="alice")
    amount: float = Field(..., gt=0, example=50)
    price_per_token: float = Field(..., gt=0, example=2.5)

class MarketplaceBuyRequest(BaseModel):
    buyer: str = Field(..., example="bob")
    listing_id: str = Field(...)
    amount: float = Field(..., gt=0, example=10)

# --- Token Endpoints ---
@app.post("/token/transfer")
async def token_transfer(req: TokenTransferRequest):
    """Transfer Miznet tokens between users, with fraud detection."""
    # Fraud detection (example: flag large transfers)
    if req.amount > 10000:
        log_fraud_alert(tx_id="N/A", reason="Large token transfer", score=1.0)
        raise HTTPException(status_code=403, detail="Transfer flagged as potentially fraudulent.")
    # Perform transfer
    if not transfer_token("MIZ", req.sender, req.receiver, req.amount):
        raise HTTPException(status_code=400, detail="Insufficient balance or invalid transfer.")
    return {"message": "Transfer successful"}

@app.get("/token/balance/{address}", response_model=TokenBalanceResponse)
async def token_balance(address: str):
    """Get Miznet token balance for an address."""
    token = get_token("MIZ")
    if not token:
        raise HTTPException(status_code=404, detail="Miznet token not found.")
    balance = token.get("balances", {}).get(address, 0.0)
    return {"address": address, "balance": balance}

# --- Marketplace Endpoints ---
@app.post("/marketplace/list")
async def marketplace_list(req: MarketplaceListRequest):
    """List Miznet tokens for sale."""
    # Check seller balance
    token = get_token("MIZ")
    if not token or token.get("balances", {}).get(req.seller, 0.0) < req.amount:
        raise HTTPException(status_code=400, detail="Insufficient token balance to list.")
    listing_id = marketplace.list_token_for_sale(req.seller, "MIZ", req.amount, req.price_per_token)
    return {"message": "Listing created", "listing_id": listing_id}

@app.post("/marketplace/buy")
async def marketplace_buy(req: MarketplaceBuyRequest):
    """Buy Miznet tokens from a listing, with fraud detection."""
    # Fraud detection (example: flag rapid or large purchases)
    if req.amount > 10000:
        log_fraud_alert(tx_id=req.listing_id, reason="Large marketplace purchase", score=1.0)
        raise HTTPException(status_code=403, detail="Purchase flagged as potentially fraudulent.")
    success = marketplace.buy_token(req.buyer, req.listing_id, req.amount)
    if not success:
        raise HTTPException(status_code=400, detail="Purchase failed. Check listing and balance.")
    return {"message": "Purchase successful"}

@app.get("/marketplace/listings")
async def marketplace_listings():
    """Get all open Miznet token listings."""
    listings = marketplace.get_listings("MIZ")
    return {"listings": listings}

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

@app.get("/")
def read_root():
    return {"message": "SmartChain API is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)