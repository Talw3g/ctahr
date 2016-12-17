
import RPi.GPIO as GPIO

class CtahrRelay:
    def __init__(self, pin):
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.OUT, initial = GPIO.LOW)

    def activate(self, b):
        if b == 1:
            GPIO.output(self.pin, GPIO.HIGH)
        else:
            GPIO.output(self.pin, GPIO.LOW)
