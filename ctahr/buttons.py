
import time,threading
import configuration
import RPi.GPIO as GPIO

class CtahrButtons(threading.Thread):

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.app = app
        self.lock = threading.Lock()

        print "[+] Starting buttons manager"

        self.reset_state = 'WAIT'
        self.running = True

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(configuration.reset_lever_pin, GPIO.IN)
        GPIO.setup(configuration.fan_lever_pin, GPIO.IN)
        GPIO.setup(configuration.dehum_lever_pin, GPIO.IN)
        GPIO.setup(configuration.heater_lever_pin, GPIO.IN)

    def update_reset(self):
        if self.reset_state == 'WAIT':
            if GPIO.input(configuration.fan_lever_pin) == 1:
                self.reset_state = 'UP'
                self.reset_up_time = time.time()

        elif self.reset_state == 'UP':
            if (time.time() - self.reset_up_time) > 3:
                pass
            elif (time.time() - self.reset_up_time) > 1:
                pass

            if GPIO.input(configuration.fan_lever_pin) == 0:
                self.reset_state = 'DOWN'

        elif self.reset_state == 'DOWN':
            if (time.time() - self.reset_up_time) < 0.5:
                self.app.display.cycle_states()
                print "Cycling states"
            self.reset_state = 'WAIT'

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
            self.update_reset()
            time.sleep(0.01)
        print "[-] Stoping buttons manager"
