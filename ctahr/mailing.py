
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import private

class CtahrMailing:

    def __init__(self):
        pass

    def connect(self):
        try:
            self.server = SMTP(private.smtp_server_address, private.smtp_server_port)
            return True
        except:
            return False

    def send_mail(self, subject, message):
        msg = MIMEMultipart()
        msg['From'] = private.sender_address
        msg['To'] = private.dest_address_1
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        self.server.starttls()
        self.server.login(private.sender_address, private.smtp_server_password)
        self.server.sendmail(private.sender_address, private.dest_address_1, msg.as_string())
        self.server.quit()
