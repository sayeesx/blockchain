import os
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the MongoDB URI from environment variables
MONGODB_URI = os.getenv('MONGODB_URI')
if not MONGODB_URI:
    raise ValueError('MONGODB_URI not set in .env file')

# Create a MongoDB client
client = MongoClient(MONGODB_URI)

# Connect to the 'smartchain' database
_db = client['smartchain']

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