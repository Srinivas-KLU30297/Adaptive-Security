import smtplib
import os
from email.message import EmailMessage

from app.core.config import settings

def send_report_email(to_email: str, subject: str, body: str, pdf_path: str):
    smtp_host = settings.SMTP_HOST
    smtp_port = settings.SMTP_PORT
    smtp_user = settings.SMTP_USER
    smtp_pass = settings.SMTP_PASS

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = smtp_user or "noreply@cybershield.ai"
    msg['To'] = to_email
    msg.set_content(body)

    if os.path.exists(pdf_path):
        with open(pdf_path, 'rb') as f:
            pdf_data = f.read()
        msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))

    if not smtp_host or not smtp_user or not smtp_pass:
        print(f"[MOCK EMAIL] To: {to_email} | Subject: {subject} | Attachment: {os.path.basename(pdf_path)}")
        return False

    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"[EMAIL ERROR] Failed to send email: {e}")
        return False
