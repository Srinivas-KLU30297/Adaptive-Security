import email
from email import policy
import re
from transformers import pipeline
from app.services.url_engine import url_engine

def clean_email_text(raw_text: str) -> str:
    text = re.sub(r'<[^>]+>', '', raw_text)
    text = re.sub(r'__.*?__', '', text)
    text = re.sub(r'\w{3}, \w{3} \d+,.*?(AM|PM).*', '', text)
    text = re.sub(r'https?://(track|click|open|opens)\.[^\s]+', '', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()

class EmailPhishingEngine:
    def __init__(self):
        print("Loading Email Phishing Detection models...")
        self.pipeline1 = pipeline("text-classification", model="ealvaradob/bert-finetuned-phishing", truncation=True, max_length=512)
        self.pipeline2 = pipeline("text-classification", model="cybersectony/phishing-email-detection-distilbert_v2.4.1", truncation=True, max_length=512)
        print("Email models loaded.")

    def extract_urls(self, text):
        url_pattern = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        return url_pattern.findall(text)

    def process_email(self, raw_email_text: str):
        reasons = []
        threat_type = "safe"
        
        # 1. Parse email for structural header checks
        msg = email.message_from_string(raw_email_text, policy=policy.default)
        
        legitimacy_bonus = 0.0
        
        # Check List-Unsubscribe
        if msg.get('List-Unsubscribe'):
            legitimacy_bonus += 0.20
            reasons.append("List-Unsubscribe header present (-0.20 risk)")
            
        # Check DKIM-Signature (RFC 5322 or Gmail Summary)
        if msg.get('DKIM-Signature') or re.search(r'(?im)^DKIM:\s*\'?PASS\'?', raw_email_text):
            legitimacy_bonus += 0.15
            reasons.append("DKIM-Signature validated (-0.15 risk)")
            
        # Check SPF pass (RFC 5322 or Gmail Summary)
        auth_results = msg.get('Authentication-Results', '')
        if 'spf=pass' in str(auth_results).lower() or re.search(r'(?im)^SPF:\s*PASS', raw_email_text):
            legitimacy_bonus += 0.10
            reasons.append("SPF check passed (-0.10 risk)")
            
        # Check DMARC pass (Gmail Summary)
        if re.search(r'(?im)^DMARC:\s*\'?PASS\'?', raw_email_text) or 'dmarc=pass' in str(auth_results).lower():
            legitimacy_bonus += 0.20
            reasons.append("DMARC check passed (-0.20 risk)")
            
        # Check From vs Reply-To domain match
        sender = msg.get('From', '')
        reply_to = msg.get('Reply-To', '')
        
        sender_email_match = re.search(r'<([^>]+)>', sender)
        sender_email = sender_email_match.group(1) if sender_email_match else sender.strip()
        sender_domain = sender_email.split('@')[-1].lower() if '@' in sender_email else ""
        
        reply_to_match = re.search(r'<([^>]+)>', reply_to)
        reply_to_email = reply_to_match.group(1) if reply_to_match else reply_to.strip()
        reply_to_domain = reply_to_email.split('@')[-1].lower() if '@' in reply_to_email else ""
        
        if sender_domain and reply_to_domain and sender_domain == reply_to_domain:
            legitimacy_bonus += 0.10
            reasons.append(f"From and Reply-To domains match ({sender_domain}) (-0.10 risk)")
            
        # Cap legitimacy bonus at 0.45 (increased to allow perfect headers to mark aggressive marketing as Safe)
        legitimacy_bonus = min(legitimacy_bonus, 0.45)
        
        # 2. Extract Body and Clean
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type in ('text/plain', 'text/html'):
                    try:
                        body += part.get_payload(decode=True).decode()
                    except:
                        pass
        else:
            payload = msg.get_payload(decode=True)
            if payload is not None:
                try:
                    body = payload.decode(errors='ignore')
                except:
                    body = str(payload)
            else:
                body = str(msg.get_payload())
                
        if not body:
            body = raw_email_text
            
        cleaned_text = clean_email_text(raw_email_text)
        
        # 3. Run ML Models
        # Model 1
        res1 = self.pipeline1(cleaned_text[:2000], truncation=True, max_length=512)[0]
        # model 1 labels: usually 'phishing' or something similar
        label1 = res1["label"].lower()
        model1_score = res1["score"] if "phishing" in label1 else (1.0 - res1["score"])
        
        # Model 2
        res2 = self.pipeline2(cleaned_text[:2000], truncation=True, max_length=512)[0]
        # cybersectony/phishing-email-detection-distilbert_v2.4.1 outputs LABEL_1 for phishing
        label2 = res2["label"].lower()
        if label2 in ["phishing", "phishing email", "label_1", "label_3"]:
            model2_score = res2["score"]
        else:
            model2_score = 1.0 - res2["score"]

        # 4. Scoring
        raw_score = (model1_score * 0.55) + (model2_score * 0.45)
        final_score = max(0, raw_score - legitimacy_bonus)
        
        if final_score > 0.85:
            verdict = "threat"
            threat_type = "phishing"
            reasons.append(f"Ensemble score {final_score*100:.1f}% indicates critical threat.")
        elif final_score >= 0.60:
            verdict = "suspicious"
            threat_type = "suspicious"
            reasons.append(f"Ensemble score {final_score*100:.1f}% indicates suspicious content.")
        else:
            verdict = "safe"
            reasons.append(f"Ensemble score {final_score*100:.1f}% indicates safe content.")
            
        # 5. Extract and check URLs (Independently, NO OVERRIDE)
        urls = self.extract_urls(raw_email_text)
        for u in urls:
            url_res = url_engine.process_url(u)
            if url_res["verdict"] == "threat":
                reasons.append(f"Embedded malicious URL found: {u} (WARNING: This does not override email verdict)")
                if verdict == "safe":
                    verdict = "suspicious" # We can flag it as suspicious if there's a bad URL, but we won't fully override the email final_score math
                    threat_type = "malicious_link"

        return {
            "verdict": verdict,
            "confidence": float(final_score),
            "model1_score": float(model1_score),
            "model2_score": float(model2_score),
            "legitimacy_bonus": float(legitimacy_bonus),
            "reasons": reasons,
            "threat_type": threat_type
        }

email_engine = EmailPhishingEngine()
