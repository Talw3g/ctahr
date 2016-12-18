
import threading,time,os
from datetime import datetime
from mailing import CtahrMailing

class CtahrSecurity(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app

        self.int_time = time.time()
        self.ext_time = time.time()

        self.mail = CtahrMailing()

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
            self.mail.send_mail(subject, message)
        if reason == 'ext_outdated':
            subject = 'Exterior values outdated (>5min old)'
            message = datetime.now().strftime("%Y-%m-%d %H:%M:%S : " + str(values))
            self.mail.send_mail(subject, message)

        os.system("shutdown -r now")


    def run(self):
        while True:
            int_values = self.app.thermohygro_interior.get()
            ext_values = self.app.thermohygro_exterior.get()
            self.check_freshness(int_values, ext_values)

            time.sleep(1)
