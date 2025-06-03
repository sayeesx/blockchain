import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.svm import OneClassSVM
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Any

class FraudDetector:
    def __init__(self):
        self.isolation_forest = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.one_class_svm = OneClassSVM(
            kernel='rbf',
            nu=0.1
        )
        self.scaler = StandardScaler()
        
    def preprocess_transactions(self, transactions: List[Dict[str, Any]]) -> np.ndarray:
        """Convert transactions to features matrix."""
        features = []
        for tx in transactions:
            features.append([
                float(tx['amount']),
                float(tx['timestamp']),
                hash(tx['sender']) % 1e6,  # Simple hash-based feature
                hash(tx['receiver']) % 1e6
            ])
        return self.scaler.fit_transform(np.array(features))
    
    def train(self, transactions: List[Dict[str, Any]]) -> None:
        """Train anomaly detection models."""
        X = self.preprocess_transactions(transactions)
        self.isolation_forest.fit(X)
        self.one_class_svm.fit(X)
        
    def detect_anomalies(self, transactions: List[Dict[str, Any]]) -> List[bool]:
        """Detect fraudulent transactions using ensemble method."""
        X = self.preprocess_transactions(transactions)
        
        # Combine predictions from both models
        if_pred = self.isolation_forest.predict(X)
        svm_pred = self.one_class_svm.predict(X)
        
        # Consider transaction fraudulent if both models flag it
        return [(i == -1 and s == -1) for i, s in zip(if_pred, svm_pred)]