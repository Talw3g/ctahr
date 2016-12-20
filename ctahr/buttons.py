
import time,threading
import configuration
import RPi.GPIO as GPIO

class CtahrButtons(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.lock = threading.Lock()

        print "[+] Starting buttons manager"

        self.reset_state = 'WAIT'
        self.fan_state = 'WAIT'
        self.heater_state = 'WAIT'
        self.dehum_state = 'WAIT'

        self.running = True

        # Setting up GPIOs
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(configuration.reset_lever_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(configuration.fan_lever_pin, GPIO.IN)
        GPIO.setup(configuration.dehum_lever_pin, GPIO.IN)
        GPIO.setup(configuration.heater_lever_pin, GPIO.IN)

    def update_reset(self):
        if self.reset_state == 'WAIT':
            if GPIO.input(configuration.reset_lever_pin) == 0:
                self.reset_state = 'UP'
                self.reset_up_time = time.time()
        elif self.reset_state == 'UP':
            if (time.time() - self.reset_up_time) > 3:
                pass
            elif (time.time() - self.reset_up_time) > 1:
                pass

            if GPIO.input(configuration.reset_lever_pin) == 1:
                self.reset_state = 'DOWN'
        elif self.reset_state == 'DOWN':
            if (time.time() - self.reset_up_time) < 0.5:
                self.app.display.cycle_states()
            self.reset_state = 'WAIT'

    def update_fan(self):
        if self.fan_state == 'WAIT':
            if GPIO.input(configuration.fan_lever_pin) == 1:
                self.app.fan.force(True)
                self.fan_state = 'UP'
        if self.fan_state == 'UP':
            if GPIO.input(configuration.fan_lever_pin) == 0:
                self.app.fan.force(False)
                self.fan_state = 'WAIT'

    def update_heater(self):
        if self.heater_state == 'WAIT':
            if GPIO.input(configuration.heater_lever_pin) == 1:
                self.app.logic.heater_force = True
                self.heater_state = 'UP'
        elif self.heater_state == 'UP':
            if GPIO.input(configuration.heater_lever_pin) == 0:
                self.app.logic.heater_force = False
                self.heater_state = 'WAIT'

    def update_dehum(self):
        if self.dehum_state == 'WAIT':
            if GPIO.input(configuration.dehum_lever_pin) == 1:
                self.app.logic.dehum_force = True
                self.dehum_state = 'UP'
        elif self.dehum_state == 'UP':
            if GPIO.input(configuration.dehum_lever_pin) == 0:
                self.app.logic.dehum_force = False
                self.dehum_state = 'WAIT'

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.update_reset()
            self.update_fan()
            self.update_heater()
            self.update_dehum()
            print time.time()
            time.sleep(0.001)
        print "[-] Stopping buttons manager"
