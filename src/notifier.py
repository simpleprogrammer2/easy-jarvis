import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

class Notifier:
    def __init__(self):
        self.enabled = os.getenv("EMAIL_NOTIFICATIONS", "False").lower() == "true"
        self.recipient = os.getenv("ALERT_EMAIL", "alina9675@gmail.com")
        self.sender = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASS")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))

    def send_alert(self, subject, message):
        """Sends an emergency email alert."""
        if not self.enabled:
            print(f"[!] Notification Disabled: {subject} - {message}")
            return

        if not self.sender or not self.password:
            print("[!] Notification Error: SMTP_USER or SMTP_PASS not set in .env")
            return

        print(f"[*] Sending Emergency Alert to {self.recipient}...")
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender
            msg['To'] = self.recipient
            msg['Subject'] = f"🚨 JARVIS ALERT: {subject}"

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender, self.password)
            text = msg.as_string()
            server.sendmail(self.sender, self.recipient, text)
            server.quit()
            print("[+] Alert sent successfully.")
        except Exception as e:
            print(f"[!] Failed to send email: {e}")

if __name__ == "__main__":
    # Test
    n = Notifier()
    # n.send_alert("Test Alert", "This is a test from the Jarvis Autonomous System.")
