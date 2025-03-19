import smtplib
import ssl
import schedule
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
import os

class EmailAutomation:
    def __init__(self, smtp_server, smtp_port, username, password):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.connection = None

    def create_connection(self):
        context = ssl.create_default_context()
        self.connection = smtplib.SMTP(self.smtp_server, self.smtp_port)
        self.connection.ehlo()
        self.connection.starttls(context=context)
        self.connection.login(self.username, self.password)

    def close_connection(self):
        if self.connection:
            self.connection.quit()

    def send_email(self, to_email, subject, body, attachments=None):
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'plain'))

        if attachments:
            for file in attachments:
                with open(file, 'rb') as attachment:
                    part = MIMEApplication(attachment.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = f'attachment; filename="{os.path.basename(file)}"'
                msg.attach(part)

        self.create_connection()
        self.connection.sendmail(self.username, to_email, msg.as_string())
        self.close_connection()

    def schedule_email(self, to_email, subject, body, attachments=None, schedule_time=None):
        if schedule_time:
            schedule.every().day.at(schedule_time).do(self.send_email, to_email, subject, body, attachments=attachments)
        else:
            self.send_email(to_email, subject, body, attachments)

def log_email_send(to_email, subject):
    with open("email_log.txt", "a") as log_file:
        log_file.write(f"{datetime.now()}: Sent email to {to_email} with subject: {subject}\n")

def main():
    EMAIL_ADDRESS = "your_email@example.com"
    EMAIL_PASSWORD = "your_password"
    SMTP_SERVER = "smtp.example.com"
    SMTP_PORT = 587

    email_automation = EmailAutomation(SMTP_SERVER, SMTP_PORT, EMAIL_ADDRESS, EMAIL_PASSWORD)

    to_email = "recipient@example.com"
    subject = "Daily Report"
    body = "Please find the attached daily report."
    attachments = ["report.pdf"]

    schedule_time = "09:00"  # 9:00 AM

    email_automation.schedule_email(to_email, subject, body, attachments, schedule_time)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()