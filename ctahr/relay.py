
import time
import RPi.GPIO as GPIO

class CtahrRelay:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial = GPIO.LOW)

    def activate(self, b):
        GPIO.output(self.pin, GPIO.HIGH if b == 1 else GPIO.LOW)

    def blink(self):
        GPIO.output(self.pin, GPIO.HIGH)
        time.sleep(0.001)
        GPIO.output(self.pin, GPIO.LOW)
