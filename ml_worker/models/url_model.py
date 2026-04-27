import random
import time
from .base_model import MockModel

class MockURLModel(MockModel):
    def predict(self, url: str):
        start = time.time()
        self.simulate_delay()
        
        url_length = len(url)
        special_char_count = sum(1 for c in url if c in ['@', '-', '~', '%'])
        has_ip = False # simple mock
        subdomain_depth = len(url.split('.'))
        has_https = "https://" in url.lower()
        
        risk_score = 0.0
        if url_length > 75: risk_score += 0.2
        if special_char_count > 3: risk_score += 0.25
        if has_ip: risk_score += 0.4
        if subdomain_depth > 4: risk_score += 0.2
        if not has_https: risk_score += 0.15
        
        if risk_score > 0.5:
            verdict = "phishing"
        else:
            verdict = "legitimate"
            
        confidence = min(0.55 + risk_score, 0.99)
        
        xai_data = {
            "type": "shap",
            "features": [
                {"feature": "url_length", "value": url_length, "contribution": 0.1},
                {"feature": "special_chars", "value": special_char_count, "contribution": 0.15},
                {"feature": "has_ip", "value": has_ip, "contribution": 0.0},
                {"feature": "subdomain_depth", "value": subdomain_depth, "contribution": 0.05},
                {"feature": "https", "value": has_https, "contribution": -0.1}
            ]
        }
        
        ms = int((time.time() - start) * 1000)
        return {"verdict": verdict, "confidence": confidence, "xai_data": xai_data, "processing_time_ms": ms}
