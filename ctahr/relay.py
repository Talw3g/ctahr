
import RPi.GPIO as GPIO

class CtahrRelay:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.pin, GPIO.OUT, initial = GPIO.LOW)

    def activate(self, b):
        GPIO.output(self.pin, GPIO.HIGH if b else GPIO.LOW)

