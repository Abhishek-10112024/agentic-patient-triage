import os
import smtplib
from email.mime.text import MIMEText
# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()


class MCPEmailTool:
    def __init__(self):
        self.sender = os.getenv("EMAIL_USER")
        self.password = os.getenv("EMAIL_PASS")

    def send(self, summary: dict):
        try:
            subject = self._build_subject(summary)
            body = self._build_body(summary)

            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = self.sender
            msg["To"] = self.sender  # self-send (doctor simulation)

            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.sender, self.password)

            server.sendmail(self.sender, self.sender, msg.as_string())
            server.quit()

            return "MCP Email sent successfully"

        except Exception as e:
            return f"MCP Email Error: {str(e)}"

    def _build_subject(self, summary):
        return "🚨 MCP ALERT: Patient Case Requires Attention"

    def _build_body(self, summary):
        return f"""
MCP Patient Case Summary
------------------------

Symptoms:
{summary.get('symptoms')}

Duration:
{summary.get('duration')}

Severity Reason:
{summary.get('severity_reason')}

Recommendation:
{summary.get('recommendation')}

------------------------
This case was escalated automatically by the triage system.
"""