
import threading,time
import RPi.GPIO as GPIO
from . import configuration

class CtahrHeater(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        print("[+] Starting heater manager")

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(configuration.heater_relay_pin, GPIO.OUT,
            initial = GPIO.LOW)
        self.state = 'OFF'
        self.running = True
        self.starting_time = None

    def update_state(self):
        if self.state == 'OFF':
            if self.app.logic.heat or self.app.buttons.heater:
                self.state = 'STARTING'

        elif self.state == 'STARTING':
            GPIO.output(configuration.heater_relay_pin, GPIO.HIGH)
            self.starting_time = time.monotonic()
            self.state = 'ON'

        elif self.state == 'ON':
            if not self.app.logic.heat and not self.app.buttons.heater:
                self.state = 'STOPPING'

        elif self.state == 'STOPPING':
            GPIO.output(configuration.heater_relay_pin, GPIO.LOW)
            self.app.stats.heater_uptime = time.monotonic() - self.starting_time
            self.state = 'OFF'

    def stop(self):
        self.running = False
        GPIO.output(configuration.heater_relay_pin, GPIO.LOW)


    def run(self):
        while self.running:
            self.update_state()
            time.sleep(0.1)

        print("[-] Stopping heater manager")
