from typing import Dict, Any

class Token:
    """
    Represents a custom token (coin) for the SmartChain blockchain.
    """
    def __init__(self, name: str, symbol: str, total_supply: float, decimals: int = 18):
        self.name = name
        self.symbol = symbol
        self.total_supply = total_supply
        self.decimals = decimals
        self.balances: Dict[str, float] = {}

    def mint(self, to: str, amount: float) -> None:
        """Mint new tokens to a wallet address."""
        self.total_supply += amount
        self.balances[to] = self.balances.get(to, 0.0) + amount

    def burn(self, from_addr: str, amount: float) -> bool:
        """Burn tokens from a wallet address."""
        if self.balances.get(from_addr, 0.0) < amount:
            return False
        self.total_supply -= amount
        self.balances[from_addr] -= amount
        return True

    def transfer(self, sender: str, receiver: str, amount: float) -> bool:
        """Transfer tokens between addresses."""
        if self.balances.get(sender, 0.0) < amount:
            return False
        self.balances[sender] -= amount
        self.balances[receiver] = self.balances.get(receiver, 0.0) + amount
        return True

    def get_balance(self, address: str) -> float:
        """Get the token balance of an address."""
        return self.balances.get(address, 0.0)

    def to_dict(self) -> Dict[str, Any]:
        """Return token metadata and balances as a dictionary."""
        return {
            "name": self.name,
            "symbol": self.symbol,
            "total_supply": self.total_supply,
            "decimals": self.decimals,
            "balances": self.balances
        }

# Default instance for the Miznet token
miznet_token = Token(name="Miznet", symbol="MIZ", total_supply=1_000_000, decimals=18) 