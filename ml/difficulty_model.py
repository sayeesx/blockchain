import numpy as np
from sklearn.linear_model import LinearRegression
from typing import List, Tuple

class DifficultyAdjuster:
    def __init__(self):
        self.model = LinearRegression()
        
    def prepare_data(self, 
                    block_times: List[float], 
                    difficulties: List[int]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features and target for training."""
        X = np.array(block_times[:-1]).reshape(-1, 1)
        y = np.array(difficulties[1:])
        return X, y
        
    def train(self, block_times: List[float], difficulties: List[int]) -> None:
        """Train the difficulty prediction model."""
        X, y = self.prepare_data(block_times, difficulties)
        self.model.fit(X, y)
        
    def predict_next_difficulty(self, current_block_time: float) -> int:
        """Predict optimal difficulty for next block."""
        prediction = self.model.predict([[current_block_time]])[0]
        return max(1, int(round(prediction)))  # Ensure minimum difficulty of 1