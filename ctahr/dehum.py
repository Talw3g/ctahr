
import threading,time
import RPi.GPIO as GPIO
import configuration

class CtahrDehum(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        print "[+] Starting dehum manager"

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(configuration.dehum_relay_pin, GPIO.OUT,
            initial = GPIO.LOW)
        self.state = 'OFF'
        self.running = True
        self.starting_time = None

    def update_state(self):
        if self.state == 'OFF':
            if self.app.logic.dehum or self.app.buttons.dehum:
                self.state = 'STARTING'

        elif self.state == 'STARTING':
            GPIO.output(configuration.dehum_relay_pin, GPIO.HIGH)
            self.starting_time = time.time()
            self.state = 'ON'

        elif self.state == 'ON':
            if not self.app.logic.dehum and not self.app.buttons.dehum:
                self.state = 'STOPPING'

        elif self.state == 'STOPPING':
            GPIO.output(configuration.dehum_relay_pin, GPIO.LOW)
            self.app.stats.dehum_uptime = time.time() - self.starting_time
            self.state = 'OFF'

    def stop(self):
        self.running = False
        GPIO.output(configuration.dehum_relay_pin, GPIO.LOW)


    def run(self):
        while self.running:
            self.update_state()
            time.sleep(1)

        print "[-] Stopping dehum manager"
