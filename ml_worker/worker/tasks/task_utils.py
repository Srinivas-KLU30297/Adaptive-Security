from typing import Optional

def compute_risk_level(confidence: float, verdict: str) -> str:
    if verdict in ["phishing", "deepfake"]:
        if confidence > 0.9: return "critical"
        elif confidence > 0.75: return "high"
        elif confidence > 0.6: return "medium"
        else: return "low"
    else:
        return "low"
