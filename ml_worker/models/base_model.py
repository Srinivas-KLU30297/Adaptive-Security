from abc import ABC, abstractmethod
import time
import random

class MockModel(ABC):
    
    @abstractmethod
    def predict(self, input_data):
        """
        Returns: {verdict: str, confidence: float, xai_data: dict, processing_time_ms: int}
        """
        pass
        
    def simulate_delay(self):
        time.sleep(random.uniform(0.5, 2.5))
