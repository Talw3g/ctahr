
import threading,time,os
import prctl
import subprocess
from datetime import datetime
from .mailing import CtahrMailing
from . import configuration

class CtahrSafety(threading.Thread):
#    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        prctl.set_name('Safety')
        self.app = app
        self.running = True
        self.int_time = time.monotonic()
        self.ext_time = time.monotonic()

        self.mail = CtahrMailing()


    def check_freshness(self, int_values, ext_values):
        if int_values[3] != 0:
            self.int_time = time.monotonic()
        if ext_values[3] != 0:
            self.ext_time = time.monotonic()

        if (time.monotonic() - self.int_time) > 300:
            self.kill('int_outdated',int_values)

        if (time.monotonic() - self.ext_time) > 300:
            self.kill('ext_outdated',ext_values)


    def logic_alive(self):
        if time.monotonic() - self.app.logic.watchdog > 120:
            self.kill('logic dead',self.app.logic.watchdog)
        else:
            pass


    def kill(self, reason, values):
        if reason == 'int_outdated':
            subject = 'Interior values outdated (>5min old)'
        elif reason == 'ext_outdated':
            subject = 'Exterior values outdated (>5min old)'
        elif reason == 'logic dead':
            subject = 'Logic module not running'

        args = ['journalctl','-u','ctahr.service','--since','yesterday']
        journal = subprocess.Popen(args, stdout=subprocess.PIPE)
        log = journal.stdout.read().decode('utf-8')
        message = datetime.now().strftime("%Y-%m-%d %H:%M:%S : " + str(values))
        message += '\n\n' + log
        if self.mail.connect():
            self.mail.send_mail(subject, message)
        else:
            with open(configuration.safety_log_file, 'a') as f:
                f.write(subject + '|' + message + '\n')

        os.system("shutdown -r now")
        self.running = False


    def stop(self):
        self.running = False


    def run(self):
        print("[+] Starting safety module")

        while self.running:
            int_values = self.app.thermohygro_interior.get()
            ext_values = self.app.thermohygro_exterior.get()
            self.check_freshness(int_values, ext_values)
            self.logic_alive()
            time.sleep(1)
        print("[-] Stopping safety module")
