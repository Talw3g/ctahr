
import threading,time
import RPi.GPIO as GPIO
import configuration

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

        self.starting_time_s = None
        self.up_time = 0
        self.daily_up_time = 0


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
            self.servo_set('OPEN')
            GPIO.output(configuration.fan_relay_pin, GPIO.HIGH)
            self.starting_time_s = time.time()
            self.state = 'RUNNING'

        elif self.state == 'RUNNING':
            if not self.app.logic.fan and not self.app.buttons.fan:
                self.state = 'STOPPING'

        elif self.state == 'STOPPING':
            GPIO.output(configuration.fan_relay_pin, GPIO.LOW)
            self.servo_set('CLOSE')
            self.up_time = time.time() - self.starting_time_s
            self.daily_up_time = self.daily_up_time + self.up_time
            self.state = 'IDLE'
            self.app.stats.fan_up_time = self.up_time

    def stop(self):
        self.running = False
        GPIO.output(configuration.fan_relay_pin, GPIO.LOW)
        self.servo_set('CLOSE')

    def run(self):
        while self.running:
#            with self.lock:
            self.update_state_machine()
            time.sleep(0.1)
        print "[-] Stopping fan manager"


