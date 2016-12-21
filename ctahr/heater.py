
import time
import RPi.GPIO as GPIO
import configuration

class CtahrHeater:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(configuration.heater_relay_pin, GPIO.OUT,
            initial = GPIO.LOW)
        self.state = 'OFF'
        self.starting_time = None

    def update_state(self):
        if self.state == 'OFF':
            pass
        elif self.state == 'STARTING':
            GPIO.output(configuration.heater_relay_pin, GPIO.HIGH)
            self.starting_time = time.time()
            self.state = 'ON'
        elif self.state == 'ON':
            pass
        elif self.state == 'STOPPING':
            GPIO.output(configuration.heater_relay_pin, GPIO.LOW)
            self.app.stats.heater_up_time = time.time() - self.starting_time
            self.state = 'OFF'
