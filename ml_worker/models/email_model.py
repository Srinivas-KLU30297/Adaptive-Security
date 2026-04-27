import random
import time
from .base_model import MockModel

class MockEmailModel(MockModel):
    def predict(self, text: str):
        start = time.time()
        self.simulate_delay()
        
        keywords = ["verify", "urgent", "password", "click here", "suspended", "bank", "account", "login"]
        text_lower = text.lower()
        found = sum(1 for k in keywords if k in text_lower)
        
        if found >= 2:
            verdict = "phishing"
            confidence = 0.85 + random.uniform(0, 0.1)
        else:
            verdict = "legitimate"
            confidence = 0.75 + random.uniform(0, 0.15)
            
        xai_data = {
            "type": "shap",
            "top_features": [
                {"token": "urgent", "shap_value": 0.4, "position": 10},
                {"token": "verify", "shap_value": 0.35, "position": 25},
                {"token": "login", "shap_value": 0.2, "position": 50}
            ]
        }
        
        ms = int((time.time() - start) * 1000)
        return {
            "verdict": verdict,
            "confidence": confidence,
            "xai_data": xai_data,
            "processing_time_ms": ms
        }
