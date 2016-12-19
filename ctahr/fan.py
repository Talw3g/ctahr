
import threading,time
import RPi.GPIO as GPIO
import configuration

class CtahrFan(threading.Thread):
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

    def servo_set(self, cmd):
        GPIO.output(configuration.servo_power_pin, GPIO.HIGH)
        print "servo ON"
        time.sleep(0.5)
        if cmd == 'OPEN':
            print "opening"
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_open)
        elif cmd == 'CLOSE':
            print "closing"
            self.pwm.ChangeDutyCycle(
                configuration.servo_dutycycle_close)
        time.sleep(0.7)
        GPIO.output(configuration.servo_power_pin, GPIO.LOW)
        print "servo OFF"


    def update_state_machine(self):
        if self.state == 'IDLE':
            # nothing to do
            pass

        elif self.state == 'STARTING':
            self.servo_set('OPEN')
            GPIO.output(configuration.fan_relay_pin, GPIO.HIGH)
            self.starting_time_s = time.time()
            self.state = 'RUNNING'

        elif self.state == 'RUNNING':
            pass

        elif self.state == 'STOPPING':
            self.servo_set('CLOSE')
            GPIO.output(configuration.fan_relay_pin, GPIO.LOW)
            self.state = 'IDLE'

    def stop(self):
        self.running = False
        self.state = 'STOPPING'

    def run(self):
        while self.running:
            with self.lock:
                self.update_state_machine()
                time.sleep(0.1)
        self.update_state_machine()
        print "[-] Stopping fan manager"


