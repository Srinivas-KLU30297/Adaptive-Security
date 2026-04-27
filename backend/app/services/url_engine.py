import datetime
import whois
import requests
import socket
import ssl
from urllib.parse import urlparse
from transformers import pipeline

class URLPhishingEngine:
    def __init__(self):
        print("Loading URL Phishing Detection model...")
        model_name = "peeyush01/phishing-url-bert-tiny-v1"
        self.pipeline = pipeline("text-classification", model=model_name, tokenizer=model_name, truncation=True, max_length=512)
        print("URL model loaded.")

    def check_domain_age(self, domain: str):
        try:
            w = whois.whois(domain)
            creation_date = w.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            if creation_date:
                age_days = (datetime.datetime.now() - creation_date).days
                return age_days
        except Exception:
            return None
        return None

    def check_ssl(self, domain: str):
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=3) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return True
        except Exception:
            return False
            
    def check_redirects(self, url: str):
        try:
            if not url.startswith("http"):
                url = "http://" + url
            response = requests.head(url, allow_redirects=True, timeout=5)
            return len(response.history)
        except Exception:
            return -1

    def process_url(self, url: str):
        parsed = urlparse(url if "://" in url else "http://" + url)
        domain = parsed.netloc if parsed.netloc else parsed.path.split('/')[0]
        
        reasons = []
        threat_type = "safe"
        
        # 1. Run ML Model
        ml_result = self.pipeline(url, max_length=512, truncation=True)[0]
        label = ml_result["label"].lower()
        
        # Determine ML score (usually LABEL_1 is phishing for peeyush01 model)
        # Note: if it's LABEL_1 and it means phishing, score is the confidence.
        # Let's check label. We assume phishing if label != LABEL_0.
        is_ml_phishing = label != "label_0" and "benign" not in label
        if is_ml_phishing:
            ml_score = ml_result["score"]
        else:
            ml_score = 1.0 - ml_result["score"]
            
        reasons.append(f"ML Model predicted phishing probability at {ml_score*100:.1f}%.")
            
        # 2. Heuristics Score Calculation
        heuristic_penalty = 0.0
        
        age = self.check_domain_age(domain)
        if age is not None:
             if age < 30:
                 heuristic_penalty += 0.40
                 reasons.append(f"Suspicious domain age: {age} days (under 30 days).")
        else:
             # Could not determine age, apply slight penalty
             heuristic_penalty += 0.10
        
        has_ssl = self.check_ssl(domain)
        if not has_ssl:
             heuristic_penalty += 0.30
             reasons.append("Invalid or missing SSL certificate.")
             
        redirects = self.check_redirects(url)
        if redirects > 3:
             heuristic_penalty += 0.30
             reasons.append(f"Suspicious redirect chain ({redirects} redirects observed).")
             
        heuristic_score = min(1.0, heuristic_penalty)

        # 3. Final Scoring
        final_score = (ml_score * 0.65) + (heuristic_score * 0.35)
        
        if final_score > 0.75:
             verdict = "threat"
             threat_type = "phishing"
             reasons.append(f"Final combined score {final_score*100:.1f}% indicates threat.")
        elif final_score >= 0.50:
             verdict = "suspicious"
             threat_type = "suspicious"
             reasons.append(f"Final combined score {final_score*100:.1f}% is suspicious.")
        else:
             verdict = "safe"
             threat_type = "safe"
             reasons.append(f"Final combined score {final_score*100:.1f}% is safe.")

        return {
             "verdict": verdict,
             "confidence": float(final_score),
             "ml_score": float(ml_score),
             "heuristic_score": float(heuristic_score),
             "domain_age_days": age if age is not None else -1,
             "ssl_valid": bool(has_ssl),
             "redirect_count": int(redirects),
             "reasons": reasons,
             "threat_type": threat_type
        }

url_engine = URLPhishingEngine()
