
import time,os
from datetime import datetime
from smtplib import SMTP
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import private

class CtahrSecurity:

    def __init__(self):
        self.int_time = time.time()
        self.ext_time = time.time()

    def check_freshness(self, int_values, ext_values):
        if int_values != None:
            self.int_time = int_values[2]
        if ext_values != None:
            self.ext_time = ext_values[2]

        if (time.time() - self.int_time) > 300:
            self.kill('int_outdated',int_values)

        if (time.time() - self.ext_time) > 300:
            self.kill('ext_outdated',ext_values)

    def kill(self, reason, values):
        if reason == 'int_outdated':
            subject = 'Interior values outdated (>5min old)'
            message = datetime.now().strftime("%Y-%m-%d %H:%M:%S : " + str(values))
            self.mail(subject, message)
        if reason == 'ext_outdated':
            subject = 'Exterior values outdated (>5min old)'
            message = datetime.now().strftime("%Y-%m-%d %H:%M:%S : " + str(values))
            self.mail(subject, message)

        os.system("shutdown -r now")


    def mail(self, subject, message):
        msg = MIMEMultipart()
        msg['From'] = private.sender_address
        msg['To'] = private.dest_address_1
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))

        server = SMTP(private.smtp_server_address, private.smtp_server_port)
        server.starttls()
        server.login(private.sender_address, private.smtp_server_password)
        server.sendmail(private.sender_address, private.dest_address_1, msg.as_string())
        server.quit()


