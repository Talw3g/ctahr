
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
        self.states_indice = 0
        self.t_state = 0

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
        states = ['CURRENT','TEMP','HYGRO','POWER']
        self.states_indice = ((self.states_indice + 1) % len(states))
        self.state = states[self.states_indice]
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
            self.clear()
            self.serial.write('MAX TEMP SCREEN')

        elif self.state == 'HYGRO':
            self.clear()
            self.serial.write('MAX HYGRO SCREEN')

        elif self.state == 'POWER':
            self.clear()
            self.serial.write('POWER SCREEN')

    def stop(self):
        self.running = False

    def run(self):
        while self.running:
#            self.clear()
            self.light_state()
            if (time.time() - self.t_state) > 1:
                self.update_state()
                self.t_state = time.time()
            time.sleep(0.1)

        self.clear()
        print "[-] Stopping display manager"
