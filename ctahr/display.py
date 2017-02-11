
import os,sys,time
import threading
import RPi.GPIO as GPIO
from serial import Serial
from . import configuration
from . import display_lib as lib

class CtahrDisplay(threading.Thread):
    daemon = True

    def __init__(self, app):
        threading.Thread.__init__(self)
        self.running = True
        print("[+] Starting display manager")

        # Configuring display
        self.serial = Serial(
            configuration.display_serial_device,
            configuration.display_serial_speed)
        # disables autoscroll:
        self.serial.write(bytes.fromhex('fe52'))
        # reset display contrast:
        self.serial.write(bytes.fromhex('fe9164'))
        self.clear()
        # Create waterdrop and thermometer symbols:
        self.serial.write(lib.waterdrop())
        self.serial.write(lib.thermo())

        # Configuring light sensor
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(configuration.light_sensor_pin, GPIO.IN)

        # Initializing variables
        self.app = app
        self.state = 'CURRENT'
        self.states_list = ['CURRENT','TEMP','POWER']
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
            self.int_hygro, self.int_temp, *rest = int_values
        if ext_values[3] != 0:
            self.ext_hygro, self.ext_temp, *rest = ext_values

    def clear(self):
        """ Clear display """
        self.serial.write(bytes.fromhex('fe58'))

    def light_state(self):
        if GPIO.input(configuration.light_sensor_pin) == 1:
            self.serial.write(bytes.fromhex('fe46'))
            self.clear()
        else:
            self.serial.write(bytes.fromhex('fe42\0'))

    def cycle_states(self):
        self.states_indice = ((self.states_indice + 1) % len(self.states_list))
        self.state = self.states_list[self.states_indice]
        self.clear()
        self.t_state = 0

    def update_state(self):
        if self.state == 'CURRENT':
            self.update_values()
            msg = bytes('INT:\n\nEXT:', encoding = 'utf8')
            self.serial.write(bytes.fromhex('fe48'))
            self.serial.write(msg)
            self.serial.write(lib.goto(1,9))
            self.serial.write(chr(1))
            self.serial.write(lib.goto(3,9))
            self.serial.write(chr(1))
            self.serial.write(lib.goto(2,9))
            self.serial.write(chr(0))
            self.serial.write(lib.goto(4,9))
            self.serial.write(chr(0))
            self.serial.write(lib.backwards(1,16,self.int_temp,'T'))
            self.serial.write(lib.backwards(2,16,self.int_hygro,'H'))
            self.serial.write(lib.backwards(3,16,self.ext_temp,'T'))
            self.serial.write(lib.backwards(4,16,self.ext_hygro,'H'))


        elif self.state == 'TEMP':
            msg = ('Int max:\n    min:\n'
                + 'Ext max:\n    min:\n')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)
            self.serial.write(lib.backwards(
                1,16,self.app.stats.int_temp_max, 'T'))
            self.serial.write(lib.backwards(
                2,16,self.app.stats.int_temp_min, 'T'))
            self.serial.write(lib.backwards(
                3,16,self.app.stats.ext_temp_max, 'T'))
            self.serial.write(lib.backwards(
                4,16,self.app.stats.ext_temp_min, 'T'))


        elif self.state == 'POWER':
            msg = (' ENERGY CONSUMPTION\n'
                + 'Fan:\nHeater:\nDehum:')
            self.serial.write('\xfe\x48')
            self.serial.write(msg)
            self.serial.write(lib.backwards(
                2,20,self.app.stats.fan_energy, 'E'))
            self.serial.write(lib.backwards(
                3,20,self.app.stats.heater_energy, 'E'))
            self.serial.write(lib.backwards(
                4,20,self.app.stats.dehum_energy, 'E'))

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
            if (time.monotonic() - self.t_state) > 0.5:
                self.update_state()
                self.t_state = time.monotonic()
            time.sleep(0.1)

        self.clear()
        print("[-] Stopping display manager")
