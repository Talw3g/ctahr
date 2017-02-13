
import threading,time
import RPi.GPIO as GPIO
from . import configuration

class CtahrFan(threading.Thread):
    def __init__(self, app):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
        self.app = app
        self.state = 'IDLE'
        self.running = True
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(configuration.fan_relay_pin, GPIO.OUT,
            initial = GPIO.LOW)
        GPIO.setup(configuration.servo_power_pin, GPIO.OUT,
            initial = GPIO.LOW)
        GPIO.setup(configuration.servo_pwm_pin, GPIO.OUT,
            initial = GPIO.LOW)

        self.pwm = GPIO.PWM(configuration.servo_pwm_pin, 50)
        self.pwm.start(configuration.servo_dutycycle_close)

        self.current_ts = None
        self.cycle_ts = None
        self.uptime = 0
        self.cycle_uptime = 0


    def servo_set(self, cmd):
        GPIO.output(configuration.servo_power_pin, GPIO.HIGH)
        time.sleep(0.5)

        if cmd == 'OPEN':
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_open)
        elif cmd == 'CLOSE':
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_close)

        time.sleep(0.7)
        GPIO.output(configuration.servo_power_pin, GPIO.LOW)


    def update_state_machine(self):
        if self.state == 'IDLE':
            if self.app.logic.fan or self.app.buttons.fan:
                self.state = 'STARTING'

        elif self.state == 'STARTING':
            self.current_ts = time.monotonic()
            self.cycle_ts = time.monotonic()
            self.servo_set('OPEN')
            GPIO.output(configuration.fan_relay_pin, GPIO.HIGH)
            self.state = 'RUNNING'

        elif self.state == 'RUNNING':
            if not self.app.logic.fan and not self.app.buttons.fan:
                self.state = 'STOPPING'

        elif self.state == 'STOPPING':
            self.uptime += time.monotonic() - self.current_ts
            self.cycle_uptime = time.monotonic() - self.cycle_ts
            GPIO.output(configuration.fan_relay_pin, GPIO.LOW)
            self.servo_set('CLOSE')
            self.state = 'IDLE'

    def get_uptime(self):
        if self.state == 'STARTING' or self.state == 'RUNNING':
            current_uptime = (self.uptime + time.monotonic()
                - self.current_ts)
        else:
            current_uptime = self.uptime
        return current_uptime

    def reset_uptime(self):
        self.uptime = 0
        if self.state == 'RUNNING':
            self.current_ts = time.monotonic()

    def stop(self):
        self.running = False
        GPIO.output(configuration.fan_relay_pin, GPIO.LOW)
        self.servo_set('CLOSE')

    def run(self):
        print("[+] Starting fan manager")

        while self.running:
            self.update_state_machine()
            time.sleep(0.1)
        print("[-] Stopping fan manager")


