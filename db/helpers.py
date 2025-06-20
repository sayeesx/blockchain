from typing import Optional, List, Dict, Any
from bson.objectid import ObjectId
from db.db import blocks, transactions, balances, fraud_alerts
from db.db import _db

tokens = _db['tokens']

# --- Transaction Helpers ---
def add_transaction(sender: str, receiver: str, amount: float, metadata: Optional[Dict[str, Any]] = None) -> str:
    """
    Add a new transaction to the transactions collection.
    Returns the inserted transaction's ID.
    """
    tx = {
        "sender": sender,
        "receiver": receiver,
        "amount": amount,
        "metadata": metadata or {},
    }
    result = transactions.insert_one(tx)
    return str(result.inserted_id)

def get_transactions_by_wallet(wallet_address: str) -> List[Dict[str, Any]]:
    """
    Get all transactions where the wallet is sender or receiver.
    """
    cursor = transactions.find({
        "$or": [
            {"sender": wallet_address},
            {"receiver": wallet_address}
        ]
    })
    return list(cursor)

# --- Block Helpers ---
def get_latest_block() -> Optional[Dict[str, Any]]:
    """
    Get the most recently mined block (by highest index or timestamp).
    """
    return blocks.find_one(sort=[("index", -1)])

# --- Balance Helpers ---
def update_balance(wallet_address: str, amount: float) -> None:
    """
    Update (set) the balance for a wallet address.
    """
    balances.update_one(
        {"wallet_address": wallet_address},
        {"$set": {"balance": amount}},
        upsert=True
    )

def get_balance(wallet_address: str) -> Optional[float]:
    """
    Get the balance for a wallet address.
    """
    doc = balances.find_one({"wallet_address": wallet_address})
    return doc["balance"] if doc else None

# --- Fraud Alert Helpers ---
def log_fraud_alert(tx_id: str, reason: str, score: float) -> str:
    """
    Log an ML fraud/anomaly detection alert for a transaction.
    Returns the inserted alert's ID.
    """
    alert = {
        "tx_id": tx_id,
        "reason": reason,
        "score": score
    }
    result = fraud_alerts.insert_one(alert)
    return str(result.inserted_id)

# --- Token Helpers ---
def create_token(name: str, symbol: str, total_supply: float, decimals: int = 18) -> str:
    """
    Create a new token and store in the tokens collection.
    """
    token_doc = {
        "name": name,
        "symbol": symbol,
        "total_supply": total_supply,
        "decimals": decimals,
        "balances": {},
    }
    result = tokens.insert_one(token_doc)
    return str(result.inserted_id)

def get_token(symbol: str) -> Optional[Dict[str, Any]]:
    """
    Get a token by its symbol.
    """
    return tokens.find_one({"symbol": symbol})

def update_token_balance(symbol: str, address: str, amount: float) -> None:
    """
    Set the token balance for an address.
    """
    tokens.update_one(
        {"symbol": symbol},
        {"$set": {f"balances.{address}": amount}},
        upsert=True
    )

def transfer_token(symbol: str, sender: str, receiver: str, amount: float) -> bool:
    """
    Transfer tokens between addresses. Returns True if successful.
    """
    token = get_token(symbol)
    if not token:
        return False
    balances = token.get("balances", {})
    if balances.get(sender, 0.0) < amount:
        return False
    balances[sender] -= amount
    balances[receiver] = balances.get(receiver, 0.0) + amount
    tokens.update_one(
        {"symbol": symbol},
        {"$set": {f"balances.{sender}": balances[sender], f"balances.{receiver}": balances[receiver]}}
    )
    return True

def ensure_miznet_token_exists():
    """Ensure the Miznet token exists in the database."""
    if not get_token("MIZ"):
        create_token("Miznet", "MIZ", 1_000_000, 18)

# Ensure Miznet token is present on import
ensure_miznet_token_exists() 