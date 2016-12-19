
import threading,time
import RPi.GPIO as GPIO
import configuration

def CtahrFan(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.lock = threading.Lock()
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

    def turn_on(self):
        with self.lock:
            self.state = 'STARTING'

    def turn_off(self):
        with self.lock:
            self.state = 'STOPPING'

    def servo_set(self, state):
        GPIO.output(configuration.servo_power_pin, GPIO.HIGH)
        time.sleep(0.5)
        if state == 'OPEN':
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_open)
        elif state == 'CLOSE':
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_close)
        time.sleep(0.7)
        GPIO.output(configuration.servo_power_pin, GPIO.LOW)


    def update_state_machine(self):
        if self.state == 'IDLE':
            # nothing to do
            pass

        elif self.state == 'STARTING':
            self.servo_set('OPEN')
            GPIO.output(configuration.fan_relay_pin, GPIO.HIGH)
            self.starting_time_s = time.time()
            self.state = 'STARTING_WAIT'

        elif self.state == 'STARTING_WAIT':
            if time.time() - self.starting_time_s > 1.0:
                self.state = 'RUNNING'

        elif self.state == 'RUNNING':
            pass

        elif self.state == 'STOPPING':
            pass

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            with self.lock:
                self.update_state_machine()
                time.sleep(0.1)
        print "[-] Stopping fan manager"


