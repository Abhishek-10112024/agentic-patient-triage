import smtplib
from email.mime.text import MIMEText
import os
from dotenv import load_dotenv

load_dotenv()


def send_email(summary: dict):
    try:
        sender = os.getenv("EMAIL_USER")
        password = os.getenv("EMAIL_PASS")

        subject = "🚨 Patient Case - Immediate Attention Required"

        body = f"""
Patient Case Summary:

Symptoms: {summary.get('symptoms')}
Duration: {summary.get('duration')}
Severity Reason: {summary.get('severity_reason')}
Recommendation: {summary.get('recommendation')}
"""

        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = sender
        msg["To"] = sender  # sending to yourself

        # Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)

        server.sendmail(sender, sender, msg.as_string())
        server.quit()

        return "Email sent successfully"

    except Exception as e:
        return f"Email Error: {str(e)}"