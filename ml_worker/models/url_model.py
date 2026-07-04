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
        
        url_lower = url.lower()
        suspicious_keywords = ['login', 'secure', 'verify', 'update', 'account', 'banking', 'paypal', 'apple', 'microsoft', 'google']
        keyword_count = sum(1 for k in suspicious_keywords if k in url_lower)
        
        suspicious_tlds = ['.xyz', '.top', '.tk', '.ml', '.ga', '.cf', '.gq', '.pw']
        has_suspicious_tld = any(tld in url_lower for tld in suspicious_tlds)
        
        risk_score = 0.0
        if url_length > 75: risk_score += 0.2
        if special_char_count > 2: risk_score += 0.25
        if has_ip: risk_score += 0.4
        if subdomain_depth > 3: risk_score += 0.3
        if not has_https: risk_score += 0.15
        if keyword_count > 0: risk_score += 0.25 * keyword_count
        if has_suspicious_tld: risk_score += 0.4
        
        if risk_score > 0.5:
            verdict = "phishing"
        else:
            verdict = "legitimate"
            
        confidence = min(0.55 + risk_score, 0.99)
        
        xai_data = {
            "type": "shap",
            "features": [
                {"feature": "url_length", "value": url_length, "contribution": 0.1 if url_length > 75 else 0.0},
                {"feature": "special_chars", "value": special_char_count, "contribution": 0.15 if special_char_count > 2 else 0.0},
                {"feature": "subdomain_depth", "value": subdomain_depth, "contribution": 0.2 if subdomain_depth > 3 else 0.0},
                {"feature": "suspicious_keywords", "value": keyword_count, "contribution": 0.25 * keyword_count},
                {"feature": "suspicious_tld", "value": has_suspicious_tld, "contribution": 0.4 if has_suspicious_tld else 0.0}
            ]
        }
        
        ms = int((time.time() - start) * 1000)
        return {"verdict": verdict, "confidence": confidence, "xai_data": xai_data, "processing_time_ms": ms}
