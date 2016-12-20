
import os,sys,time
import threading
import RPi.GPIO as GPIO
import configuration
from serial import Serial

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.running = True
        print "[+] Starting display manager"

        # Configuring display
        self.serial = Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)
        self.serial.write('\xfe\x52')
        self.clear()

        # Configuring light sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(configuration.light_sensor_pin, GPIO.IN)

        # Initializing variables
        self.app = app
        self.state = 'CURRENT'
        self.states_list = ['CURRENT','TEMP','HYGRO','POWER']
        self.states_indice = 0
        self.t_state = 0
        self.reset_toggle = False

        self.int_hygro = None
        self.int_temp = None
        self.ext_temp = None
        self.ext_hygro = None

    def update_values(self):
        """ Get latest values of Temp and Hygro """
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values[3] != 0:
            self.int_hygro, self.int_temp = int_values[:2]
        if ext_values[3] != 0:
            self.ext_hygro, self.ext_temp = ext_values[:2]

    def clear(self):
        """ Clear display """
        self.serial.write('\xfe\x58')

    def light_state(self):
        if GPIO.input(configuration.light_sensor_pin) == 1:
            self.serial.write('\xfe\x46')
            self.clear()
        else:
            self.serial.write('\xfe\x42\0')

    def cycle_states(self):
        self.states_indice = ((self.states_indice + 1) % len(self.states_list))
        self.state = self.states_list[self.states_indice]
        self.clear()
        self.t_state = 0

    def update_state(self):
        if self.state == 'CURRENT':
            self.update_values()
            msg = ('Interior Temp:' + str(self.int_temp) + '\xb2C\n'
                + 'Exterior Temp:' + str(self.ext_temp) + '\xb2C\n'
                + 'Interior Hygro:' + str(self.int_hygro) + '\x25\n'
                + 'Exterior Hygro:' + str(self.ext_hygro)+ '\x25')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)

        elif self.state == 'TEMP':
            msg = ('Interior MAX: ' + str(self.app.stats.int_temp_max)
                + '\xb2C\n'
                + 'Interior MIN: ' + str(self.app.stats.int_temp_min)
                + '\xb2C\n'
                + 'Exterior MAX: ' + str(self.app.stats.ext_temp_max)
                + '\xb2C\n'
                + 'Exterior MIN: ' + str(self.app.stats.ext_temp_min)
                + '\xb2C')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)

        elif self.state == 'HYGRO':
            msg = ('Interior MAX: ' + str(self.app.stats.int_hygro_max)
                + '\x25\n'
                + 'Interior MIN: ' + str(self.app.stats.int_hygro_min)
                + '\x25\n'
                + 'Exterior MAX: ' + str(self.app.stats.ext_hygro_max)
                + '\x25\n'
                + 'Exterior MIN: ' + str(self.app.stats.ext_hygro_min)
                + '\x25')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)

        elif self.state == 'POWER':
            self.serial.write('\xfe\x48')
            self.serial.write('POWER SCREEN')

        elif self.state == 'RESET':
            self.clear()
            if not self.reset_toggle:
                msg = '\n        RESET'
                self.serial.write('\xfe\x48')
                self.serial.write(msg)
            self.reset_toggle = not self.reset_toggle


    def stop(self):
        self.running = False

    def run(self):
        while self.running:
#            self.clear()
            self.light_state()
            if (time.time() - self.t_state) > 0.5:
                self.update_state()
                self.t_state = time.time()
            time.sleep(0.1)

        self.clear()
        print "[-] Stopping display manager"
