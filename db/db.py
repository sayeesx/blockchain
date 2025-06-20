import os
from pymongo import MongoClient
from dotenv import load_dotenv
from urllib.parse import urlparse

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError('MONGODB_URI not set in .env file')

# Create a MongoDB client
client = MongoClient(MONGODB_URI)

# Dynamically select the database from the URI
parsed = urlparse(MONGODB_URI)
db_name = (parsed.path[1:] if parsed.path else None) or os.getenv('MONGODB_DB', 'blockchain')
if not db_name:
    raise ValueError('Database name not found in MONGODB_URI or MONGODB_DB')
_db = client[db_name]

# Export collection references for easy use
blocks = _db['blocks']
transactions = _db['transactions']
balances = _db['balances']
fraud_alerts = _db['fraud_alerts']
tokens = _db['tokens']

# Export collection references for easy use
blocks = _db['blocks']
transactions = _db['transactions']
balances = _db['balances']
fraud_alerts = _db['fraud_alerts'] 