
import threading,time,os
import prctl
import subprocess
from datetime import datetime
from .mailing import CtahrMailing
from .relay import CtahrRelay
from . import configuration as conf

class CtahrSafety(threading.Thread):
#    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        prctl.set_name('Safety')
        self.app = app
        self.running = True
        self.int_time = time.monotonic()
        self.ext_time = time.monotonic()
        self.buzzer = CtahrRelay(conf.buzzer_pin)
        self._alarm_mode = False

        self.mail = CtahrMailing()

    @property
    def reboot_count(self):
        if os.path.isfile(conf.reboot_count_file):
            with open(conf.reboot_count_file, 'r') as f:
                rc = int(f.read())
        else:
            rc = 0
        return rc

    @reboot_count.setter
    def reboot_count(self, value):
        with open(conf.reboot_count_file, 'w') as f:
            rc = f.write(str(value))
        
    @property
    def alarm_mode(self):
        return self._alarm_mode

    @alarm_mode.setter
    def alarm_mode(self, alarm_on):
        display = self.app.display
        if alarm_on == self._alarm_mode:
            return
        if alarm_on:
            print("Safety: entering alarm mode")
            self.buzzer.activate(True)
            display.state = "ERROR"
        else:
            print("Safety: leaving alarm mode")
            self.reboot_count = 0
            self.buzzer.activate(False)
            display.lib.clear()
            display.state = display.states_list[display.states_indice]
        self._alarm_mode = alarm_on

    def check_freshness(self, int_values, ext_values):
        if int_values[3] != 0:
            self.int_time = time.monotonic()
        if ext_values[3] != 0:
            self.ext_time = time.monotonic()

        if (time.monotonic() - self.int_time) > 300:
            self.kill('int_outdated',int_values)
        elif (time.monotonic() - self.ext_time) > 300:
            self.kill('ext_outdated',ext_values)
        else:
            self.alarm_mode = False


    def logic_alive(self):
        if time.monotonic() - self.app.logic.watchdog > 5:
            self.kill('logic dead',self.app.logic.watchdog)
        else:
            self.feed_watchdog()


    def kill(self, reason, values):
        if self.alarm_mode:
            return

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
            with open(conf.safety_log_file, 'a') as f:
                f.write(subject + '|' + message + '\n')
        if self.reboot_count == 0:
            print("Safety: killing, rc=0 ==> rebooting")
            self.reboot_count = 1
            os.system("shutdown -r now")
            self.running = False
        else:
            self.alarm_mode = True


    def feed_watchdog(self):
        with open(conf.watchdog_file, 'w') as f:
            f.write('miam')


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
