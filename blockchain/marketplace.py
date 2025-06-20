from typing import List, Dict, Any
from db.helpers import tokens, get_token, update_token_balance, transfer_token

marketplace_listings = tokens.database['marketplace_listings']

class Marketplace:
    """
    Marketplace for buying and selling tokens on SmartChain.
    """
    def list_token_for_sale(self, seller: str, symbol: str, amount: float, price_per_token: float) -> str:
        """List tokens for sale in the marketplace."""
        listing = {
            "seller": seller,
            "symbol": symbol,
            "amount": amount,
            "price_per_token": price_per_token,
            "status": "open"
        }
        result = marketplace_listings.insert_one(listing)
        return str(result.inserted_id)

    def get_listings(self, symbol: str = None) -> List[Dict[str, Any]]:
        """Get all open listings, optionally filtered by token symbol."""
        query = {"status": "open"}
        if symbol:
            query["symbol"] = symbol
        return list(marketplace_listings.find(query))

    def buy_token(self, buyer: str, listing_id: str, amount: float) -> bool:
        """Buy tokens from a listing. Handles partial and full purchases."""
        from bson.objectid import ObjectId
        listing = marketplace_listings.find_one({"_id": ObjectId(listing_id), "status": "open"})
        if not listing or listing["amount"] < amount:
            return False
        symbol = listing["symbol"]
        seller = listing["seller"]
        # Transfer tokens
        if not transfer_token(symbol, seller, buyer, amount):
            return False
        # Update listing
        new_amount = listing["amount"] - amount
        if new_amount <= 0:
            marketplace_listings.update_one({"_id": ObjectId(listing_id)}, {"$set": {"amount": 0, "status": "closed"}})
        else:
            marketplace_listings.update_one({"_id": ObjectId(listing_id)}, {"$set": {"amount": new_amount}})
        return True 