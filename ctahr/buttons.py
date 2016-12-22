
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
        self.fan = False
        self.heater = False
        self.dehum = False

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
            if (time.time() - self.reset_up_time) > 5:
                self.app.stats.reset_global_times()
            elif (time.time() - self.reset_up_time) > 3:
                self.app.stats.reset_hygro_temp()
                self.app.display.state = (
                    self.app.display.states_list[self.app.display.states_indice])
            elif (time.time() - self.reset_up_time) > 1:
                self.app.display.state = 'RESET'

            if GPIO.input(configuration.reset_lever_pin) == 1:
                self.reset_state = 'DOWN'
        elif self.reset_state == 'DOWN':
            if (time.time() - self.reset_up_time) < 0.5:
                self.app.display.cycle_states()
            self.reset_state = 'WAIT'

    def update_fan(self):
        if self.fan_state == 'WAIT':
            if GPIO.input(configuration.fan_lever_pin) == 1:
                self.fan_state = 'UP'
                self.fan = True
        if self.fan_state == 'UP':
            if GPIO.input(configuration.fan_lever_pin) == 0:
                self.fan_state = 'WAIT'
                self.fan = False

    def update_heater(self):
        if self.heater_state == 'WAIT':
            if GPIO.input(configuration.heater_lever_pin) == 1:
                self.heater_state = 'UP'
                self.heater = True
        elif self.heater_state == 'UP':
            if GPIO.input(configuration.heater_lever_pin) == 0:
                self.heater_state = 'WAIT'
                self.heater = False

    def update_dehum(self):
        if self.dehum_state == 'WAIT':
            if GPIO.input(configuration.dehum_lever_pin) == 1:
                self.dehum_state = 'UP'
                self.dehum = True
        elif self.dehum_state == 'UP':
            if GPIO.input(configuration.dehum_lever_pin) == 0:
                self.dehum_state = 'WAIT'
                self.dehum = False

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.update_reset()
            self.update_fan()
            self.update_heater()
            self.update_dehum()
            time.sleep(0.01)
        print "[-] Stopping buttons manager"
