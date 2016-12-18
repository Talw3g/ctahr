
import os,sys,time
import threading
import RPi.GPIO as GPIO
import configuration
from serial import Serial

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)

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

        self.int_hygro = None
        self.int_temp = None
        self.ext_temp = None
        self.ext_hygro = None

    def update_values(self):
        """ Get latest values of Temp and Hygro """
        int_values = self.app.thermohygro_interior.get()
        ext_values = self.app.thermohygro_exterior.get()
        if int_values != None:
            self.int_hygro, self.int_temp, self.int_time = int_values
        if ext_values != None:
            self.ext_hygro, self.ext_temp, self.ext_time = ext_values

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
        self.states_indice += 1
        if self.states_indice > (len(states) - 1):
            self.states_indice = 0
        self.state = states[self.states_indice]

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
            self.write('MAX TEMP SCREEN')
            self.clear()

        elif self.state == 'HYGRO':
            pass

        elif self.state == 'POWER':
            pass

    def run(self):
        while True:
#            self.clear()
            self.light_state()
            self.update_state()
            time.sleep(1)
