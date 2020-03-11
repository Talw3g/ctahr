
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .private import *

class CtahrMailing:

    def __init__(self):
        pass

    def connect(self):
        try:
            self.server = SMTP(mail['server'], mail['port'])
            return True
        except:
            return False


    def send_mail(self, subject, message):
        msg = MIMEMultipart()
        msg['From'] = mail['from_addr']
        msg['To'] = dest_address_1
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        self.server.starttls()
        self.server.login(mail['addr'], mail['pass'])
        self.server.sendmail(mail['addr'], dest_address_1, msg.as_string())
        self.server.quit()
