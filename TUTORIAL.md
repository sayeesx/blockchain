# SmartChain Tutorial

This tutorial will guide you through setting up and using the SmartChain blockchain project.

## 1. Setup Environment

### Prerequisites
- Python 3.8 or higher
- Git
- Visual Studio Code (recommended)

### Installation Steps
```batch
# Clone the repository (if using git)
git clone <repository-url>
cd Blockchain

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 2. Project Structure
```
smartchain/
├── blockchain/
│   ├── block.py         # Block implementation
│   ├── chain.py         # Blockchain core
│   └── transaction.py   # Transaction handling
├── ml/
│   ├── fraud_detection.py    # ML fraud detection
│   └── difficulty_model.py   # Dynamic difficulty
├── app.py              # FastAPI application
└── requirements.txt    # Dependencies
```

## 3. Running the Blockchain

### Start the API Server
```batch
python app.py
```
The server will start at `http://localhost:8000`

### API Documentation
Access the interactive API docs at `http://localhost:8000/docs`

## 4. Using the API

### Create a Transaction
```bash
curl -X POST "http://localhost:8000/add_transaction" \
     -H "Content-Type: application/json" \
     -d '{"sender": "Alice", "receiver": "Bob", "amount": 50.0}'
```

### Mine a Block
```bash
curl -X POST "http://localhost:8000/mine_block"
```

### View the Blockchain
```bash
curl "http://localhost:8000/get_chain"
```

## 5. Example Workflow

```python
# Example Python code to interact with the blockchain
import requests

BASE_URL = "http://localhost:8000"

# Add a transaction
def add_transaction():
    response = requests.post(
        f"{BASE_URL}/add_transaction",
        params={
            "sender": "Alice",
            "receiver": "Bob",
            "amount": 50.0
        }
    )
    print(response.json())

# Mine a block
def mine_block():
    response = requests.post(f"{BASE_URL}/mine_block")
    print(response.json())

# View the chain
def view_chain():
    response = requests.get(f"{BASE_URL}/get_chain")
    print(response.json())
```

## 6. Features

### 6.1 Fraud Detection
The system uses machine learning to detect suspicious transactions:
```bash
curl -X POST "http://localhost:8000/detect_fraud" \
     -H "Content-Type: application/json" \
     -d '{"transactions": [{"sender": "Alice", "receiver": "Bob", "amount": 1000000}]}'
```

### 6.2 Dynamic Difficulty
The blockchain automatically adjusts mining difficulty based on:
- Network hash rate
- Block creation time
- Transaction volume

### 6.3 Transaction Validation
Each transaction is validated for:
- Valid sender/receiver addresses
- Positive amount
- Sufficient balance

## 7. Testing

Run the test suite:
```batch
python -m pytest tests/
```

## 8. Common Issues & Solutions

### Issue 1: Import Errors
If you see "ModuleNotFoundError", ensure:
- Virtual environment is activated
- You're in the project root directory
- All dependencies are installed

### Issue 2: API Connection Failed
Check:
- Server is running
- Correct port (8000) is being used
- No firewall blocking

## 9. Development Guidelines

### Adding New Features
1. Create feature branch
2. Implement changes
3. Add tests
4. Create pull request

### Code Style
- Follow PEP 8
- Add type hints
- Document functions
- Keep methods small and focused

## 10. Security Considerations

- Use secure key generation
- Validate all inputs
- Handle exceptions properly
- Don't expose sensitive data in logs

## 11. Next Steps

Consider exploring:
1. Adding smart contracts
2. Implementing consensus mechanisms
3. Creating a web interface
4. Adding more ML features

For support or contributions, please refer to the README.md file.